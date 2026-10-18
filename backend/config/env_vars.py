"""Read and validate the process environment, once (PY-26)."""

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from utils.singleton_meta import SingletonMeta

FILE_SUFFIX: Final = "_FILE"


class EnvVars(BaseModel, frozen=True):
    """The backend's configuration, validated from the environment."""

    model_config = ConfigDict(
        extra="ignore", hide_input_in_errors=True, validate_default=True
    )

    # App
    environment: Annotated[
        Literal["dev", "test", "prod"], Field(validation_alias="ENVIRONMENT")
    ] = "dev"
    """Read it through ``is_prod()``, never by comparing strings
    (ENV-3).
    """

    # Hosts
    app_domain: Annotated[str, Field(validation_alias="APP_DOMAIN")] = (
        "msg-docking-bay.dev"
    )

    # Database
    database_host: Annotated[str, Field(validation_alias="DATABASE_HOST")] = "postgres"
    database_name: Annotated[str, Field(validation_alias="DATABASE_NAME")] = "app"
    database_password: Annotated[
        SecretStr, Field(validation_alias="DATABASE_PASSWORD")
    ] = SecretStr("UNSET")
    """Set through ``DATABASE_PASSWORD_FILE`` in containers (ENV-31)."""
    database_port: Annotated[int, Field(gt=0, validation_alias="DATABASE_PORT")] = 5432
    database_user: Annotated[str, Field(validation_alias="DATABASE_USER")] = "app"
    log_sql: Annotated[bool, Field(validation_alias="LOG_SQL")] = False
    """Accepts true/false, 1/0, yes/no or on/off, in any case."""

    # Logging
    log_level: Annotated[
        Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        Field(validation_alias="LOG_LEVEL"),
    ] = "INFO"

    @classmethod
    def from_environ(cls, environ: Mapping[str, str] | None = None) -> Self:
        """Validate the process environment, or a test's mapping.

        Each ``<NAME>_FILE`` variable is replaced by ``<NAME>``, set to
        the contents of that file, so secrets can be mounted as files
        (ENV-31). A file's value wins over a plain ``<NAME>``.
        """
        return cls.model_validate(
            resolve_file_variables(os.environ if environ is None else environ)
        )


class EnvVarManager(metaclass=SingletonMeta):
    """Hold the validated configuration for the process (PY-28)."""

    def __init__(self) -> None:
        """Validate the process environment."""
        self.env_vars: EnvVars = EnvVars.from_environ()

    def reload(self, environ: Mapping[str, str] | None = None) -> EnvVars:
        """Re-read the configuration after a test changes it."""
        self.env_vars = EnvVars.from_environ(environ)
        return self.env_vars


def resolve_file_variables(environ: Mapping[str, str]) -> dict[str, str]:
    """Replace each ``<NAME>_FILE`` with ``<NAME>``, read from the file.

    Raises:
        OSError: A ``<NAME>_FILE`` variable names a file that cannot be
            read, so a missing secret fails at startup.
    """
    resolved = dict(environ)
    for name, path in environ.items():
        if name.endswith(FILE_SUFFIX):
            del resolved[name]
            resolved[name.removesuffix(FILE_SUFFIX)] = (
                Path(path).read_text(encoding="utf-8").strip()
            )
    return resolved


def is_prod() -> bool:
    """Return whether the process runs in production."""
    return EnvVarManager().env_vars.environment == "prod"
