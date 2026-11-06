# pyright: reportIncompatibleVariableOverride=false
"""The ``WorkRelationDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from constants.catalog import WorkRelationType
from db.db_session_manager import DBSessionManager
from models.work_relation.db import WorkRelationDB


class WorkRelationDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[WorkRelationDB],
):
    """Build a sequel edge; pass both works' ids and a source's."""

    class Meta:
        model = WorkRelationDB
        sqlalchemy_session = DBSessionManager().scoped_session

    from_work_id = None  # a real foreign key: pass an existing work's id
    relation_type = WorkRelationType.SEQUEL_OF
    source_id = None  # a real foreign key: pass an existing source's id
    to_work_id = None  # a real foreign key: pass an existing work's id
