"""The only place that creates the engine and sessions (SQLA-14)."""

from functools import cached_property

from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from config.env_vars import EnvVarManager, EnvVars
from utils.singleton_meta import SingletonMeta


class DBSessionManager(metaclass=SingletonMeta):
    """Hold the process's connection pool and session factory (PG-14).

    The engine is built on first use, never at import (PY-27), so each
    worker process opens its own connections.
    """

    @staticmethod
    def build_psql_url(env_vars: EnvVars | None = None) -> URL:
        """Build the psycopg 3 URL from the configuration.

        ``URL.create`` escapes the password, so it may contain any
        character. Alembic's ``env.py`` uses this too (ALEM-2).
        """
        config: EnvVars = env_vars or EnvVarManager().env_vars
        return URL.create(
            "postgresql+psycopg",
            username=config.database_user,
            password=config.database_password.get_secret_value(),
            host=config.database_host,
            port=config.database_port,
            database=config.database_name,
        )

    @cached_property
    def engine(self) -> Engine:
        """Return the process's engine, creating it on first use."""
        env_vars = EnvVarManager().env_vars
        application_name = (
            "app-backend-test" if env_vars.environment == "test" else "app-backend"
        )
        return create_engine(
            self.build_psql_url(env_vars),
            connect_args={
                "application_name": application_name,
                "connect_timeout": 5,
                "options": (
                    "-c timezone=utc -c statement_timeout=10s"
                    " -c idle_in_transaction_session_timeout=30s"
                ),
            },
            echo=env_vars.log_sql,
            max_overflow=30,
            pool_pre_ping=True,
        )

    @cached_property
    def scoped_session(self) -> scoped_session[Session]:
        """Return the thread-local registry for scripts, jobs, tests.

        Never use it in request handling (FAPI-9). Its callers call
        ``scoped_session.remove()`` in a ``finally``.
        """
        return scoped_session(
            sessionmaker(autoflush=False, bind=self.engine, expire_on_commit=False)
        )
