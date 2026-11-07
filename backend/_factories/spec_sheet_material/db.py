# pyright: reportIncompatibleVariableOverride=false
"""The ``SpecSheetMaterialDB`` factory (PYTEST-11)."""

from factory.alchemy import SQLAlchemyModelFactory

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import CreatedAtDBMixinFactory
from constants.catalog import MaterialUse
from db.db_session_manager import DBSessionManager
from models.spec_sheet_material.db import SpecSheetMaterialDB


class SpecSheetMaterialDBFactory(
    CreatedAtDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[SpecSheetMaterialDB],
):
    """Build a bare listing; pass the part's and the sheet's ids."""

    class Meta:
        model = SpecSheetMaterialDB
        sqlalchemy_session = DBSessionManager().scoped_session

    material_id = None  # a real foreign key: pass an existing material's id
    material_use = MaterialUse.ARMOR
    note = None
    spec_sheet_id = None  # a real foreign key: pass an existing sheet's id
