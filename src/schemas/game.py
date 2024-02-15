from uuid import UUID
from pydantic import BaseModel


class NewGameSchema(BaseModel):
    width: int
    height: int
    mines_count: int


class TurnSchema(BaseModel):
    game_id: UUID
    row: int
    col: int
