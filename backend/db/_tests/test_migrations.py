from alembic import command
from alembic.script import ScriptDirectory

from conftest import alembic_config


class TestMigrations:
    def test_has_one_head(self) -> None:
        """Two heads mean two branches need a merge revision (ALEM-10).

        Zero until the first revision exists.
        """
        script = ScriptDirectory.from_config(alembic_config())

        assert len(script.get_heads()) <= 1

    def test_downgrade_and_upgrade_round_trip(self) -> None:
        """A downgrade that leaves an object behind breaks the upgrade
        (ALEM-8, ALEM-14).
        """
        config = alembic_config()

        command.downgrade(config, "base")
        command.upgrade(config, "head")
