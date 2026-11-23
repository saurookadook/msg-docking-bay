from models.spec_sheet.entity import SPEC_SHEET_PART_KINDS, MobileSuitSpecSheetEntity


class TestMobileSuitSpecSheetEntity:
    def test_has_a_field_for_every_part_kind(self) -> None:
        """Entities ignore unknown keys, so a kind with no field would
        drop its listings from the response without an error.
        """
        fields = MobileSuitSpecSheetEntity.model_fields

        assert [kind for kind in SPEC_SHEET_PART_KINDS if kind not in fields] == []
