"""The catalog search's results and totals (catalog-search.md Q1)."""

from pydantic import BaseModel

from models.base.entity import BaseEntityModel
from models.character.entity import CharacterCardEntity
from models.mechanical_designer.entity import MechanicalDesignerCardEntity
from models.mobile_suit.entity import MobileSuitCardEntity
from models.organization.entity import OrganizationCardEntity
from models.work.entity import WorkCardEntity


class CatalogSearchResultsEntity(BaseEntityModel):
    """The top cards of each kind that match a search.

    Each list holds the kind's own cards, in its list order behind the
    prefix rank (D8), so a result renders as it would in its list.
    """

    characters: list[CharacterCardEntity]
    mechanical_designers: list[MechanicalDesignerCardEntity]
    mobile_suits: list[MobileSuitCardEntity]
    organizations: list[OrganizationCardEntity]
    works: list[WorkCardEntity]


class CatalogSearchTotals(BaseModel):
    """How many rows of each kind match, across every page.

    A plain model, like ``PageMeta``, so its fields stay ``snake_case``.
    """

    characters: int
    mechanical_designers: int
    mobile_suits: int
    organizations: int
    works: int


class CatalogSearch(BaseModel):
    """Return the facade's results and totals, as ``Page`` does.

    The route turns it into ``data`` and ``meta`` (fastapi.md FAPI-12).
    """

    results: CatalogSearchResultsEntity
    totals: CatalogSearchTotals
