"""
Genera data/selfie.y4m para usarlo como cámara fake en Chrome.

Requisitos:
    pip install pillow numpy
    (opencv-python es opcional, se usa solo para resize si está disponible)

Uso:
    python utils/generate_fake_camera_video.py

Entrada esperada:
    data/selfie.jpeg

Salida:
    data/selfie.y4m

    python utils/generate_fake_camera_video.py [ruta_salida.y4m]

El video simula (siempre con la cara CENTRADA, ubicada con Haar cascade):
    - 0-4s   : cara pequeña (SDK detecta rostro)
    - 4-12s  : acercamiento progresivo hasta llenar el óvalo ("acércate")
    - 12-30s : cara fija y centrada dentro del óvalo ("mantén esta posición")

Nota: El archivo .y4m se construye manualmente frame a frame en formato
YUV4MPEG2 I420, que es el único subformato compatible con Chrome en Windows.
"""

from pathlib import Path

import math
import sys

import cv2
import numpy as np
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_IMAGE = PROJECT_ROOT / "data" / "selfie.jpeg"
OUTPUT_VIDEO = PROJECT_ROOT / "data" / "selfie.y4m"

# Alto de la cara como fracción del alto del frame
FRACTION_START = 0.50
FRACTION_HOLD = 0.68


def load_image_rgb(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"No existe la imagen base: {path}")
    return np.array(Image.open(path).convert("RGB"))


