from pydantic import SecretStr

from config.env_vars import EnvVars
from db.db_session_manager import DBSessionManager


class TestBuildPsqlUrl:
    def test_uses_psycopg_and_the_configuration(self) -> None:
        env_vars = EnvVars.from_environ(
            {
                "DATABASE_HOST": "db.internal",
                "DATABASE_NAME": "projects",
                "DATABASE_PASSWORD": "pw",
                "DATABASE_PORT": "6543",
                "DATABASE_USER": "reader",
            }
        )

        url = DBSessionManager.build_psql_url(env_vars)

        assert url.render_as_string(hide_password=False) == (
            "postgresql+psycopg://reader:pw@db.internal:6543/projects"
        )

    def test_escapes_the_password(self) -> None:
        env_vars = EnvVars.from_environ({}).model_copy(
            update={"database_password": SecretStr("p@ss/w:rd")}
        )

        url = DBSessionManager.build_psql_url(env_vars)

        assert url.password == "p@ss/w:rd"
        assert "p%40ss%2Fw%3Ard" in url.render_as_string(hide_password=False)
