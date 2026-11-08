# pyright: reportIncompatibleVariableOverride=false
"""The ``SpecSheetDB`` factory (PYTEST-11)."""

from uuid import uuid7

from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import LazyFunction

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from db.db_session_manager import DBSessionManager
from models.spec_sheet.db import SpecSheetDB


class SpecSheetDBFactory(
    TimestampsDBMixinFactory,
    SQLAlchemyModelFactory,
    metaclass=BaseMetaFactory[SpecSheetDB],
):
    """Build an empty base sheet; pass the suit's and source's ids."""

    class Meta:
        model = SpecSheetDB
        sqlalchemy_session = DBSessionManager().scoped_session

    id = LazyFunction(uuid7)
    configuration = None
    empty_weight_kg = None
    generator_output_kw = None
    gross_weight_kg = None
    head_height_m = None
    max_acceleration_g = None
    max_speed_kmh = None
    mobile_suit_id = None  # a real foreign key: pass an existing suit's id
    overall_height_m = None
    raw_infobox = LazyFunction(dict)  # a new dict per sheet, never shared
    sensor_range_m = None
    source_id = None  # a real foreign key: pass an existing source's id
    total_thrust_kg = None
    turn_time_s = None
