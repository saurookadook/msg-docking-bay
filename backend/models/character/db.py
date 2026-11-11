"""The ``characters`` table: people in the Gundam stories."""

from db.base_db import BaseDB
from models.mixins.db import TimestampsDB
from models.mixins.person import PersonDB


class CharacterDB(BaseDB, TimestampsDB, PersonDB):
    """A fictional person, such as Amuro Ray, read from their wiki page.

    One row however many series they appear in: membership lives in
    ``character_appearances``, and the suits they pilot in
    ``mobile_suit_pilots``.
    """
