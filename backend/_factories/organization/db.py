# pyright: reportIncompatibleVariableOverride=false
"""The ``OrganizationDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _factories.sequences import numbered
from db.db_session_manager import DBSessionManager
from models.organization.db import OrganizationDB


class OrganizationDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[OrganizationDB],
):
    """Build a top-level organization with no wiki page."""

    class Meta:
        model = OrganizationDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    fandom_page_title = None
    name = numbered("Organization {n}")
    parent_organization_id = None  # a real foreign key: pass an existing id
    slug = numbered("organization-{n}")
