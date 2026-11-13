# pyright: reportIncompatibleVariableOverride=false
"""The ``MobileSuitDesignerDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.mobile_suit_designer.db import MobileSuitDesignerDB


class MobileSuitDesignerDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MobileSuitDesignerDB],
):
    """Build a design credit; every column is a real foreign key."""

    class Meta:
        model = MobileSuitDesignerDB
        sqlalchemy_session = DBSessionManager().scoped_session

    mechanical_designer_id = None  # a real foreign key: pass a designer's id
    mobile_suit_id = None  # a real foreign key: pass an existing suit's id
    source_id = None  # a real foreign key: pass an existing source's id
