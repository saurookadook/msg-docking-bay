# pyright: reportIncompatibleVariableOverride=false
"""The ``MobileSuitAppearanceDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB


class MobileSuitAppearanceDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MobileSuitAppearanceDB],
):
    """Build a non-debut appearance with no episode range."""

    class Meta:
        model = MobileSuitAppearanceDB
        sqlalchemy_session = DBSessionManager().scoped_session

    first_episode = None
    is_debut = False
    last_episode = None
    mobile_suit_id = None  # a real foreign key: pass an existing suit's id
    source_id = None  # a real foreign key: pass an existing source's id
    work_id = None  # a real foreign key: pass an existing work's id
