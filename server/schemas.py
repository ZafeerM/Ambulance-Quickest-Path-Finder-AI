from pydantic import BaseModel, field_validator
from typing import List, Dict, Any


class GridPayload(BaseModel):
    """Payload sent by the frontend over the WebSocket."""

    grid: List[List[int]]
    rows: int
    cols: int
    algorithm: str
    params: Dict[str, Any] = {}

    @field_validator("grid")
    @classmethod
    def grid_must_not_be_empty(cls, v: List[List[int]]) -> List[List[int]]:
        if not v or not v[0]:
            raise ValueError("grid must not be empty")
        return v

    @field_validator("rows")
    @classmethod
    def rows_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("rows must be a positive integer")
        return v

    @field_validator("cols")
    @classmethod
    def cols_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("cols must be a positive integer")
        return v


class WSMessage(BaseModel):
    """Shape of every message sent back to the frontend over the WebSocket."""

    type: str   # "info" | "step" | "done" | "error"
    grid: List[List[int]]
    message: str
