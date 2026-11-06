# pyright: reportIncompatibleVariableOverride=false
"""The ``ContinuityDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.continuity.db import ContinuityDB


class ContinuityDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[ContinuityDB],
):
    """Build a root continuity; set ``parent_continuity_id`` to nest."""

    class Meta:
        model = ContinuityDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    name = numbered("Continuity {n}")
    parent_continuity_id = None
    slug = numbered("continuity-{n}")
