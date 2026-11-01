# pyright: reportIncompatibleVariableOverride=false
"""The ``WorkDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from constants.catalog import WorkType
from db.db_session_manager import DBSessionManager
from models.work.db import WorkDB


class WorkDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[WorkDB],
):
    """Build a TV series with no timeline, parent, or external IDs."""

    class Meta:
        model = WorkDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    anilist_id = None
    ann_id = None
    continuity_id = None  # a real foreign key: pass an existing continuity's id
    end_date = None
    fandom_page_title = None
    parent_work_id = None
    slug = numbered("work-{n}")
    start_date = None
    title = numbered("Work {n}")
    title_ja = None
    wikidata_qid = None
    work_type = WorkType.TV_SERIES
