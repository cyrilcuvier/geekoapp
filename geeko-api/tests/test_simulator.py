import random

from geeko_api.simulator import BOUNDS, initial_state, next_state


def test_initial_state_is_centered_and_step_zero():
    state = initial_state()
    assert state.x == 50
    assert state.y == 50
    assert state.step == 0


def test_next_state_increments_step():
    state = initial_state()
    new_state = next_state(state, rng=random.Random(1))
    assert new_state.step == state.step + 1


def test_next_state_never_leaves_bounds():
    state = initial_state()
    rng = random.Random(42)
    # Push the state around a lot of times; position must always stay in [0, BOUNDS]
    for _ in range(500):
        state = next_state(state, rng=rng)
        assert 0 <= state.x <= BOUNDS
        assert 0 <= state.y <= BOUNDS


def test_next_state_is_deterministic_given_seeded_rng():
    state = initial_state()
    a = next_state(state, rng=random.Random(7))
    b = next_state(state, rng=random.Random(7))
    assert a == b