def resize_cover(image: np.ndarray, width: int, height: int) -> np.ndarray:
    src_h, src_w = image.shape[:2]
    scale = max(width / src_w, height / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)

    pil = Image.fromarray(image).resize((new_w, new_h), Image.LANCZOS)
    arr = np.array(pil)

    x = max((new_w - width) // 2, 0)
    y = max((new_h - height) // 2, 0)
    return arr[y:y + height, x:x + width]


# Fallback (px sobre data/selfie.jpeg 1200x1600) si no se detecta la cara
FALLBACK_FACE = (555.0, 620.0, 640.0)  # centro_x, centro_y, alto (frente-barbilla)


def detect_face(image: np.ndarray):
    """Devuelve (cx, cy, alto_cara) de la cara más grande, o el fallback."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(150, 150))
    if len(faces) == 0:
        print("Aviso: no se detectó cara, usando coordenadas de respaldo")
        return FALLBACK_FACE
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    # El cuadro de Haar va de cejas a barbilla; se amplía a frente-barbilla
    return (x + w / 2.0, y + h / 2.0, h * 1.15)


def face_frame(
    image: np.ndarray,
    width: int,
    height: int,
    face: tuple,
    face_fraction: float,
    dx: float = 0.0,
    dy: float = 0.0,
) -> np.ndarray:
    """
    Encuadra la cara centrada en un frame width x height, de modo que su alto
    ocupe `face_fraction` del alto del frame. Si la ventana excede la imagen
    fuente, se refleja el borde (no hay bandas negras ni deformación).
    dx/dy: desplazamiento en fracción del frame (micro-movimiento).
    """
    cx, cy, face_h = face
    scale = (height * face_fraction) / face_h  # px de frame por px de fuente
    # Punto de la fuente que va al centro del frame (+ desplazamiento)
    src_cx = cx - dx * width / scale
    src_cy = cy - dy * height / scale
    matrix = np.float32([
        [scale, 0, width / 2.0 - src_cx * scale],
        [0, scale, height / 2.0 - src_cy * scale],
    ])
    return cv2.warpAffine(
        image, matrix, (width, height),
        flags=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )


def rgb_to_i420(frame_rgb: np.ndarray, width: int, height: int) -> bytes:
    """
    Convierte un frame RGB a YUV I420 exactamente width x height píxeles.
    BT.601 studio swing. El frame de salida es siempre width*height*3//2 bytes.
    """
    # width y height DEBEN ser pares (640x480 lo son)
    assert width % 2 == 0 and height % 2 == 0, "width y height deben ser pares"

    # Forzar dimensión exacta recortando o rellenando con PIL
    pil = Image.fromarray(frame_rgb.astype(np.uint8)).resize((width, height), Image.LANCZOS)
    f = np.array(pil, dtype=np.float32)
    R, G, B = f[:, :, 0], f[:, :, 1], f[:, :, 2]

    # BT.601 studio swing: Y en [16,235], Cb/Cr en [16,240]
    Y  = ( 0.2568 * R + 0.5041 * G + 0.0979 * B +  16).clip(16, 235).round().astype(np.uint8)
    Cb = (-0.1482 * R - 0.2910 * G + 0.4392 * B + 128).clip(16, 240).round().astype(np.uint8)
    Cr = ( 0.4392 * R - 0.3678 * G - 0.0714 * B + 128).clip(16, 240).round().astype(np.uint8)

    # Submuestreo 4:2:0 por promedio de bloques 2x2
    # Y tiene shape (height, width) exacto — sin necesidad de recortar
    Cb_f = Cb.astype(np.float32)
    Cr_f = Cr.astype(np.float32)
    Cb_down = ((Cb_f[0::2, 0::2] + Cb_f[1::2, 0::2] +
                Cb_f[0::2, 1::2] + Cb_f[1::2, 1::2]) / 4).astype(np.uint8)
    Cr_down = ((Cr_f[0::2, 0::2] + Cr_f[1::2, 0::2] +
                Cr_f[0::2, 1::2] + Cr_f[1::2, 1::2]) / 4).astype(np.uint8)

    # Tamaño esperado: width*height + 2*(width//2)*(height//2) = width*height*3//2
    assert Y.nbytes == width * height
    assert Cb_down.nbytes == (width // 2) * (height // 2)
    assert Cr_down.nbytes == (width // 2) * (height // 2)

    return Y.tobytes() + Cb_down.tobytes() + Cr_down.tobytes()


def main(output: Path = OUTPUT_VIDEO):
    OUTPUT_VIDEO = output
    OUTPUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    width = 320
    height = 240
    fps = 10
    duration_seconds = 30
    total_frames = fps * duration_seconds

    source_image = load_image_rgb(INPUT_IMAGE)
    face = detect_face(source_image)
    print(f"Cara: centro=({face[0]:.0f},{face[1]:.0f}) alto={face[2]:.0f}px")

    with open(OUTPUT_VIDEO, "wb") as f:
        # Cabecera YUV4MPEG2
        header = f"YUV4MPEG2 W{width} H{height} F{fps}:1 Ip A0:0 C420\n"
        f.write(header.encode("ascii"))

        for index in range(total_frames):
            t = index / fps

            # Fase 1 (0-4s): cara pequeña centrada — el SDK detecta el rostro
            # Fase 2 (4-12s): acercamiento progresivo hasta llenar el óvalo
            # Fase 3 (12-30s): cara fija y centrada ("mantén esta posición")
            if t < 4.0:
                fraction = FRACTION_START
            elif t < 12.0:
                prog = (t - 4.0) / 8.0
                fraction = FRACTION_START + prog * (FRACTION_HOLD - FRACTION_START)
            else:
                fraction = FRACTION_HOLD

            # Micro movimiento leve (la cara nunca sale del óvalo). En la fase
            # de mantener posición es aún menor para no romper la validación.
            amp = 0.006 if t >= 12.0 else 0.012
            dx = amp * math.sin(2 * math.pi * t / 3.0)
            dy = amp * math.sin(2 * math.pi * t / 4.0)

            frame = face_frame(source_image, width, height, face, fraction, dx, dy)

            i420_data = rgb_to_i420(frame, width, height)

            f.write(b"FRAME\n")
            f.write(i420_data)

    if not OUTPUT_VIDEO.exists() or OUTPUT_VIDEO.stat().st_size == 0:
        raise RuntimeError(f"No se generó correctamente: {OUTPUT_VIDEO}")

    print(f"Video fake camera generado: {OUTPUT_VIDEO}")
    print(f"  Resolución : {width}x{height}")
    print(f"  FPS        : {fps}")
    print(f"  Duración   : {duration_seconds}s ({total_frames} frames)")
    print(f"  Tamaño     : {OUTPUT_VIDEO.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUTPUT_VIDEO)
