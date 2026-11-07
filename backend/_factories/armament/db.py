# pyright: reportIncompatibleVariableOverride=false
"""The ``ArmamentDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.armament.db import ArmamentDB


class ArmamentDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[ArmamentDB],
):
    """Build a weapon with no wiki page."""

    class Meta:
        model = ArmamentDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    fandom_page_title = None
    name = numbered("Armament {n}")
    slug = numbered("armament-{n}")
