import json


class NetworkInterceptor:
    def __init__(self, driver):
        self.driver = driver

    def install_network_interceptor(self):
        script = """
        if (!window.__networkInterceptorInstalled) {
            window.__networkInterceptorInstalled = true;
            window.__capturedRequests = [];
            window.__mockImageContent = null;
            window.__lastSmsOtpResponse = null;
            window.__lastLegalarioOtpResponse = null;

            function getRequestUrl(url) {
                if (typeof url === "string") return url;
                if (url && typeof url.url === "string") return url.url;
                return String(url || "");
            }

            function getLegalarioMockField(url) {
                const requestUrl = getRequestUrl(url);

                if (
                    requestUrl.includes("sdk/onboarding/identify/front") ||
                    requestUrl.includes("sdk/onboarding/identify/reverse")
                ) {
                    return "image_content";
                }

                if (requestUrl.includes("sdk/onboarding/identify/facematch")) {
                    return "selfie";
                }

                return null;
            }

            function isSendConfirmationSms(url) {
                return getRequestUrl(url).includes("/v1/sendconfirmationsms");
            }

            function isLegalarioSendCode(url) {
                return getRequestUrl(url).includes("/sdk/invites/send-code");
            }

            function replaceImageInBody(body, fieldName) {
                try {
                    if (!window.__mockImageContent || !body || !fieldName) return body;

                    if (typeof body === "string") {
                        const parsed = JSON.parse(body);

                        if (Object.prototype.hasOwnProperty.call(parsed, fieldName)) {
                            parsed[fieldName] = window.__mockImageContent;
                            return JSON.stringify(parsed);
                        }

                        return body;
                    }

                    if (
                        typeof body === "object" &&
                        Object.prototype.hasOwnProperty.call(body, fieldName)
                    ) {
                        body[fieldName] = window.__mockImageContent;
                        return body;
                    }

                    return body;
                } catch (e) {
                    return body;
                }
            }

            function captureOtpResponse(requestUrl, response) {
                if (isSendConfirmationSms(requestUrl)) {
                    try {
                        const clonedResponse = response.clone();
                        clonedResponse.json().then((data) => {
                            window.__lastSmsOtpResponse = data;
                        }).catch((e) => {
                            window.__lastSmsOtpResponse = {
                                error: String(e),
                                raw: null
                            };
                        });
                    } catch (e) {
                        window.__lastSmsOtpResponse = {
                            error: String(e),
                            raw: null
                        };
                    }
                }

                if (isLegalarioSendCode(requestUrl)) {
                    try {
                        const clonedResponse = response.clone();
                        clonedResponse.json().then((data) => {
                            window.__lastLegalarioOtpResponse = data;
                        }).catch((e) => {
                            window.__lastLegalarioOtpResponse = {
                                error: String(e),
                                raw: null
                            };
                        });
                    } catch (e) {
                        window.__lastLegalarioOtpResponse = {
                            error: String(e),
                            raw: null
                        };
                    }
                }
            }

            // =========================
            // FETCH
            // =========================
            const originalFetch = window.fetch;

            window.fetch = async function (...args) {
                let [url, options] = args;
                const requestUrl = getRequestUrl(url);
                const legalarioMockField = getLegalarioMockField(requestUrl);

                let headersObj = {};

                try {
                    if (options && options.headers) {
                        if (options.headers instanceof Headers) {
                            options.headers.forEach((value, key) => {
                                headersObj[key] = value;
                            });
                        } else {
                            headersObj = options.headers;
                        }
                    }
                } catch (e) {
                    headersObj = { error: String(e) };
                }

                if (legalarioMockField && options && options.body) {
                    options.body = replaceImageInBody(
                        options.body,
                        legalarioMockField
                    );
                }

                const capturedEntry = {
                    transport: "fetch",
                    url: requestUrl,
                    method: options?.method || "GET",
                    headers: headersObj,
                    body: options?.body || null
                };
                window.__capturedRequests.push(capturedEntry);

                const response = await originalFetch.apply(this, [url, options]);

                capturedEntry.status = response.status;
                try {
                    response.clone().text().then(function(t) {
                        capturedEntry.responseText = t.slice(0, 500);
                    }).catch(function() {});
                } catch (e) {}

                captureOtpResponse(requestUrl, response);

                return response;
            };

            // =========================
            // XHR
            // =========================
            const originalOpen = XMLHttpRequest.prototype.open;
            const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;
            const originalSend = XMLHttpRequest.prototype.send;

            XMLHttpRequest.prototype.open = function(method, url) {
                this.__requestData = {
                    transport: "xhr",
                    method: method,
                    url: getRequestUrl(url),
                    headers: {},
                    body: null
                };

                return originalOpen.apply(this, arguments);
            };

            XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
                if (this.__requestData) {
                    this.__requestData.headers[name] = value;
                }

                return originalSetRequestHeader.apply(this, arguments);
            };

            XMLHttpRequest.prototype.send = function(body) {
                if (this.__requestData) {
                    const legalarioMockField = getLegalarioMockField(
                        this.__requestData.url
                    );

                    if (legalarioMockField) {
                        body = replaceImageInBody(body, legalarioMockField);
                    }

                    this.__requestData.body = body;
                    window.__capturedRequests.push(this.__requestData);

                    const xhrEntry = this.__requestData;
                    this.addEventListener("loadend", function() {
                        xhrEntry.status = this.status;
                        try {
                            xhrEntry.responseText = String(this.responseText).slice(0, 500);
                        } catch (e) {}
                    });

                    if (isSendConfirmationSms(this.__requestData.url)) {
                        this.addEventListener("load", function() {
                            try {
                                window.__lastSmsOtpResponse = JSON.parse(
                                    this.responseText
                                );
                            } catch (e) {
                                window.__lastSmsOtpResponse = {
                                    error: String(e),
                                    raw: this.responseText
                                };
                            }
                        });
                    }

                    if (isLegalarioSendCode(this.__requestData.url)) {
                        this.addEventListener("load", function() {
                            try {
                                window.__lastLegalarioOtpResponse = JSON.parse(
                                    this.responseText
                                );
                            } catch (e) {
                                window.__lastLegalarioOtpResponse = {
                                    error: String(e),
                                    raw: this.responseText
                                };
                            }
                        });
                    }
                }

                return originalSend.call(this, body);
            };
        }
        """
        self.driver.execute_script(script)

    def clear_captured_requests(self):
        self.driver.execute_script("window.__capturedRequests = [];")

    def clear_last_sms_otp_response(self):
        self.driver.execute_script("window.__lastSmsOtpResponse = null;")

    def clear_last_legalario_otp_response(self):
        self.driver.execute_script("window.__lastLegalarioOtpResponse = null;")

    def clear_all_otp_responses(self):
        self.clear_last_sms_otp_response()
        self.clear_last_legalario_otp_response()

    def get_captured_requests(self):
        return self.driver.execute_script(
            "return window.__capturedRequests || [];"
        )

    def get_legalario_requests(self):
        requests = self.get_captured_requests()
        return [
            req for req in requests
            if "legalario.com" in str(req.get("url", "")).lower()
        ]

    def get_legalario_requests_by_endpoint(self, endpoint: str):
        requests = self.get_legalario_requests()
        return [
            req for req in requests
            if endpoint in str(req.get("url", ""))
        ]

    def get_last_sms_otp_response(self):
        return self.driver.execute_script(
            "return window.__lastSmsOtpResponse || null;"
        )

    def get_last_sms_otp_code(self):
        response = self.get_last_sms_otp_response()

        if not response:
            return None

        body = response.get("body", {})
        code = body.get("code")

        return str(code) if code else None

    def get_last_legalario_otp_response(self):
        return self.driver.execute_script(
            "return window.__lastLegalarioOtpResponse || null;"
        )

    def get_last_legalario_otp_code(self):
        response = self.get_last_legalario_otp_response()

        if not response:
            return None

        data = response.get("data", {})
        return self._formatear_otp_legalario(data.get("otp_code"))

    @staticmethod
    def _formatear_otp_legalario(code):
        """El código es de 4 dígitos; la API lo devuelve como entero (se pierden ceros a la izquierda)."""
        if code is None or code == "":
            return None
        texto = str(code)
        return texto.zfill(4) if texto.isdigit() else texto

    def solicitar_otp_legalario(self):
        """
        Desde ~nov-2026 el SDK de Legalario envía el SMS con `/sdk/invites/send-code-new`, cuya
        respuesta ya NO trae `data.otp_code`. El endpoint anterior `/sdk/invites/send-code` sigue
        activo y sí lo devuelve, así que se le pide el código con el mismo firmante y las mismas
        cabeceras de la request real capturada. Genera un código NUEVO (invalida el anterior), por
        eso se llama justo antes de teclearlo. Devuelve el código (str) o None si no se pudo.
        """
        envios = [
            r for r in self.get_captured_requests()
            if "/sdk/invites/send-code" in str(r.get("url", ""))
        ]
        if not envios:
            return None
        base = envios[-1]
        url = str(base["url"]).replace("send-code-new", "send-code")
        resultado = self.driver.execute_async_script(
            "const [url, headers, body, done] = arguments;"
            "fetch(url, {method: 'POST', headers: headers, body: body})"
            ".then(r => r.json().then(j => done(j)))"
            ".catch(e => done({error: String(e)}));",
            url, base.get("headers") or {}, base.get("body"),
        )
        if not isinstance(resultado, dict):
            return None
        self.driver.execute_script(
            "window.__lastLegalarioOtpResponse = arguments[0];", resultado
        )
        return self._formatear_otp_legalario((resultado.get("data") or {}).get("otp_code"))

    def set_mock_image_content(self, data_url: str):
        self.driver.execute_script(
            "window.__mockImageContent = arguments[0];",
            data_url
        )

    def save_to_file(self, requests, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(requests, f, indent=2, ensure_ascii=False)
        return file_path

    def save_all_requests_to_file(self, file_path: str):
        requests = self.get_captured_requests()
        return self.save_to_file(requests, file_path)

    def force_facematch_request(
        self,
        selfie_data_url: str,
        onboarding_id: str,
        auth_token: str = None,
        base_url: str = None,
        front_data_url: str = None,
    ) -> dict:
        """
        Envía directamente el request de facematch a la API de Legalario.
        Si se proporciona auth_token y base_url, los usa directamente.
        De lo contrario, los busca en window.__capturedRequests.
        Retorna dict con {ok, status, body, error}.
        """
        script = """
        const callback       = arguments[arguments.length - 1];
        const selfieDataUrl  = arguments[0];
        const onboardingId   = arguments[1];
        const givenAuthToken = arguments[2];
        const givenBaseUrl   = arguments[3];
        const frontDataUrl   = arguments[4] || selfieDataUrl;

        const base64 = selfieDataUrl.includes(',')
            ? selfieDataUrl.split(',')[1]
            : selfieDataUrl;

        const frontBase64 = frontDataUrl.includes(',')
            ? frontDataUrl.split(',')[1]
            : frontDataUrl;

        const videoDataUrl = 'data:video/mp4;base64,' + base64;

        let authHeader = givenAuthToken || null;
        let baseUrl    = givenBaseUrl   || null;

        if (!authHeader) {
            const prevRequests = (window.__capturedRequests || []).filter(function(r) {
                return r.url && r.url.includes('legalario.com')
                    && r.headers && (r.headers['Authorization'] || r.headers['authorization']);
            });
            if (!prevRequests.length) {
                callback({ ok: false, status: 0, body: null, error: 'No Authorization header found' });
                return;
            }
            const lastReq = prevRequests[prevRequests.length - 1];
            authHeader = lastReq.headers['Authorization'] || lastReq.headers['authorization'];
            if (!baseUrl) {
                const m = lastReq.url.match(/^(https?:\\/\\/[^/]+)/);
                baseUrl = m ? m[1] : 'https://sandbox-api.legalario.com';
            }
        }

        if (!baseUrl) { baseUrl = 'https://sandbox-api.legalario.com'; }
        const endpoint = baseUrl + '/sdk/onboarding/identify/facematch';

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': authHeader
            },
            body: JSON.stringify({
                onboarding_id: onboardingId,
                front: frontDataUrl,
                selfie: base64,
                happy: selfieDataUrl,
                blink: selfieDataUrl,
                video: videoDataUrl
            })
        })
        .then(function(r) {
            return r.json().then(function(body) {
                callback({ ok: r.ok, status: r.status, body: body, error: null });
            }).catch(function() {
                callback({ ok: r.ok, status: r.status, body: null, error: null });
            });
        })
        .catch(function(e) {
            callback({ ok: false, status: 0, body: null, error: String(e) });
        });
        """
        result = self.driver.execute_async_script(
            script, selfie_data_url, onboarding_id, auth_token, base_url, front_data_url
        )
        return result or {}

    def save_legalario_requests_to_file(self, file_path: str):
        requests = self.get_legalario_requests()
        return self.save_to_file(requests, file_path)