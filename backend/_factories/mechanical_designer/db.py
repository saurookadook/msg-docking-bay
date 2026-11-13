# pyright: reportIncompatibleVariableOverride=false
"""The ``MechanicalDesignerDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.mechanical_designer.db import MechanicalDesignerDB


class MechanicalDesignerDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MechanicalDesignerDB],
):
    """Build a designer with no wiki page or Japanese name."""

    class Meta:
        model = MechanicalDesignerDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    fandom_page_title = None
    name = numbered("Mechanical Designer {n}")
    name_ja = None
    slug = numbered("mechanical-designer-{n}")
