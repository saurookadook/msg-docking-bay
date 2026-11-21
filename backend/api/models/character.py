"""Response models for characters (FAPI-12)."""

from api.models.base import BaseResponseModel
from api.models.pagination import PageMeta
from models.character.detail import CharacterDetailEntity
from models.character.entity import CharacterCardEntity


class CharactersListResponse(BaseResponseModel):
    """One page of characters."""

    data: list[CharacterCardEntity]
    meta: PageMeta


class CharacterResponse(BaseResponseModel):
    """One character, with their works and the suits they pilot."""

    data: CharacterDetailEntity
