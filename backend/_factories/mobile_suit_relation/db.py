# pyright: reportIncompatibleVariableOverride=false
"""The ``MobileSuitRelationDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from constants.catalog import MobileSuitRelationType
from db.db_session_manager import DBSessionManager
from models.mobile_suit_relation.db import MobileSuitRelationDB


class MobileSuitRelationDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MobileSuitRelationDB],
):
    """Build a variant edge; pass both suits' ids and a source's."""

    class Meta:
        model = MobileSuitRelationDB
        sqlalchemy_session = DBSessionManager().scoped_session

    from_mobile_suit_id = None  # a real foreign key: pass an existing suit's id
    relation_type = MobileSuitRelationType.VARIANT_OF
    source_id = None  # a real foreign key: pass an existing source's id
    to_mobile_suit_id = None  # a real foreign key: pass an existing suit's id
