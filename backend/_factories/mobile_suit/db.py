# pyright: reportIncompatibleVariableOverride=false
"""The ``MobileSuitDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from constants.catalog import UnitType
from db.db_session_manager import DBSessionManager
from models.mobile_suit.db import MobileSuitDB


class MobileSuitDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MobileSuitDB],
):
    """Build a suit with no timeline, model number, or page ID."""

    class Meta:
        model = MobileSuitDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    continuity_id = None  # a real foreign key: pass an existing continuity's id
    fandom_page_id = None
    model_number = None
    name = numbered("Mobile Suit {n}")
    name_ja = None
    slug = numbered("mobile-suit-{n}")
    unit_type = UnitType.SUIT
