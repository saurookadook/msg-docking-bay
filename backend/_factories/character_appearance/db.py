# pyright: reportIncompatibleVariableOverride=false
"""The ``CharacterAppearanceDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.character_appearance.db import CharacterAppearanceDB


class CharacterAppearanceDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[CharacterAppearanceDB],
):
    """Build an appearance; every column is a real foreign key."""

    class Meta:
        model = CharacterAppearanceDB
        sqlalchemy_session = DBSessionManager().scoped_session

    character_id = None  # a real foreign key: pass an existing character's id
    source_id = None  # a real foreign key: pass an existing source's id
    work_id = None  # a real foreign key: pass an existing work's id
