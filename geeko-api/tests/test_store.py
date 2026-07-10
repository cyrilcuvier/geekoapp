import fakeredis

from geeko_api.models import GeekoState
from geeko_api.store import GeekoStore


def make_store() -> GeekoStore:
    return GeekoStore(fakeredis.FakeRedis())


def test_get_returns_none_when_nothing_stored():
    store = make_store()
    assert store.get() is None


def test_set_then_get_round_trips():
    store = make_store()
    state = GeekoState(x=1, y=2, color="#000", mood="happy", step=5)
    store.set(state)
    assert store.get() == state


def test_set_overwrites_previous_state():
    store = make_store()
    store.set(GeekoState(x=1, y=1, color="#000", mood="happy", step=1))
    store.set(GeekoState(x=2, y=2, color="#111", mood="grumpy", step=2))
    assert store.get().step == 2
