"""PYD-3: every relationship the people reads use fails when not loaded.

A facade that drops an eager load then raises at once, in its tests,
rather than sending one query per row in production (SQLA-10, SQLA-22).
"""

from collections.abc import Callable

import pytest
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.character_appearance.db import CharacterAppearanceDBFactory
from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_designer.db import MobileSuitDesignerDBFactory
from _factories.mobile_suit_organization.db import MobileSuitOrganizationDBFactory
from _factories.mobile_suit_pilot.db import MobileSuitPilotDBFactory
from _factories.organization.db import OrganizationDBFactory
from _factories.organization_appearance.db import OrganizationAppearanceDBFactory
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from db.base_db import RootDB
from models.character_appearance.db import CharacterAppearanceDB
from models.mobile_suit_designer.db import MobileSuitDesignerDB
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.mobile_suit_pilot.db import MobileSuitPilotDB
from models.organization.db import OrganizationDB
from models.organization_appearance.db import OrganizationAppearanceDB


def seed_character_appearance(test_db_session: Session) -> None:
    character, work, source = CharacterDBFactory(), WorkDBFactory(), SourceDBFactory()
    test_db_session.flush()
    CharacterAppearanceDBFactory(
        character_id=character.id, source_id=source.id, work_id=work.id
    )


def seed_organization_appearance(test_db_session: Session) -> None:
    organization = OrganizationDBFactory()
    work, source = WorkDBFactory(), SourceDBFactory()
    test_db_session.flush()
    OrganizationAppearanceDBFactory(
        organization_id=organization.id, source_id=source.id, work_id=work.id
    )


def seed_pilot(test_db_session: Session) -> None:
    character, suit = CharacterDBFactory(), MobileSuitDBFactory()
    source = SourceDBFactory()
    test_db_session.flush()
    MobileSuitPilotDBFactory(
        character_id=character.id, mobile_suit_id=suit.id, source_id=source.id
    )


def seed_suit_organization(test_db_session: Session) -> None:
    organization, suit = OrganizationDBFactory(), MobileSuitDBFactory()
    source = SourceDBFactory()
    test_db_session.flush()
    MobileSuitOrganizationDBFactory(
        mobile_suit_id=suit.id, organization_id=organization.id, source_id=source.id
    )


def seed_suit_designer(test_db_session: Session) -> None:
    designer, suit = MechanicalDesignerDBFactory(), MobileSuitDBFactory()
    source = SourceDBFactory()
    test_db_session.flush()
    MobileSuitDesignerDBFactory(
        mechanical_designer_id=designer.id, mobile_suit_id=suit.id, source_id=source.id
    )


def seed_child_organization(test_db_session: Session) -> None:
    parent = OrganizationDBFactory(slug="earth-federation")
    test_db_session.flush()
    OrganizationDBFactory(parent_organization_id=parent.id, slug="titans")


@pytest.mark.parametrize(
    ("seed", "model", "relationship"),
    [
        (seed_character_appearance, CharacterAppearanceDB, "source"),
        (seed_character_appearance, CharacterAppearanceDB, "work"),
        (seed_organization_appearance, OrganizationAppearanceDB, "source"),
        (seed_organization_appearance, OrganizationAppearanceDB, "work"),
        (seed_pilot, MobileSuitPilotDB, "source"),
        (seed_suit_organization, MobileSuitOrganizationDB, "source"),
        (seed_suit_designer, MobileSuitDesignerDB, "source"),
        (seed_child_organization, OrganizationDB, "parent_organization"),
    ],
)
def test_an_unloaded_relationship_raises(
    test_db_session: Session,
    seed: Callable[[Session], None],
    model: type[RootDB],
    relationship: str,
) -> None:
    seed(test_db_session)
    test_db_session.commit()
    test_db_session.expunge_all()
    rows = test_db_session.scalars(select(model)).all()

    with pytest.raises(InvalidRequestError, match="lazy='raise'"):
        for row in rows:
            getattr(row, relationship)
