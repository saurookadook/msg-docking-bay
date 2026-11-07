# pyright: reportIncompatibleVariableOverride=false
"""The ``SpecSheetPowerplantDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.spec_sheet_powerplant.db import SpecSheetPowerplantDB


class SpecSheetPowerplantDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[SpecSheetPowerplantDB],
):
    """Build a bare listing; pass the part's and the sheet's ids."""

    class Meta:
        model = SpecSheetPowerplantDB
        sqlalchemy_session = DBSessionManager().scoped_session

    note = None
    powerplant_id = None  # a real foreign key: pass an existing powerplant's id
    quantity_max = None
    quantity_min = None
    spec_sheet_id = None  # a real foreign key: pass an existing sheet's id
