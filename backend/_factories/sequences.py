"""Typed helpers for factory-boy sequences (PYTEST-11)."""

from factory.declarations import Sequence


def numbered(template: str) -> Sequence:
    """Return a sequence of ``template`` with ``{n}`` set to 0, 1, 2, …

    factory-boy leaves ``Sequence``'s function untyped, so a bare lambda
    fails pyright strict; this keeps factories free of suppressions.
    """

    def value(n: int) -> str:
        return template.format(n=n)

    return Sequence(value)
