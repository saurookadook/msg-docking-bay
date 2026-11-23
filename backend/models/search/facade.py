"""Search every catalog kind at once (catalog-search.md Q2)."""

from models.base.facade import BaseFacade
from models.character.facade import CharacterFacade
from models.mechanical_designer.facade import MechanicalDesignerFacade
from models.mobile_suit.facade import MobileSuitFacade
from models.organization.facade import OrganizationFacade
from models.search.entity import (
    CatalogSearch,
    CatalogSearchResultsEntity,
    CatalogSearchTotals,
)
from models.work.facade import WorkFacade


class CatalogSearchFacade(BaseFacade):
    """Run one ``q`` through each kind's list, on one session.

    It owns no table: each kind's facade keeps its own matching, so a
    search finds what that kind's list finds for the same ``q``.
    """

    def search(self, *, q: str | None, limit: int) -> CatalogSearch:
        """Return the first ``limit`` matches of each kind, and totals.

        ``q`` matches as each list's ``q`` does (D8): normalized, prefix
        matches first, and a blank ``q`` is no filter, so it returns
        the first rows of each list (Q4). Ten statements, whatever
        ``q`` is: a page and a count per kind.
        """
        session = self.db_session
        mobile_suits = MobileSuitFacade(db_session=session).get_page(
            q=q, limit=limit, offset=0
        )
        characters = CharacterFacade(db_session=session).get_page(
            q=q, limit=limit, offset=0
        )
        organizations = OrganizationFacade(db_session=session).get_page(
            q=q, limit=limit, offset=0
        )
        mechanical_designers = MechanicalDesignerFacade(db_session=session).get_page(
            q=q, limit=limit, offset=0
        )
        works = WorkFacade(db_session=session).get_page(q=q, limit=limit, offset=0)
        return CatalogSearch(
            results=CatalogSearchResultsEntity(
                characters=characters.items,
                mechanical_designers=mechanical_designers.items,
                mobile_suits=mobile_suits.items,
                organizations=organizations.items,
                works=works.items,
            ),
            totals=CatalogSearchTotals(
                characters=characters.total,
                mechanical_designers=mechanical_designers.total,
                mobile_suits=mobile_suits.total,
                organizations=organizations.total,
                works=works.total,
            ),
        )
