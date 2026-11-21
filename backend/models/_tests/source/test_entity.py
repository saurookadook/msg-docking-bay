from datetime import UTC, datetime

import pytest

from constants.catalog import ContentLicense, SourceKind
from models.source.entity import SourceCitationEntity

RETRIEVED_AT = datetime(2026, 11, 15, 23, 32, 58, tzinfo=UTC)


def citation(
    kind: SourceKind, url: str, revision_id: int | None
) -> SourceCitationEntity:
    return SourceCitationEntity.model_validate(
        {
            "content_license": ContentLicense.CC_BY_SA_3_0,
            "kind": kind,
            "retrieved_at": RETRIEVED_AT,
            "revision_id": revision_id,
            "url": url,
        }
    )


class TestSourceCitationEntity:
    @pytest.mark.parametrize(
        ("kind", "url", "revision_url"),
        [
            (
                SourceKind.FANDOM_PAGE,
                "https://gundam.fandom.com/wiki/RX-78-2_Gundam",
                "https://gundam.fandom.com/wiki/RX-78-2_Gundam?oldid=706484",
            ),
            (
                SourceKind.FANDOM_PAGE,
                "https://gundam.fandom.com/?curid=2034",
                "https://gundam.fandom.com/?curid=2034&oldid=706484",
            ),
            (
                SourceKind.WIKIDATA_ITEM,
                "https://www.wikidata.org/wiki/Q1134906",
                "https://www.wikidata.org/w/index.php?title=Q1134906&oldid=706484",
            ),
            (
                SourceKind.WIKIPEDIA_EN_PAGE,
                "https://en.wikipedia.org/wiki/RX-78-2_Gundam",
                "https://en.wikipedia.org/wiki/RX-78-2_Gundam?oldid=706484",
            ),
            (
                SourceKind.WIKIPEDIA_JA_PAGE,
                "https://ja.wikipedia.org/wiki/Gundam",
                "https://ja.wikipedia.org/wiki/Gundam?oldid=706484",
            ),
        ],
    )
    def test_links_the_revision_for_each_kind(
        self, kind: SourceKind, url: str, revision_url: str
    ) -> None:
        assert citation(kind, url, 706484).revision_url == revision_url

    def test_has_no_revision_url_without_a_revision(self) -> None:
        source = citation(
            SourceKind.FANDOM_PAGE, "https://gundam.fandom.com/?curid=1", None
        )

        assert source.revision_url is None

    @pytest.mark.parametrize(
        ("content_license", "name", "url"),
        [
            (
                ContentLicense.CC_BY_SA_3_0,
                "CC BY-SA 3.0",
                "https://creativecommons.org/licenses/by-sa/3.0/",
            ),
            (
                ContentLicense.CC_BY_SA_4_0,
                "CC BY-SA 4.0",
                "https://creativecommons.org/licenses/by-sa/4.0/",
            ),
            (
                ContentLicense.CC0_1_0,
                "CC0 1.0",
                "https://creativecommons.org/publicdomain/zero/1.0/",
            ),
        ],
    )
    def test_names_and_links_its_license(
        self, content_license: ContentLicense, name: str, url: str
    ) -> None:
        source = citation(
            SourceKind.FANDOM_PAGE, "https://gundam.fandom.com/?curid=1", 1
        )
        source = source.model_copy(update={"content_license": content_license})

        assert (source.license_name, source.license_url) == (name, url)

    def test_serves_its_computed_fields(self) -> None:
        dumped = citation(
            SourceKind.FANDOM_PAGE, "https://gundam.fandom.com/?curid=1", 5
        ).model_dump()

        assert dumped["license_name"] == "CC BY-SA 3.0"
        assert dumped["revision_url"] == "https://gundam.fandom.com/?curid=1&oldid=5"
        assert "external_id" not in dumped
