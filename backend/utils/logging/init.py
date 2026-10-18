"""Configure logging for a process (PY-38)."""

import logging

from config.env_vars import EnvVarManager, is_prod

HANDLER_NAME = "app"
"""Names the root handler ``init_logging`` installs, so a second call
replaces it without touching handlers that others (pytest) attached.
"""


def init_logging(*, app_name: str) -> logging.Logger:
    """Install the root handler, set the level, and return a logger.

    Call once per process, from its entry point. ``RichHandler`` is
    used outside production for readable local output; production
    gets a plain ``StreamHandler`` whose lines log tools can parse.

    Args:
        app_name: The name of the logger to return.
    """
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if handler.get_name() == HANDLER_NAME:
            root_logger.removeHandler(handler)

    handler = _build_handler(prod=is_prod())
    handler.set_name(HANDLER_NAME)
    root_logger.addHandler(handler)
    # Read per call, so a test's reloaded configuration applies (PY-27).
    root_logger.setLevel(EnvVarManager().env_vars.log_level)

    return logging.getLogger(app_name)


def _build_handler(*, prod: bool) -> logging.Handler:
    if prod:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        return handler

    # Deferred: rich is only needed outside production (PY-14).
    from rich.logging import RichHandler

    return RichHandler(rich_tracebacks=True)
