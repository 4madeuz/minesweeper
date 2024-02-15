import random
import uuid
from collections import deque
from fastapi import status, HTTPException, Depends
from typing import Dict
from src.schemas.game import NewGameSchema, TurnSchema


active_games = {}


class MinesweeperGame:
    def __init__(self, data: NewGameSchema):
        self.game_id = str(uuid.uuid4())
        self.width = data.width
        self.height = data.height
        self.mines_count = data.mines_count
        self.field = [[" " for _ in range(data.width)] for _ in range(data.height)]
        self.completed = False
        self.remaining_cells = self.width * self.height
        self.opened_cells = 0
        self.generate_mines()

    def generate_mines(self):
        mines_generated = 0
        while mines_generated < self.mines_count:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            if self.field[row][col] != "M":
                self.field[row][col] = "M"
                mines_generated += 1

    def count_adjacent_mines(self, row: int, col: int) -> int:
        count = 0
        for i in range(max(0, row - 1), min(self.height, row + 2)):
            for j in range(max(0, col - 1), min(self.width, col + 2)):
                if self.field[i][j] == "M":
                    count += 1
        return count

    def reveal_all_cells(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.field[row][col] == "M":
                    self.field[row][col] = "X"
                else:
                    self.field[row][col] = str(self.count_adjacent_mines(row, col))

    def is_game_won(self):
        return self.opened_cells + self.mines_count == self.width * self.height

    def decrement_remaining_cells(self):
        self.remaining_cells -= 1

    def increment_opened_cells(self):
        self.opened_cells += 1

    def open_cell(self, row: int, col: int):
        stack = deque([(row, col)])

        while stack:
            current_row, current_col = stack.pop()

            if 0 <= current_row < self.height and 0 <= current_col < self.width and self.field[current_row][current_col] == " ":
                mines_nearby = self.count_adjacent_mines(current_row, current_col)
                self.field[current_row][current_col] = str(mines_nearby)
                self.increment_opened_cells()

                if mines_nearby == 0:
                    for i in range(max(0, current_row - 1), min(self.height, current_row + 2)):
                        for j in range(max(0, current_col - 1), min(self.width, current_col + 2)):
                            stack.append((i, j))

    def open_empty_cells(self, row: int, col: int):
        if 0 <= row < self.height and 0 <= col < self.width and self.field[row][col] == " ":
            self.open_cell(row, col)


class MinesweeperService:
    def __init__(self, active_games: Dict) -> None:
        self.active_games = active_games

    async def _format_game_response(self, game: MinesweeperGame):
        response = {
            "game_id": game.game_id,
            "width": game.width,
            "height": game.height,
            "mines_count": game.mines_count,
            "field": [[" " if cell == "M" and not game.completed else cell for cell in row] for row in game.field],
            "completed": game.completed
        }
        return response

    async def new_game(self, data: NewGameSchema):
        if data.width > 30 or data.height > 30 or data.mines_count > data.width * data.height - 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parameters")
        game = MinesweeperGame(data)
        self.active_games[game.game_id] = game
        return await self._format_game_response(game)

    async def turn(self, data: TurnSchema):
        print(self.active_games)
        game = self.active_games.get(str(data.game_id))

        if not game:
            raise HTTPException(status_code=400, detail="Game not found")

        if game.completed:
            raise HTTPException(status_code=400, detail="Game already completed")

        if game.field[data.row][data.col] == "M":
            game.completed = True
            game.reveal_all_cells()
            return game.__dict__

        if game.field[data.row][data.col] == " ":
            game.open_empty_cells(data.row, data.col)
        else:
            game.field[data.row][data.col] = str(game.count_adjacent_mines(data.row, data.col))

        if game.is_game_won():
            game.completed = True

        return await self._format_game_response(game)


def get_active_games() -> Dict[str, MinesweeperGame]:
    return active_games


def get_minesweeper_service(active_games: Dict = Depends(get_active_games)) -> MinesweeperService:
    return MinesweeperService(active_games=active_games)
