"""The declarative base every model inherits from (SQLA-2, SQLA-5)."""

import enum
import re
import uuid
from datetime import datetime
from typing import Any, ClassVar, Final

from sqlalchemy import Enum, MetaData, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

NAMING_CONVENTION: Final[dict[str, str]] = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

_CAMEL_BOUNDARY: Final = re.compile(r"(?<!^)(?=[A-Z])")


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    """Persist each member's value ("in_progress"), not its name."""
    return [str(member.value) for member in enum_cls]


def table_name_for(class_name: str) -> str:
    """Derive a table name: snake_case, without ``_db``, pluralized.

    ``ProjectDB`` becomes ``projects`` and ``PropertyDB``
    ``properties``. Override ``__tablename__`` on the model, with a
    comment, where this plural is wrong (SQLA-2).
    """
    singular = _CAMEL_BOUNDARY.sub("_", class_name.removesuffix("DB")).lower()
    if singular.endswith("y") and singular[-2:-1] not in ("a", "e", "i", "o", "u"):
        return f"{singular[:-1]}ies"
    if singular.endswith(("s", "x", "z", "ch", "sh")):
        return f"{singular}es"
    return f"{singular}s"


class BaseDB(DeclarativeBase):
    """Give every model a UUIDv7 key, a table name, and the type map."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map: ClassVar[dict[Any, Any]] = {
        datetime: postgresql.TIMESTAMP(timezone=True),
        dict[str, Any]: postgresql.JSONB,
        enum.Enum: Enum(enum.Enum, values_callable=enum_values),
        float: postgresql.DOUBLE_PRECISION,
        list[str]: postgresql.ARRAY(postgresql.TEXT),
        str: postgresql.TEXT,
    }

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=func.uuidv7()
    )

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Name the table after the model class."""
        return table_name_for(cls.__name__)
