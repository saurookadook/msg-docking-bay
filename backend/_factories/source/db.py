# pyright: reportIncompatibleVariableOverride=false
"""The ``SourceDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from _mocks.temporal import get_mock_utcnow
from constants.catalog import ContentLicense, SourceKind
from db.db_session_manager import DBSessionManager
from models.source.db import SourceDB


class SourceDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[SourceDB],
):
    """Build a Gundam Wiki page loaded from a dump with no revision."""

    class Meta:
        model = SourceDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    content_license = ContentLicense.CC_BY_SA_3_0
    external_id = numbered("{n}")
    kind = SourceKind.FANDOM_PAGE
    retrieved_at = LazyFunction(get_mock_utcnow)
    revision_id = None
    url = numbered("https://gundam.fandom.com/?curid={n}")
