# pyright: reportIncompatibleVariableOverride=false
from dataclasses import dataclass
from datetime import datetime

from _factories.base_meta import BaseMetaFactory
from _factories.mixins.timestamps import TimestampsDBMixinFactory
from _mocks.temporal import get_mock_utcnow


@dataclass
class Stamped:
    created_at: datetime
    name: str
    updated_at: datetime


class StampedFactory(TimestampsDBMixinFactory, metaclass=BaseMetaFactory[Stamped]):
    class Meta:
        model = Stamped

    name = "MS-06F Zaku II"


class TestBaseMetaFactory:
    def test_calling_the_factory_returns_an_instance_of_its_model(self) -> None:
        stamped = StampedFactory()

        assert isinstance(stamped, Stamped)
        assert stamped.name == "MS-06F Zaku II"

    def test_keyword_arguments_override_declarations(self) -> None:
        stamped = StampedFactory(name="RGM-79 GM")

        assert stamped.name == "RGM-79 GM"


class TestTimestampsDBMixinFactory:
    def test_sets_both_timestamps_to_the_fixed_instant(self) -> None:
        stamped = StampedFactory()

        assert stamped.created_at == get_mock_utcnow()
        assert stamped.updated_at == get_mock_utcnow()
