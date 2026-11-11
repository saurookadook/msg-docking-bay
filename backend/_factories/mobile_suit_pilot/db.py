# pyright: reportIncompatibleVariableOverride=false
"""The ``MobileSuitPilotDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.mobile_suit_pilot.db import MobileSuitPilotDB


class MobileSuitPilotDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MobileSuitPilotDB],
):
    """Build a pilot link with no work."""

    class Meta:
        model = MobileSuitPilotDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    character_id = None  # a real foreign key: pass an existing character's id
    mobile_suit_id = None  # a real foreign key: pass an existing suit's id
    source_id = None  # a real foreign key: pass an existing source's id
    work_id = None
