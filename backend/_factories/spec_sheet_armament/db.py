# pyright: reportIncompatibleVariableOverride=false
"""The ``SpecSheetArmamentDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from constants.catalog import ArmamentMount
from db.db_session_manager import DBSessionManager
from models.spec_sheet_armament.db import SpecSheetArmamentDB


class SpecSheetArmamentDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[SpecSheetArmamentDB],
):
    """Build a bare listing; pass the part's and the sheet's ids."""

    class Meta:
        model = SpecSheetArmamentDB
        sqlalchemy_session = DBSessionManager().scoped_session

    armament_id = None  # a real foreign key: pass an existing weapon's id
    mount = ArmamentMount.FIXED
    note = None
    quantity_max = None
    quantity_min = None
    spec_sheet_id = None  # a real foreign key: pass an existing sheet's id
