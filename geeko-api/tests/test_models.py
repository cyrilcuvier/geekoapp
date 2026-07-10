from geeko_api.models import GeekoState


def test_geeko_state_round_trips_through_json():
    state = GeekoState(x=10, y=20, color="#4CAF50", mood="zen", step=3)
    raw = state.model_dump_json()
    restored = GeekoState.model_validate_json(raw)
    assert restored == state
