# pyright: reportIncompatibleVariableOverride=false
"""The ``MobileSuitSlugRedirectDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDB


class MobileSuitSlugRedirectDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MobileSuitSlugRedirectDB],
):
    """Build an old slug; pass the suit it points at."""

    class Meta:
        model = MobileSuitSlugRedirectDB
        sqlalchemy_session = DBSessionManager().scoped_session

    mobile_suit_id = None  # a real foreign key: pass an existing suit's id
    old_slug = numbered("old-mobile-suit-{n}")
