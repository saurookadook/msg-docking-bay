"""The typed metaclass every model factory uses (PYTEST-11)."""

from typing import Any, cast, override

from factory.base import FactoryMetaClass


class BaseMetaFactory[T](FactoryMetaClass):
    """Type a factory call as the model it builds.

    With ``metaclass=BaseMetaFactory[ProjectDB]``, pyright types
    ``ProjectDBFactory(...)`` as a ``ProjectDB``; factory-boy's own
    metaclass leaves the result unknown.
    """

    @override
    def __call__(cls, **kwargs: Any) -> T:  # noqa: N805 - a metaclass method receives the class
        """Build or create one instance with the factory's strategy."""
        # factory-boy leaves FactoryMetaClass.__call__ unannotated.
        return cast(T, super().__call__(**kwargs))  # pyright: ignore[reportUnknownMemberType]
