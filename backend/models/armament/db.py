"""The ``armaments`` table: parts that spec sheets list."""

from db.base_db import BaseDB
from models.mixins.db import TimestampsDB
from models.mixins.part import PartDB


class ArmamentDB(BaseDB, TimestampsDB, PartDB):
    """A weapon with its own wiki page, such as the 60mm Vulcan Gun.

    One row however many suits carry it, so its page can list
    every sheet that does (ADR 0002).
    """
