"""The ``powerplants`` table: parts that spec sheets list."""

from db.base_db import BaseDB
from models.mixins.db import TimestampsDB
from models.mixins.part import PartDB


class PowerplantDB(BaseDB, TimestampsDB, PartDB):
    """A generator, such as a Minovsky ultracompact fusion reactor.

    One row however many suits use it (ADR 0002).
    """
