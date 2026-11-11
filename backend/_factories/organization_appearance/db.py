# pyright: reportIncompatibleVariableOverride=false
"""The ``OrganizationAppearanceDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.organization_appearance.db import OrganizationAppearanceDB


class OrganizationAppearanceDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[OrganizationAppearanceDB],
):
    """Build an appearance; every column is a real foreign key."""

    class Meta:
        model = OrganizationAppearanceDB
        sqlalchemy_session = DBSessionManager().scoped_session

    organization_id = None  # a real foreign key: pass an existing organization's id
    source_id = None  # a real foreign key: pass an existing source's id
    work_id = None  # a real foreign key: pass an existing work's id
