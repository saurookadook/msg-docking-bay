# pyright: reportIncompatibleVariableOverride=false
"""The ``MechanicalDesignerSlugRedirectDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.mechanical_designer_slug_redirect.db import MechanicalDesignerSlugRedirectDB


class MechanicalDesignerSlugRedirectDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MechanicalDesignerSlugRedirectDB],
):
    """Build an old slug; pass the designer it points at."""

    class Meta:
        model = MechanicalDesignerSlugRedirectDB
        sqlalchemy_session = DBSessionManager().scoped_session

    old_slug = numbered("old-designer-{n}")
    mechanical_designer_id = None  # a real foreign key: pass an existing designer's id
