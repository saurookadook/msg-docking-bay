import logging
from collections.abc import Iterator

import pytest
from rich.logging import RichHandler

from config.env_vars import EnvVarManager
from utils.logging.init import HANDLER_NAME, init_logging


@pytest.fixture(autouse=True)
def restore_logging() -> Iterator[None]:
    yield
    EnvVarManager().reload()
    init_logging(app_name="test")


def _app_handlers() -> list[logging.Handler]:
    return [h for h in logging.getLogger().handlers if h.get_name() == HANDLER_NAME]


class TestInitLogging:
    def test_returns_the_named_logger(self) -> None:
        assert init_logging(app_name="some-app").name == "some-app"

    def test_sets_the_root_level_from_log_level(self) -> None:
        EnvVarManager().reload({"LOG_LEVEL": "WARNING"})

        init_logging(app_name="test")

        assert logging.getLogger().level == logging.WARNING

    def test_uses_rich_outside_production(self) -> None:
        EnvVarManager().reload({"ENVIRONMENT": "dev"})

        init_logging(app_name="test")

        assert [type(h) for h in _app_handlers()] == [RichHandler]

    def test_uses_a_plain_stream_handler_in_production(self) -> None:
        EnvVarManager().reload({"ENVIRONMENT": "prod"})

        init_logging(app_name="test")

        assert [type(h) for h in _app_handlers()] == [logging.StreamHandler]

    def test_replaces_its_handler_when_called_again(self) -> None:
        init_logging(app_name="test")
        init_logging(app_name="test")

        assert len(_app_handlers()) == 1
