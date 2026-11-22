# pyright: reportIncompatibleVariableOverride=false
"""The ``EquipmentDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction, Sequence

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.equipment.db import EquipmentDB


class EquipmentDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[EquipmentDB],
):
    """Build an item with no wiki page."""

    class Meta:
        model = EquipmentDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id: LazyFunction = LazyFunction(uuid7)
    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: Sequence = numbered("Equipment {n}")
    slug: Sequence = numbered("equipment-{n}")
