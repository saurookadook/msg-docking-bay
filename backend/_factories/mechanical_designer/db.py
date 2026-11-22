# pyright: reportIncompatibleVariableOverride=false
"""The ``MechanicalDesignerDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction, Sequence

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

    id: LazyFunction = LazyFunction(uuid7)
    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: Sequence = numbered("Mechanical Designer {n}")
    name_ja: str | None = None
    slug: Sequence = numbered("mechanical-designer-{n}")
