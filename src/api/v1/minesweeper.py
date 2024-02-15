from fastapi import HTTPException, Depends, APIRouter
from src.services.minesweeper import MinesweeperService, get_minesweeper_service
from src.schemas.game import NewGameSchema, TurnSchema

router = APIRouter()


@router.post("/new")
async def new_game(data: NewGameSchema,
                   mine_service: MinesweeperService = Depends(get_minesweeper_service)):
    response = await mine_service.new_game(data)
    print(response)
    return response


@router.post("/turn")
async def turn(data: TurnSchema,
               mine_service: MinesweeperService = Depends(get_minesweeper_service)):
    response = await mine_service.turn(data)
    return response
