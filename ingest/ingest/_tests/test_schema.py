import pytest
from alembic.script import ScriptDirectory
from sqlalchemy.orm import Session

from _fixtures.db import alembic_config
from ingest.errors import SchemaNotAtHeadError
from ingest.schema import (
    MIGRATE_HINT,
    UPDATE_HINT,
    assert_schema_at_head,
    check_heads,
    current_heads,
    expected_heads,
    known_revisions,
)

# Labels for check_heads, not the real chain, which grows with each PR.
HEAD = "2222aaaa2222"
OLDER = "1111aaaa1111"
NEWER = "3333aaaa3333"
KNOWN = {OLDER, HEAD}


class TestBackendMigrations:
    def test_reads_the_same_heads_as_the_backends_alembic_config(self) -> None:
        """The folder found through ``db`` is alembic.ini's."""
        backend = ScriptDirectory.from_config(alembic_config())

        assert expected_heads() == backend.get_heads()
        assert known_revisions() == {
            script.revision for script in backend.walk_revisions()
        }


class TestAssertSchemaAtHead:
    def test_accepts_the_migrated_test_database(self, test_db_session: Session) -> None:
        connection = test_db_session.connection()

        assert assert_schema_at_head(connection) == current_heads(connection)
        assert set(current_heads(connection)) == set(expected_heads())


class TestCheckHeads:
    def test_accepts_matching_heads_in_any_order(self) -> None:
        check_heads(expected=["b", "a"], current=("a", "b"), known={"a", "b"})

    def test_rejects_a_database_behind_the_head(self) -> None:
        with pytest.raises(SchemaNotAtHeadError) as exc_info:
            check_heads(expected=[HEAD], current=(OLDER,), known=KNOWN)

        message = str(exc_info.value)
        assert f"revision '{OLDER}'" in message
        assert f"head '{HEAD}'" in message
        assert message.endswith(MIGRATE_HINT)

    def test_rejects_a_database_migrated_by_a_newer_backend(self) -> None:
        with pytest.raises(SchemaNotAtHeadError) as exc_info:
            check_heads(expected=[HEAD], current=(NEWER,), known=KNOWN)

        assert str(exc_info.value).endswith(UPDATE_HINT)

    def test_rejects_an_unmigrated_database(self) -> None:
        with pytest.raises(SchemaNotAtHeadError) as exc_info:
            check_heads(expected=[HEAD], current=(), known=KNOWN)

        message = str(exc_info.value)
        assert message.startswith("The database has no migrations applied")
        assert message.endswith(MIGRATE_HINT)
