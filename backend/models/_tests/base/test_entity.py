from models.base.entity import BaseEntityModel


class OptionalNameEntity(BaseEntityModel):
    name: str | None = None


class TestBaseEntityModel:
    def test_lists_defaulted_fields_as_required_in_the_response_schema(self) -> None:
        """The API always sends the key, so it is never optional."""
        schema = OptionalNameEntity.model_json_schema(mode="serialization")

        assert schema["required"] == ["name"]

    def test_keeps_defaulted_fields_optional_for_validation(self) -> None:
        schema = OptionalNameEntity.model_json_schema(mode="validation")

        assert "required" not in schema

    def test_validates_from_attributes(self) -> None:
        class Row:
            name = "RX-78-2 Gundam"

        assert OptionalNameEntity.model_validate(Row()).name == "RX-78-2 Gundam"
