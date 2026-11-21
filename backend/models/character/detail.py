"""The character detail entity (PYD-4).

Kept out of ``models.character.entity`` to break an import cycle: the
suit detail names its pilots with ``CharacterRefEntity``, while this
detail lists the suits a character pilots with suit cards.
"""

from pydantic import Field

from models.character.entity import CharacterCardEntity
from models.mobile_suit.entity import PilotedMobileSuitEntity
from models.work.entity import CitedWorkEntity


class CharacterDetailEntity(CharacterCardEntity):
    """A character, with their works and the suits they pilot.

    Both lists are bounded (a character pilots tens of suits, not
    hundreds), so they nest instead of paging.
    """

    # ----- from `character_appearances`
    appearances: list[CitedWorkEntity] = Field(default_factory=list[CitedWorkEntity])
    # ----- from `mobile_suit_pilots`
    piloted_mobile_suits: list[PilotedMobileSuitEntity] = Field(
        default_factory=list[PilotedMobileSuitEntity]
    )
