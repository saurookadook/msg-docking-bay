"""The ``mechanical_designers`` table: the people who design suits."""

from db.base_db import BaseDB
from models.mixins.db import TimestampsDB
from models.mixins.person import PersonDB


class MechanicalDesignerDB(BaseDB, TimestampsDB, PersonDB):
    """A real person, such as Kunio Okawara, who designs mobile suits.

    Kept apart from ``characters``, which are fictional. The suits they
    designed are listed in ``mobile_suit_designers``.
    """
