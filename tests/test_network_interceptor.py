"""Pruebas unitarias (sin navegador) de la obtención del OTP de Legalario en NetworkInterceptor."""
from services.network_interceptor import NetworkInterceptor


class FakeDriver:
    """Simula lo mínimo de Selenium que usa NetworkInterceptor."""

    def __init__(self, capturadas=None, respuesta_fetch=None, ultima_otp=None):
        self.capturadas = capturadas or []
        self.respuesta_fetch = respuesta_fetch
        self.ultima_otp = ultima_otp
        self.fetch_llamadas = []
        self.guardado = None

    def execute_script(self, script, *args):
        if "__capturedRequests" in script:
            return self.capturadas
        if "return window.__lastLegalarioOtpResponse" in script:
            return self.ultima_otp
        if "window.__lastLegalarioOtpResponse = arguments[0]" in script:
            self.guardado = args[0]
            return None
        raise AssertionError(f"script inesperado: {script}")

    def execute_async_script(self, script, *args):
        self.fetch_llamadas.append(args)
        return self.respuesta_fetch


def _send_code_new():
    return {
        "url": "https://sandbox-api.legalario.com/sdk/invites/send-code-new",
        "headers": {"Authorization": "Bearer x", "Content-Type": "application/json"},
        "body": '{"signer_id":"abc","organization_id":"org","requested_by":"sdk"}',
        "responseText": '{"success":true,"data":{"id":"abc"},"message":"Código único enviado"}',
    }


class TestFormatoOtp:
    def test_entero_se_rellena_a_4_digitos(self):
        assert NetworkInterceptor._formatear_otp_legalario(2947) == "2947"
        assert NetworkInterceptor._formatear_otp_legalario(472) == "0472"
        assert NetworkInterceptor._formatear_otp_legalario("0007") == "0007"

    def test_vacio_es_none(self):
        assert NetworkInterceptor._formatear_otp_legalario(None) is None
        assert NetworkInterceptor._formatear_otp_legalario("") is None


class TestGetLastLegalarioOtpCode:
    def test_sin_respuesta(self):
        assert NetworkInterceptor(FakeDriver()).get_last_legalario_otp_code() is None

    def test_respuesta_sin_otp_code_como_send_code_new(self):
        driver = FakeDriver(ultima_otp={"data": {"id": "abc"}, "message": "Código único enviado"})
        assert NetworkInterceptor(driver).get_last_legalario_otp_code() is None

    def test_respuesta_con_otp_code_entero(self):
        driver = FakeDriver(ultima_otp={"data": {"otp_code": 472}})
        assert NetworkInterceptor(driver).get_last_legalario_otp_code() == "0472"


class TestSolicitarOtpLegalario:
    def test_sin_send_code_capturado_no_pide_nada(self):
        driver = FakeDriver(capturadas=[{"url": "https://sandbox-api.legalario.com/sdk/login"}])
        assert NetworkInterceptor(driver).solicitar_otp_legalario() is None
        assert driver.fetch_llamadas == []

    def test_reenvia_al_endpoint_antiguo_con_mismas_cabeceras_y_cuerpo(self):
        base = _send_code_new()
        driver = FakeDriver(
            capturadas=[base],
            respuesta_fetch={"success": True, "data": {"otp_code": 2947, "otp_status": "active"}},
        )
        assert NetworkInterceptor(driver).solicitar_otp_legalario() == "2947"

        (url, headers, body), = driver.fetch_llamadas
        assert url == "https://sandbox-api.legalario.com/sdk/invites/send-code"
        assert headers == base["headers"] and body == base["body"]
        # deja la respuesta guardada para get_last_legalario_otp_code()
        assert driver.guardado["data"]["otp_code"] == 2947

    def test_usa_el_ultimo_envio_capturado(self):
        viejo = {**_send_code_new(), "body": '{"signer_id":"viejo"}'}
        nuevo = {**_send_code_new(), "body": '{"signer_id":"nuevo"}'}
        driver = FakeDriver(capturadas=[viejo, nuevo], respuesta_fetch={"data": {"otp_code": 1}})
        NetworkInterceptor(driver).solicitar_otp_legalario()
        assert driver.fetch_llamadas[0][2] == '{"signer_id":"nuevo"}'

    def test_error_de_red_o_respuesta_sin_codigo_devuelve_none(self):
        for respuesta in ({"error": "TypeError: Failed to fetch"}, {"data": {}}, "texto"):
            driver = FakeDriver(capturadas=[_send_code_new()], respuesta_fetch=respuesta)
            assert NetworkInterceptor(driver).solicitar_otp_legalario() is None
