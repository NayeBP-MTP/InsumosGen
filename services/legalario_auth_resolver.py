import json


class LegalarioAuthResolver:
    def __init__(self, driver=None):
        self.driver = driver

    def get_authorization_from_captured_requests(self, captured_requests):
        for req in captured_requests:
            url = str(req.get("url", ""))
            headers = req.get("headers", {})

            if "legalario.com" in url.lower():
                if isinstance(headers, dict):
                    for key, value in headers.items():
                        if str(key).lower() == "authorization":
                            return value

        return None

    def find_front_request(self, captured_requests):
        for req in captured_requests:
            url = str(req.get("url", ""))
            if "sdk/onboarding/identify/front" in url:
                return req
        return None

    def save_front_request_to_file(self, captured_requests, file_path: str):
        front_request = self.find_front_request(captured_requests)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(front_request, f, indent=2, ensure_ascii=False)
        return file_path