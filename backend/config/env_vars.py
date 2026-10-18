"""Read and validate the process environment, once (PY-26)."""

import os
from collections.abc import Mapping
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field

from utils.singleton_meta import SingletonMeta


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

    # Logging
    log_level: Annotated[
        Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        Field(validation_alias="LOG_LEVEL"),
    ] = "INFO"

    @classmethod
    def from_environ(cls, environ: Mapping[str, str] | None = None) -> Self:
        """Validate the process environment, or a test's mapping."""
        return cls.model_validate(dict(os.environ if environ is None else environ))


class EnvVarManager(metaclass=SingletonMeta):
    """Hold the validated configuration for the process (PY-28)."""

    def __init__(self) -> None:
        """Validate the process environment."""
        self.env_vars: EnvVars = EnvVars.from_environ()

    def reload(self, environ: Mapping[str, str] | None = None) -> EnvVars:
        """Re-read the configuration after a test changes it."""
        self.env_vars = EnvVars.from_environ(environ)
        return self.env_vars


def is_prod() -> bool:
    """Return whether the process runs in production."""
    return EnvVarManager().env_vars.environment == "prod"
