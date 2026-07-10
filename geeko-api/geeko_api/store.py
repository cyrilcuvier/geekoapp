from .models import GeekoState

STATE_KEY = "geeko:state"


class GeekoStore:
    def __init__(self, redis_client):
        self._redis = redis_client

    def get(self) -> GeekoState | None:
        raw = self._redis.get(STATE_KEY)
        if raw is None:
            return None
        return GeekoState.model_validate_json(raw)

    def set(self, state: GeekoState) -> None:
        self._redis.set(STATE_KEY, state.model_dump_json())
