# Cámara fake para Legalario facematch

## Archivos involucrados

- `conftest.py` — aplica `--use-file-for-fake-video-capture` al iniciar Chrome
- `config/settings.py` — controla `USE_FAKE_CAMERA` y rutas de archivos
- `utils/generate_fake_camera_video.py` — genera `data/selfie.y4m` a partir de `data/selfie.jpeg`

## Prerrequisitos: archivos en `data/`

Coloca los siguientes archivos antes de ejecutar:

| Archivo | Descripción |
|---|---|
| `data/ine_frente.jpeg` | Foto frontal de la INE del cliente |
| `data/ine_tras.jpeg` | Foto trasera de la INE del cliente |
| `data/selfie.jpeg` | Selfie del cliente — debe corresponder con la INE frontal |
| `data/comprobante.jpeg` | Comprobante de domicilio |

## Instalar dependencias

Las dependencias ya están incluidas en `requirements.txt`. Solo ejecuta:

```bash
pip install -r requirements.txt
```

## Generar el video .y4m

```bash
python utils/generate_fake_camera_video.py
```

Esto genera `data/selfie.y4m` a partir de `data/selfie.jpeg`.
El video simula un rostro estático con acercamiento progresivo para activar el paso "acércate" del SDK.

> **Este paso es obligatorio.** Si `data/selfie.y4m` no existe, `conftest.py` lanzará un `FileNotFoundError` y la prueba no arrancará.

## Estado de `USE_FAKE_CAMERA`

`USE_FAKE_CAMERA = True` ya es el valor por defecto en `config/settings.py`.
No es necesario cambiarlo para ejecuciones desatendidas.

Para deshabilitar la cámara fake (p. ej. prueba manual con cámara real), cámbialo a `False` en `config/settings.py`.

## Ejecutar prueba

```bash
python run.py
```

O directamente:

```bash
pytest --alluredir=allure-results
```

## Nota importante

Si Legalario no dispara `facematch`, probablemente el SDK no está detectando el rostro o el acercamiento.
En ese caso hay que regenerar `selfie.y4m` con una selfie frontal más clara, mejor encuadre o ajustando los parámetros de zoom en `utils/generate_fake_camera_video.py`.
