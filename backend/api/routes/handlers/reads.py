"""The error mapping read routes share (fastapi.md FAPI-13)."""

import logging
from collections.abc import Callable

from fastapi import HTTPException, status


def run_read[T](
    operation: Callable[[], T],
    *,
    error_detail: str,
    logger: logging.Logger,
    not_found: type[Exception] | None = None,
    not_found_detail: str = "Not found",
) -> T:
    """Run a facade read and map its errors onto status codes.

    ``not_found`` becomes a 404 with ``not_found_detail``; any other
    error is logged with its traceback and becomes a 500 with the fixed
    ``error_detail``, so no internal message reaches the client. A list
    route passes no ``not_found``: an empty page is a 200 (FAPI-12).

    Raises:
        HTTPException: 404 for ``not_found``, 500 for anything else.
    """
    try:
        return operation()
    except Exception as e:
        if not_found is not None and isinstance(e, not_found):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail
            ) from e
        logger.exception(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail
        ) from e
