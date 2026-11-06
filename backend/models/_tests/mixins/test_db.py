from typing import ClassVar

from sqlalchemy import MetaData, Table
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.db import CreatedAtDB, TimestampsDB


class MixinTestBase(DeclarativeBase):
    """Its own metadata keeps these tables out of BaseDB.metadata."""

    metadata = MetaData()
    type_annotation_map: ClassVar = BaseDB.type_annotation_map


class StampedEntityDB(MixinTestBase, TimestampsDB):
    __tablename__ = "stamped_entities"

    id: Mapped[int] = mapped_column(primary_key=True)


class StampedJunctionDB(MixinTestBase, CreatedAtDB):
    __tablename__ = "stamped_junctions"

    id: Mapped[int] = mapped_column(primary_key=True)


def table_of(model: type[MixinTestBase]) -> Table:
    return MixinTestBase.metadata.tables[model.__tablename__]


class TestTimestampsDB:
    def test_adds_timezone_aware_not_null_timestamps(self) -> None:
        table = table_of(StampedEntityDB)

        for name in ("created_at", "updated_at"):
            column = table.c[name]
            assert isinstance(column.type, postgresql.TIMESTAMP)
            assert column.type.timezone is True
            assert column.nullable is False

    def test_defaults_both_timestamps_to_now_on_the_server(self) -> None:
        table = table_of(StampedEntityDB)

        for name in ("created_at", "updated_at"):
            assert table.c[name].server_default is not None

    def test_refreshes_updated_at_on_update(self) -> None:
        table = table_of(StampedEntityDB)

        assert table.c.updated_at.onupdate is not None
        assert table.c.created_at.onupdate is None


class TestCreatedAtDB:
    def test_adds_created_at_only(self) -> None:
        table = table_of(StampedJunctionDB)

        assert "created_at" in table.c
        assert "updated_at" not in table.c
