from fastapi import APIRouter
from app.repositories.character_repository import CharacterRepository

router = APIRouter(prefix="/api/characters", tags=["Characters"])

character_repository = CharacterRepository()


@router.get("")
async def list_characters():
    characters = character_repository.list_all()
    return {
        "characters": [
            {
                "id": c.id,
                "name": c.name,
                "has_voice": c.has_voice,
            }
            for c in characters
        ]
    }