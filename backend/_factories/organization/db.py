# pyright: reportIncompatibleVariableOverride=false
"""The ``OrganizationDB`` factory (PYTEST-11)."""

import uuid
from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction, Sequence

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

    id: LazyFunction = LazyFunction(uuid7)
    fandom_page_id: int | None = None
    fandom_page_title: str | None = None
    name: Sequence = numbered("Organization {n}")
    # a real foreign key: pass an existing id
    parent_organization_id: uuid.UUID | None = None
    slug: Sequence = numbered("organization-{n}")
