# pyright: reportIncompatibleVariableOverride=false
"""The ``MaterialDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction, Sequence

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.material.db import MaterialDB


class MaterialDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MaterialDB],
):
    """Build a material with no wiki page."""

    class Meta:
        model = MaterialDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id: LazyFunction = LazyFunction(uuid7)
    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: Sequence = numbered("Material {n}")
    slug: Sequence = numbered("material-{n}")
