"""The ``equipment`` table: parts that spec sheets list."""

from typing import override

from sqlalchemy.orm import declared_attr

from db.base_db import BaseDB
from models.mixins.db import TimestampsDB
from models.mixins.part import PartDB


class EquipmentDB(BaseDB, TimestampsDB, PartDB):
    """Equipment with its own wiki page, such as the Core Block System.

    One row however many suits carry it (ADR 0002).
    """

    @declared_attr.directive
    @classmethod
    @override
    def __tablename__(cls) -> str:
        """Use the mass noun: the derived ``equipments`` is wrong."""
        return "equipment"
