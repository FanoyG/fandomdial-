import json
from pathlib import Path

from app.models.character import Character


class CharacterNotFoundError(Exception):
    pass


class CharacterRepository:
    """
    Loads character configs from characters.json.
    SRP: this class's only job is loading + looking up characters.
    Later this can become a DB-backed repository with the exact
    same public methods — nothing above it (ChatService, routers)
    would need to change.
    """

    def __init__(self, json_path: str = "characters.json"):
        self._path = Path(json_path)
        self._characters: dict[str, Character] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"characters.json not found at {self._path}")

        with open(self._path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        for entry in raw:
            character = Character(
                id=entry["id"],
                name=entry["name"],
                system_prompt=entry["system_prompt"],
                voice_id=entry.get("voice_id") or None,
                comedic_mechanism=entry.get("comedic_mechanism", ""),
            )
            self._characters[character.id] = character

    def get(self, character_id: str) -> Character:
        character = self._characters.get(character_id)
        if character is None:
            raise CharacterNotFoundError(f"No character with id '{character_id}'")
        return character

    def list_all(self) -> list[Character]:
        return list(self._characters.values())
