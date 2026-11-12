"""
Cliente base de comunicación HTTP con la API REST de Hotel KeyFlow.
Centraliza sesión, headers de autenticación JWT y manejo uniforme de errores.
"""
import requests


class ErrorAPI(Exception):
    """Excepción base para errores de comunicación con la API."""
    def __init__(self, mensaje: str, status_code: int = None, detalle: dict = None):
        super().__init__(mensaje)
        self.status_code = status_code
        self.detalle = detalle or {}


class ClienteAPIBase:
    def __init__(self, token: str = None, url_base: str = "http://127.0.0.1:8000"):
        self.url_base = url_base.rstrip("/")
        self.session = requests.Session()
        self.token = token
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def actualizar_token(self, token: str):
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get(self, endpoint: str, params: dict = None, timeout: int = 10) -> requests.Response:
        url = f"{self.url_base}/{endpoint.lstrip('/')}"
        return self.session.get(url, params=params, timeout=timeout)

    def post(self, endpoint: str, json: dict = None, data: dict = None, timeout: int = 10) -> requests.Response:
        url = f"{self.url_base}/{endpoint.lstrip('/')}"
        return self.session.post(url, json=json, data=data, timeout=timeout)

    def put(self, endpoint: str, json: dict = None, data: dict = None, timeout: int = 10) -> requests.Response:
        url = f"{self.url_base}/{endpoint.lstrip('/')}"
        return self.session.put(url, json=json, data=data, timeout=timeout)

    def delete(self, endpoint: str, params: dict = None, timeout: int = 10) -> requests.Response:
        url = f"{self.url_base}/{endpoint.lstrip('/')}"
        return self.session.delete(url, params=params, timeout=timeout)

    @staticmethod
    def extraer_detalle(response: requests.Response) -> str:
        """Extrae el mensaje legible de error de una respuesta HTTP."""
        try:
            body = response.json()
            if isinstance(body, dict):
                detail = body.get("detail", "")
                if isinstance(detail, str):
                    return detail
                if isinstance(detail, list) and detail:
                    first = detail[0]
                    if isinstance(first, dict):
                        return first.get("msg", str(first))
            return response.text
        except Exception:
            return response.text or f"Error HTTP {response.status_code}"
