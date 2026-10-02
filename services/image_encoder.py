import base64
import os


class ImageEncoder:
    @staticmethod
    def image_to_base64(image_path: str) -> str:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"No existe la imagen: {image_path}")

        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    @staticmethod
    def image_to_data_url(image_path: str, mime_type: str = "image/jpeg") -> str:
        base64_image = ImageEncoder.image_to_base64(image_path)
        return f"data:{mime_type};base64,{base64_image}"