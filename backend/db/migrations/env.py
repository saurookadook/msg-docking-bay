"""Migrate with the application's URL and metadata (ALEM-2)."""

from logging.config import fileConfig
from typing import Final

from alembic import context
from sqlalchemy import MetaData, create_engine, pool, text

from db.base_db import BaseDB
from db.db_session_manager import DBSessionManager
from models.armament.db import ArmamentDB
from models.character.db import CharacterDB
from models.character_appearance.db import CharacterAppearanceDB
from models.continuity.db import ContinuityDB
from models.equipment.db import EquipmentDB
from models.ingest_run.db import IngestRunDB
from models.material.db import MaterialDB
from models.mechanical_designer.db import MechanicalDesignerDB
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.mobile_suit_pilot.db import MobileSuitPilotDB
from models.mobile_suit_relation.db import MobileSuitRelationDB
from models.organization.db import OrganizationDB
from models.organization_appearance.db import OrganizationAppearanceDB
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

MODELS: Final = (
    ArmamentDB,
    CharacterAppearanceDB,
    CharacterDB,
    ContinuityDB,
    EquipmentDB,
    IngestRunDB,
    MaterialDB,
    MechanicalDesignerDB,
    MobileSuitAppearanceDB,
    MobileSuitDB,
    MobileSuitOrganizationDB,
    MobileSuitPilotDB,
    MobileSuitRelationDB,
    OrganizationAppearanceDB,
    OrganizationDB,
    PowerplantDB,
    SourceDB,
    SpecSheetArmamentDB,
    SpecSheetDB,
    SpecSheetEquipmentDB,
    SpecSheetMaterialDB,
    SpecSheetPowerplantDB,
    WorkDB,
    WorkRelationDB,
    WorkShortNameDB,
)
"""Every model, imported so autogenerate sees its table (SQLA-13).

List each new model here, and in scripts/db/initialize.py once it
exists; a model that is not imported is missing from the metadata.
"""

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata: MetaData = BaseDB.metadata


def run_migrations_offline() -> None:
    """Emit the migrations as SQL, without connecting."""
    context.configure(
        url=DBSessionManager.build_psql_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_server_default=True,
        transaction_per_migration=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migrate through a dedicated connection with a short lock wait."""
    engine = create_engine(DBSessionManager.build_psql_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        connection.execute(text("SET lock_timeout = '5s'"))
        connection.commit()  # a session-level SET outlives each migration's commit
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_server_default=True,
            transaction_per_migration=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
