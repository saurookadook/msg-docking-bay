from collections.abc import Iterator

import pytest
from pydantic import ValidationError

from config.env_vars import EnvVarManager, EnvVars, is_prod


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
