"""The base every facade inherits from (sqlalchemy.md SQLA-16)."""

import re
import uuid
from collections.abc import Mapping, Sequence
from typing import Any, Final

from sqlalchemy import (
    ColumnElement,
    SQLColumnExpression,
    case,
    func,
    or_,
    select,
    tuple_,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from db.base_db import RootDB
from db.db_session_manager import DBSessionManager

_NOT_SEARCHABLE: Final = re.compile(r"[^a-z0-9]")
_NOT_SEARCHABLE_SQL: Final = "[^a-z0-9]"


def normalize_search(q: str | None) -> str | None:
    """Lowercase ``q`` and keep only ``a-z0-9`` (D8).

    ``RX 78-2`` and ``rx-78-2`` both become ``rx782``.

    Returns:
        The needle, or ``None`` when nothing is left, which callers
        treat as no filter: a blank search box lists everything.
    """
    if q is None:
        return None
    return _NOT_SEARCHABLE.sub("", q.lower()) or None


def _normalized(column: SQLColumnExpression[str | None]) -> ColumnElement[str | None]:
    """Normalize a column in SQL the way ``normalize_search`` does."""
    return func.regexp_replace(func.lower(column), _NOT_SEARCHABLE_SQL, "", "g")


class BaseFacade:
    """Hold the session and the helpers that facades share."""

    def __init__(self, *, db_session: Session | None = None) -> None:
        """Use the caller's session, or the scoped one for scripts.

        Routes always pass ``api_db_session`` (fastapi.md FAPI-9).
        """
        self.db_session: Session = (
            db_session
            if db_session is not None
            else DBSessionManager().scoped_session()
        )

    @staticmethod
    def _search_filter(
        columns: Sequence[SQLColumnExpression[str | None]], needle: str
    ) -> ColumnElement[bool]:
        """Match rows where any column contains the needle (D8).

        ``needle`` comes from ``normalize_search``, so it holds no
        ``LIKE`` wildcards; it is still a bound parameter (RDB-25).
        """
        return or_(*(_normalized(column).contains(needle) for column in columns))

    @staticmethod
    def _prefix_rank(
        columns: Sequence[SQLColumnExpression[str | None]], needle: str
    ) -> ColumnElement[int]:
        """Rank rows that start with the needle first (D8)."""
        starts = or_(*(_normalized(column).startswith(needle) for column in columns))
        return case((starts, 0), else_=1)

    @staticmethod
    def _has_slug(
        slug_column: SQLColumnExpression[str],
        id_column: SQLColumnExpression[uuid.UUID],
        redirect_old_slug: SQLColumnExpression[str],
        redirect_target: SQLColumnExpression[uuid.UUID],
        slug: str,
    ) -> ColumnElement[bool]:
        """Match the row whose current or old slug this is (D2).

        Order by ``_current_slug_first`` too: an old slug can name
        another row's current one.
        """
        return or_(
            slug_column == slug,
            id_column.in_(select(redirect_target).where(redirect_old_slug == slug)),
        )

    @staticmethod
    def _current_slug_first(
        slug_column: SQLColumnExpression[str], slug: str
    ) -> ColumnElement[int]:
        """Rank a current slug before an old one (D2)."""
        return case((slug_column == slug, 0), else_=1)

    def _upsert[T: RootDB](
        self,
        model: type[T],
        *,
        payload: Mapping[str, Any],
        conflict_columns: Sequence[str],
    ) -> T:
        """Insert a row, or update it on its natural key if it changed.

        The update runs only when some column differs (``IS DISTINCT
        FROM``), so an unchanged row keeps its ``updated_at``
        (sqlalchemy.md SQLA-25, catalog-read-api.md D5). When nothing
        changed, the guarded statement returns no row, so the row is
        read back by its key.

        Args:
            model: the table's model class.
            payload: column values, keyed by column name.
            conflict_columns: the unique key to upsert on.

        Returns:
            The row as stored after the statement.

        Raises:
            ValueError: when a payload key is not a column (SQLA-26), or
                every payload column is in the key, so there is nothing
                to compare or update.
        """
        table = model.__table__
        unknown = sorted(set(payload) - set(table.c.keys()))
        if unknown:
            raise ValueError(
                f"Not columns of {model.__tablename__}: {', '.join(unknown)}"
            )
        stmt = insert(model).values(**payload)
        changing = [name for name in payload if name not in conflict_columns]
        if not changing:
            raise ValueError("An upsert payload needs a column outside its key")
        set_: dict[str, Any] = {name: stmt.excluded[name] for name in changing}
        if "updated_at" in table.c:
            set_["updated_at"] = func.now()
        stmt = stmt.on_conflict_do_update(
            index_elements=list(conflict_columns),
            set_=set_,
            where=tuple_(*(table.c[name] for name in changing)).is_distinct_from(
                tuple_(*(stmt.excluded[name] for name in changing))
            ),
        )
        row = self.db_session.scalars(
            stmt.returning(model), execution_options={"populate_existing": True}
        ).one_or_none()
        if row is not None:
            return row
        key = [
            table.c[name].is_not_distinct_from(payload[name])
            for name in conflict_columns
        ]
        return self.db_session.execute(select(model).where(*key)).scalar_one()
