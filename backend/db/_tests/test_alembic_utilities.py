import sqlalchemy as sa
from alembic import op
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.migrations.alembic_utilities import (
    create_pg_enum,
    drop_pg_enum,
    existing_pg_enum,
)

VALUES = ["fixed", "handheld"]


def enum_labels(test_db_session: Session, name: str) -> list[str]:
    rows = test_db_session.execute(
        text(
            "SELECT e.enumlabel FROM pg_enum e"
            " JOIN pg_type t ON t.oid = e.enumtypid"
            " WHERE t.typname = :name ORDER BY e.enumsortorder"
        ),
        {"name": name},
    )
    return [label for (label,) in rows]


class TestPgEnumHelpers:
    def test_creates_the_type_with_its_values_in_order(
        self, test_db_session: Session
    ) -> None:
        context = MigrationContext.configure(test_db_session.connection())

        with Operations.context(context):
            enum_type = create_pg_enum("test_mount", VALUES)

        assert enum_labels(test_db_session, "test_mount") == VALUES
        assert enum_type.name == "test_mount"

    def test_drops_the_type(self, test_db_session: Session) -> None:
        context = MigrationContext.configure(test_db_session.connection())

        with Operations.context(context):
            create_pg_enum("test_mount", VALUES)
            drop_pg_enum("test_mount", VALUES)

        assert enum_labels(test_db_session, "test_mount") == []

    def test_shares_an_existing_type_without_creating_it_again(
        self, test_db_session: Session
    ) -> None:
        """A second ``create_table`` must not re-create the type."""
        context = MigrationContext.configure(test_db_session.connection())

        with Operations.context(context):
            create_pg_enum("test_mount", VALUES)
            op.create_table(
                "test_mounts",
                sa.Column("mount", existing_pg_enum("test_mount", VALUES)),
            )
            op.drop_table("test_mounts")

        assert enum_labels(test_db_session, "test_mount") == VALUES
