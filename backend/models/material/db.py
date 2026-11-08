"""The ``materials`` table: parts that spec sheets list."""

from db.base_db import BaseDB
from models.mixins.db import TimestampsDB
from models.mixins.part import PartDB


class MaterialDB(BaseDB, TimestampsDB, PartDB):
    """An armor or frame material, such as Luna Titanium Alloy.

    One row however many suits use it (ADR 0002).
    """
