"""SQLAlchemy models, one package per entity (SQLA-4).

Importing the package imports every model, so string targets in
``relationship()`` always resolve, whichever model a caller imports
first.
"""

from models.armament.db import ArmamentDB
from models.character.db import CharacterDB
from models.character_appearance.db import CharacterAppearanceDB
from models.character_slug_redirect.db import CharacterSlugRedirectDB
from models.continuity.db import ContinuityDB
from models.equipment.db import EquipmentDB
from models.ingest_run.db import IngestRunDB
from models.material.db import MaterialDB
from models.mechanical_designer.db import MechanicalDesignerDB
from models.mechanical_designer_slug_redirect.db import MechanicalDesignerSlugRedirectDB
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB
from models.mobile_suit_designer.db import MobileSuitDesignerDB
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.mobile_suit_pilot.db import MobileSuitPilotDB
from models.mobile_suit_relation.db import MobileSuitRelationDB
from models.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDB
from models.organization.db import OrganizationDB
from models.organization_appearance.db import OrganizationAppearanceDB
from models.organization_slug_redirect.db import OrganizationSlugRedirectDB
from models.powerplant.db import PowerplantDB
from models.source.db import SourceDB
from models.spec_sheet.db import SpecSheetDB
from models.spec_sheet_armament.db import SpecSheetArmamentDB
from models.spec_sheet_equipment.db import SpecSheetEquipmentDB
from models.spec_sheet_material.db import SpecSheetMaterialDB
from models.spec_sheet_powerplant.db import SpecSheetPowerplantDB
from models.work.db import WorkDB
from models.work_relation.db import WorkRelationDB
from models.work_short_name.db import WorkShortNameDB
from models.work_slug_redirect.db import WorkSlugRedirectDB

__all__ = [
    "ArmamentDB",
    "CharacterAppearanceDB",
    "CharacterDB",
    "CharacterSlugRedirectDB",
    "ContinuityDB",
    "EquipmentDB",
    "IngestRunDB",
    "MaterialDB",
    "MechanicalDesignerDB",
    "MechanicalDesignerSlugRedirectDB",
    "MobileSuitAppearanceDB",
    "MobileSuitDB",
    "MobileSuitDesignerDB",
    "MobileSuitOrganizationDB",
    "MobileSuitPilotDB",
    "MobileSuitRelationDB",
    "MobileSuitSlugRedirectDB",
    "OrganizationAppearanceDB",
    "OrganizationDB",
    "OrganizationSlugRedirectDB",
    "PowerplantDB",
    "SourceDB",
    "SpecSheetArmamentDB",
    "SpecSheetDB",
    "SpecSheetEquipmentDB",
    "SpecSheetMaterialDB",
    "SpecSheetPowerplantDB",
    "WorkDB",
    "WorkRelationDB",
    "WorkShortNameDB",
    "WorkSlugRedirectDB",
]
