"""Entities for ``spec_sheets`` (PYD-2, PYD-3, PYD-4)."""

import uuid
from typing import Any, Final, Literal, get_args

from pydantic import Field

from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin
from models.source.entity import SourceCitationEntity
from models.spec_sheet_armament.entity import ArmamentListingEntity
from models.spec_sheet_equipment.entity import EquipmentListingEntity
from models.spec_sheet_material.entity import MaterialListingEntity
from models.spec_sheet_powerplant.entity import PowerplantListingEntity

# NOTE: SpecSheetField and SpecSheetPartKind are plain assignments,
# not ``type`` statements (a departure from PY-43). Pydantic turns a
# ``type`` alias into a named schema (PYD-6), which would change the
# API contract; a plain Literal stays inlined in each field.
SpecSheetField = Literal[
    "empty_weight_kg",
    "generator_output_kw",
    "gross_weight_kg",
    "head_height_m",
    "max_acceleration_g",
    "max_speed_kmh",
    "overall_height_m",
    "sensor_range_m",
    "total_thrust_kg",
    "turn_time_s",
]
"""A spec sheet's measurements, each in the unit its name says."""

SPEC_SHEET_FIELDS: Final[tuple[SpecSheetField, ...]] = get_args(SpecSheetField)

SpecSheetPartKind = Literal["armaments", "equipment", "materials", "powerplants"]
"""A spec sheet's part lists, each named as its field is."""

SPEC_SHEET_PART_KINDS: Final[tuple[SpecSheetPartKind, ...]] = get_args(
    SpecSheetPartKind
)


class SpecSheetEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A spec sheet row, as stored."""

    configuration: str | None = None
    empty_weight_kg: float | None = None
    generator_output_kw: float | None = None
    gross_weight_kg: float | None = None
    head_height_m: float | None = None
    max_acceleration_g: float | None = None
    max_speed_kmh: float | None = None
    mobile_suit_id: uuid.UUID
    overall_height_m: float | None = None
    raw_infobox: dict[str, Any] = Field(default_factory=dict[str, Any])
    sensor_range_m: float | None = None
    source_id: uuid.UUID
    total_thrust_kg: float | None = None
    turn_time_s: float | None = None


class MobileSuitSpecSheetEntity(BaseEntityModel, TimestampsEntityMixin):
    """One configuration's specs, as one source gives them.

    Deliberately not ``SpecSheetEntity``: ``raw_infobox`` is bulky
    copied wiki text, kept out of anything served (D5), and ``id`` is
    not a public key.

    A named configuration's gaps are filled from the base sheet of the
    same source; ``inherited_fields`` names the columns that were, so a
    page can tell "same as base" from a value the source states. Its
    empty part lists are filled the same way, and ``inherited_parts``
    names them, so ``inherited_fields`` stays measurements only. A
    configuration cannot say it drops every part of a kind.
    """

    armaments: list[ArmamentListingEntity] = Field(
        default_factory=list[ArmamentListingEntity]
    )
    configuration: str | None = None
    """Null for the base sheet; otherwise the configuration's name."""
    empty_weight_kg: float | None = None
    equipment: list[EquipmentListingEntity] = Field(
        default_factory=list[EquipmentListingEntity]
    )
    generator_output_kw: float | None = None
    gross_weight_kg: float | None = None
    head_height_m: float | None = None
    inherited_fields: list[SpecSheetField] = Field(default_factory=list[SpecSheetField])
    inherited_parts: list[SpecSheetPartKind] = Field(
        default_factory=list[SpecSheetPartKind]
    )
    materials: list[MaterialListingEntity] = Field(
        default_factory=list[MaterialListingEntity]
    )
    max_acceleration_g: float | None = None
    max_speed_kmh: float | None = None
    overall_height_m: float | None = None
    powerplants: list[PowerplantListingEntity] = Field(
        default_factory=list[PowerplantListingEntity]
    )
    sensor_range_m: float | None = None
    total_thrust_kg: float | None = None
    turn_time_s: float | None = None

    # ----- from `sources`, through `source_id`
    source: SourceCitationEntity
