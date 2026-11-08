# pyright: reportIncompatibleVariableOverride=false
"""The ``PowerplantDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.powerplant.db import PowerplantDB


class PowerplantDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[PowerplantDB],
):
    """Build a powerplant with no wiki page."""

    class Meta:
        model = PowerplantDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    fandom_page_title = None
    name = numbered("Powerplant {n}")
    slug = numbered("powerplant-{n}")
