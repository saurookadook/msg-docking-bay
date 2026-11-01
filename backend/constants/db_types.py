"""Named PostgreSQL enum types for the catalog's StrEnums (SQLA-11)."""

from typing import Final

from sqlalchemy import Enum

from constants.catalog import WorkRelationType, WorkType
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
