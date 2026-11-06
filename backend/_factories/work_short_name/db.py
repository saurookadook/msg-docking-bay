# pyright: reportIncompatibleVariableOverride=false
"""The ``WorkShortNameDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.work_short_name.db import WorkShortNameDB


class WorkShortNameDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[WorkShortNameDB],
):
    """Build a short name; pass ``work_id`` from an existing work."""

    class Meta:
        model = WorkShortNameDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    short_name = numbered("W{n}")
    work_id = None  # a real foreign key: pass an existing work's id
