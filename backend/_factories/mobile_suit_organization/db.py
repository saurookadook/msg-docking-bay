# pyright: reportIncompatibleVariableOverride=false
"""The ``MobileSuitOrganizationDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from constants.catalog import MobileSuitOrganizationRole
from db.db_session_manager import DBSessionManager
from models.mobile_suit_organization.db import MobileSuitOrganizationDB


class MobileSuitOrganizationDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[MobileSuitOrganizationDB],
):
    """Build an operator link with no work."""

    class Meta:
        model = MobileSuitOrganizationDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    mobile_suit_id = None  # a real foreign key: pass an existing suit's id
    organization_id = None  # a real foreign key: pass an existing org's id
    role = MobileSuitOrganizationRole.OPERATOR
    source_id = None  # a real foreign key: pass an existing source's id
    work_id = None
