# pyright: reportIncompatibleVariableOverride=false
"""Factory declarations for the timestamp mixins (PYTEST-11)."""

from typing import Any

# Imported from their defining modules: factory-boy's package root does
# not declare its re-exports, so pyright treats them as private.
from factory.base import Factory
from factory.declarations import LazyFunction

from _mocks.temporal import get_mock_utcnow


class CreatedAtDBMixinFactory(Factory[Any]):
    """Set ``created_at`` to the fixed instant, for junction tables."""

    class Meta:
        abstract = True

    created_at = LazyFunction(get_mock_utcnow)


class TimestampsDBMixinFactory(CreatedAtDBMixinFactory):
    """Set ``created_at`` and ``updated_at`` to the fixed instant.

    List it before ``SQLAlchemyModelFactory`` in a model factory's
    bases, so its declarations apply (PYTEST-11).
    """

    class Meta:
        abstract = True

    updated_at = LazyFunction(get_mock_utcnow)
