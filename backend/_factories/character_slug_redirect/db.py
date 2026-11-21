# pyright: reportIncompatibleVariableOverride=false
"""The ``CharacterSlugRedirectDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.character_slug_redirect.db import CharacterSlugRedirectDB


class CharacterSlugRedirectDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[CharacterSlugRedirectDB],
):
    """Build an old slug; pass the character it points at."""

    class Meta:
        model = CharacterSlugRedirectDB
        sqlalchemy_session = DBSessionManager().scoped_session

    old_slug = numbered("old-character-{n}")
    character_id = None  # a real foreign key: pass an existing character's id
