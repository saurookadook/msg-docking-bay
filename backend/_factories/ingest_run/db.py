# pyright: reportIncompatibleVariableOverride=false
"""The ``IngestRunDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _mocks.temporal import get_mock_utcnow
from constants.catalog import IngestRunStatus, SourceKind
from db.db_session_manager import DBSessionManager
from models.ingest_run.db import IngestRunDB


class IngestRunDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[IngestRunDB],
):
    """Build a Gundam Wiki run that has started and found nothing yet.

    A finished run needs ``status`` and ``finished_at`` together.
    """

    class Meta:
        model = IngestRunDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    error_count = 0
    error_summary = None
    finished_at = None
    pages_seen = 0
    rows_written = 0
    source_kind = SourceKind.FANDOM_PAGE
    started_at = LazyFunction(get_mock_utcnow)
    status = IngestRunStatus.RUNNING
    watermark_at = None
