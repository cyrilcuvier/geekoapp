from pydantic import BaseModel


class GeekoState(BaseModel):
    x: int
    y: int
    color: str
    mood: str
    step: int
