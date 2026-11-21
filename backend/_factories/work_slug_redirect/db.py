# pyright: reportIncompatibleVariableOverride=false
"""The ``WorkSlugRedirectDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.work_slug_redirect.db import WorkSlugRedirectDB


class WorkSlugRedirectDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[WorkSlugRedirectDB],
):
    """Build an old slug; pass the work it points at."""

    class Meta:
        model = WorkSlugRedirectDB
        sqlalchemy_session = DBSessionManager().scoped_session

    old_slug = numbered("old-work-{n}")
    work_id = None  # a real foreign key: pass an existing work's id
