import httpx


class SageUnavailable(Exception):
    pass


class SageClient:
    def __init__(self, base_url: str, timeout: float = 1.5, transport: httpx.BaseTransport | None = None):
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout, transport=transport)

    def fetch_fortune(self) -> dict:
        try:
            response = self._client.get(f"{self._base_url}/fortune")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise SageUnavailable(str(exc)) from exc
