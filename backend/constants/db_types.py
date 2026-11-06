"""Named PostgreSQL enum types for the catalog's StrEnums (SQLA-11)."""

from typing import Final

from sqlalchemy import Enum

from constants.catalog import (
    ContentLicense,
    IngestRunStatus,
    SourceKind,
    WorkRelationType,
    WorkType,
)
from db.base_db import BaseDB, enum_values

WORK_TYPE_DB_TYPE: Final[Enum] = Enum(
    WorkType,
    name="work_type",
    values_callable=enum_values,
    metadata=BaseDB.metadata,
)

WORK_RELATION_TYPE_DB_TYPE: Final[Enum] = Enum(
    WorkRelationType,
    name="work_relation_type",
    values_callable=enum_values,
    metadata=BaseDB.metadata,
)

SOURCE_KIND_DB_TYPE: Final[Enum] = Enum(
    SourceKind,
    name="source_kind",
    values_callable=enum_values,
    metadata=BaseDB.metadata,
)
"""Shared by ``sources.kind`` and ``ingest_runs.source_kind``."""

CONTENT_LICENSE_DB_TYPE: Final[Enum] = Enum(
    ContentLicense,
    name="content_license",
    values_callable=enum_values,
    metadata=BaseDB.metadata,
)

INGEST_RUN_STATUS_DB_TYPE: Final[Enum] = Enum(
    IngestRunStatus,
    name="ingest_run_status",
    values_callable=enum_values,
    metadata=BaseDB.metadata,
)
