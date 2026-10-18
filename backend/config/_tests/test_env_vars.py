from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from config.env_vars import EnvVarManager, EnvVars, is_prod, resolve_file_variables


@pytest.fixture
def restore_env_vars() -> Iterator[None]:
    yield
    EnvVarManager().reload()


class TestEnvVars:
    def test_defaults_to_development(self) -> None:
        env_vars = EnvVars.from_environ({})

        assert env_vars.environment == "dev"
        assert env_vars.log_level == "INFO"

    def test_from_environ_reads_the_mapping(self) -> None:
        env_vars = EnvVars.from_environ({"ENVIRONMENT": "prod", "LOG_LEVEL": "DEBUG"})

        assert env_vars.environment == "prod"
        assert env_vars.log_level == "DEBUG"

    def test_from_environ_ignores_unrelated_variables(self) -> None:
        env_vars = EnvVars.from_environ({"HOME": "/home/app"})

        assert env_vars == EnvVars.from_environ({})

    def test_rejects_an_unknown_log_level(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            EnvVars.from_environ({"LOG_LEVEL": "LOUD"})

        assert exc_info.value.errors()[0]["type"] == "literal_error"


class TestEnvVarManager:
    def test_is_a_singleton(self) -> None:
        assert EnvVarManager() is EnvVarManager()

    @pytest.mark.usefixtures("restore_env_vars")
    def test_reload_replaces_the_configuration(self) -> None:
        EnvVarManager().reload({"LOG_LEVEL": "ERROR"})

        assert EnvVarManager().env_vars.log_level == "ERROR"


@pytest.mark.usefixtures("restore_env_vars")
class TestIsProd:
    @pytest.mark.parametrize(
        "environment, expected",
        [
            ("dev", False),
            ("test", False),
            ("prod", True),
        ],
    )
    def test_is_true_only_in_production(self, environment: str, expected: bool) -> None:
        EnvVarManager().reload({"ENVIRONMENT": environment})

        assert is_prod() is expected


class TestDatabaseSettings:
    def test_defaults_to_the_compose_database(self) -> None:
        env_vars = EnvVars.from_environ({})

        assert env_vars.database_host == "postgres"
        assert env_vars.database_port == 5432
        assert env_vars.database_name == "app"
        assert env_vars.database_user == "app"
        assert env_vars.log_sql is False

    def test_hides_the_password_in_reprs(self) -> None:
        env_vars = EnvVars.from_environ({"DATABASE_PASSWORD": "hunter2"})

        assert "hunter2" not in repr(env_vars)
        assert env_vars.database_password.get_secret_value() == "hunter2"

    def test_rejects_a_non_numeric_port(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            EnvVars.from_environ({"DATABASE_PORT": "five"})

        assert exc_info.value.errors()[0]["type"] == "int_parsing"


class TestResolveFileVariables:
    def test_reads_the_secret_from_the_file(self, tmp_path: Path) -> None:
        secret_file = tmp_path / "db_password"
        secret_file.write_text("from-file\n", encoding="utf-8")

        env_vars = EnvVars.from_environ({"DATABASE_PASSWORD_FILE": str(secret_file)})

        assert env_vars.database_password.get_secret_value() == "from-file"

    def test_the_file_wins_over_the_plain_variable(self, tmp_path: Path) -> None:
        secret_file = tmp_path / "db_password"
        secret_file.write_text("from-file", encoding="utf-8")

        resolved = resolve_file_variables(
            {"DATABASE_PASSWORD": "plain", "DATABASE_PASSWORD_FILE": str(secret_file)}
        )

        assert resolved == {"DATABASE_PASSWORD": "from-file"}

    def test_a_missing_file_fails(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            resolve_file_variables({"DATABASE_PASSWORD_FILE": str(tmp_path / "nope")})
