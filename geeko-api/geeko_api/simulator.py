import random

from .models import GeekoState

COLORS = ["#4CAF50", "#8BC34A", "#FFC107", "#FF5722", "#9C27B0", "#00BCD4"]
MOODS = ["happy", "sleepy", "grumpy", "excited", "zen"]
BOUNDS = 100
_STEP_CHOICES = [-5, -2, 0, 2, 5]


def initial_state() -> GeekoState:
    return GeekoState(x=50, y=50, color=COLORS[0], mood="zen", step=0)


def next_state(state: GeekoState, rng: random.Random | None = None) -> GeekoState:
    rng = rng or random.Random()
    new_x = max(0, min(BOUNDS, state.x + rng.choice(_STEP_CHOICES)))
    new_y = max(0, min(BOUNDS, state.y + rng.choice(_STEP_CHOICES)))
    new_color = rng.choice(COLORS) if rng.random() < 0.2 else state.color
    new_mood = rng.choice(MOODS) if rng.random() < 0.15 else state.mood
    return GeekoState(x=new_x, y=new_y, color=new_color, mood=new_mood, step=state.step + 1)
