# pyright: reportIncompatibleVariableOverride=false
"""The ``SpecSheetEquipmentDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from constants.catalog import EquipmentFit
from db.db_session_manager import DBSessionManager
from models.spec_sheet_equipment.db import SpecSheetEquipmentDB


class SpecSheetEquipmentDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[SpecSheetEquipmentDB],
):
    """Build a bare listing; pass the part's and the sheet's ids."""

    class Meta:
        model = SpecSheetEquipmentDB
        sqlalchemy_session = DBSessionManager().scoped_session

    equipment_id = None  # a real foreign key: pass an existing item's id
    fit = EquipmentFit.STANDARD
    note = None
    spec_sheet_id = None  # a real foreign key: pass an existing sheet's id
