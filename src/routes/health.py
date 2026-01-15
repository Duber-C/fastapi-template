from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix='/health', tags=['Account'])

class Health(BaseModel):
    message: str


@router.get("/")
def health() -> Health:
    return Health(message="ok")
