import uuid

from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.organization.db import OrganizationDBFactory
from _factories.source.db import SourceDBFactory
from constants.catalog import MobileSuitOrganizationRole
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.mobile_suit_organization.facade import MobileSuitOrganizationFacade

MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c2f000ff")


class TestMobileSuitOrganizationFacadeReads:
    def test_get_for_suit_with_no_organizations(self, test_db_session: Session) -> None:
        """An unknown suit has none; the caller owns the 404."""
        assert (
            MobileSuitOrganizationFacade(db_session=test_db_session).get_for_suit(
                MISSING_ID
            )
            == []
        )

    def test_get_links_for_suits_with_an_empty_page(
        self, test_db_session: Session
    ) -> None:
        """An empty page runs no query and has no links."""
        assert (
            MobileSuitOrganizationFacade(
                db_session=test_db_session
            ).get_links_for_suits([], link_filters=[])
            == {}
        )

    def test_get_links_for_suits_applies_the_filters(
        self, test_db_session: Session
    ) -> None:
        federation = OrganizationDBFactory()
        rx_78_2_gundam = MobileSuitDBFactory()
        source = SourceDBFactory()
        test_db_session.flush()
        for role in (
            MobileSuitOrganizationRole.MANUFACTURER,
            MobileSuitOrganizationRole.OPERATOR,
        ):
            test_db_session.add(
                MobileSuitOrganizationDB(
                    mobile_suit_id=rx_78_2_gundam.id,
                    organization_id=federation.id,
                    role=role,
                    source_id=source.id,
                )
            )
        test_db_session.commit()

        links = MobileSuitOrganizationFacade(
            db_session=test_db_session
        ).get_links_for_suits(
            [rx_78_2_gundam.id],
            link_filters=[
                MobileSuitOrganizationDB.role == MobileSuitOrganizationRole.OPERATOR
            ],
        )

        assert [link.role for link in links[rx_78_2_gundam.id]] == [
            MobileSuitOrganizationRole.OPERATOR
        ]


class TestMobileSuitOrganizationFacadeCreateOrUpdate:
    def test_keys_on_the_role(self, test_db_session: Session) -> None:
        """A rerun finds its link; another role is another link."""
        federation = OrganizationDBFactory()
        rx_78_2_gundam = MobileSuitDBFactory()
        source = SourceDBFactory()
        test_db_session.commit()
        facade = MobileSuitOrganizationFacade(db_session=test_db_session)
        payload = {
            "mobile_suit_id": rx_78_2_gundam.id,
            "organization_id": federation.id,
            "role": MobileSuitOrganizationRole.MANUFACTURER,
            "source_id": source.id,
            "work_id": None,
        }

        first = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload=payload)
        operator = facade.create_or_update(
            payload={**payload, "role": MobileSuitOrganizationRole.OPERATOR}
        )

        assert rerun.id == first.id
        assert operator.id != first.id
