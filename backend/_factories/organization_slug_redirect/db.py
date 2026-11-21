# pyright: reportIncompatibleVariableOverride=false
"""The ``OrganizationSlugRedirectDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.organization_slug_redirect.db import OrganizationSlugRedirectDB


class OrganizationSlugRedirectDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[OrganizationSlugRedirectDB],
):
    """Build an old slug; pass the organization it points at."""

    class Meta:
        model = OrganizationSlugRedirectDB
        sqlalchemy_session = DBSessionManager().scoped_session

    old_slug = numbered("old-organization-{n}")
    organization_id = None  # a real foreign key: pass an existing organization's id
