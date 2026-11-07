# pyright: reportIncompatibleVariableOverride=false
"""The ``EquipmentDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

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
    """Build a item with no wiki page."""

    class Meta:
        model = EquipmentDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    fandom_page_title = None
    name = numbered("Equipment {n}")
    slug = numbered("equipment-{n}")
