import json
from services.image_encoder import ImageEncoder


class LegalarioUploader:
    ENDPOINT_FRONT = "https://sandbox-api.legalario.com/sdk/onboarding/identify/front"

    def __init__(self, driver):
        self.driver = driver

    def load_real_payload(self, file_path: str) -> dict:
        """
        Lee el front_request.json guardado por el interceptor y convierte
        el campo 'body' stringificado a dict real.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_body = data.get("body")
        if not raw_body:
            raise ValueError("El archivo front_request.json no contiene 'body'")

        if isinstance(raw_body, dict):
            return raw_body

        return json.loads(raw_body)

    def replace_image(self, payload: dict, image_path: str) -> dict:
        """
        Reemplaza únicamente la imagen por la local, manteniendo el resto
        del payload real capturado.
        """
        updated_payload = payload.copy()
        updated_payload["image_content"] = ImageEncoder.image_to_data_url(image_path)
        return updated_payload

    def upload_using_real_request(
        self,
        front_request_file: str,
        image_path: str,
        authorization_header: str
    ) -> dict:
        """
        Reutiliza el body real del SDK y solo reemplaza image_content.
        """
        payload = self.load_real_payload(front_request_file)
        payload = self.replace_image(payload, image_path)

        script = """
        const endpoint = arguments[0];
        const payload = arguments[1];
        const authorizationHeader = arguments[2];
        const callback = arguments[arguments.length - 1];

        fetch(endpoint, {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": authorizationHeader
            },
            body: JSON.stringify(payload)
        })
        .then(async response => {
            const text = await response.text();
            callback({
                ok: response.ok,
                status: response.status,
                body: text
            });
        })
        .catch(error => {
            callback({
                ok: false,
                status: 0,
                body: error.toString()
            });
        });
        """

        return self.driver.execute_async_script(
            script,
            self.ENDPOINT_FRONT,
            payload,
            authorization_header
        )