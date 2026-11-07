"""Check that ingest locks shared packages at the backend's versions.

ingest installs the backend as a path dependency and runs its code, so
the two lockfiles must agree on every package both hold; Dependabot
updates them in separate PRs, so they drift. ``backend/uv.lock`` is the
source of truth: on drift this prints the ``uv lock`` command that moves
ingest back to the backend's versions, and exits 1.

Run it with ``moon run ingest:lock-drift``, in ingest's environment
(for Pydantic). Its tests are in ``scripts/_tests/``.
"""

import argparse
import shlex
import sys
import tomllib
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, NamedTuple

from pydantic import BaseModel

DESCRIPTION: Final = (
    "Check that ingest locks shared packages at the backend's versions."
)

REPO_ROOT: Final = Path(__file__).resolve().parent.parent

OWN_PACKAGES: Final = frozenset({"msg-docking-bay-backend", "msg-docking-bay-ingest"})
"""The projects themselves: path packages, not pinned dependencies."""


class LockedPackage(BaseModel):
    """One ``[[package]]`` entry; other keys are ignored."""

    name: str
    version: str | None = None
    """Missing for a path or workspace package."""


class Lockfile(BaseModel):
    """The part of a ``uv.lock`` this check reads."""

    package: list[LockedPackage]


class Drift(NamedTuple):
    """A package both lockfiles hold, at different versions."""

    name: str
    backend_versions: frozenset[str]
    ingest_versions: frozenset[str]

    @property
    def forked(self) -> bool:
        """Whether either lockfile holds several versions of it.

        A forked resolution locks one version per set of markers (a
        platform, a Python version); a ``-P`` pin cannot say which
        version goes with which markers, so it is realigned by hand.
        """
        return len(self.backend_versions) > 1 or len(self.ingest_versions) > 1


def locked_versions(lockfile: Path) -> dict[str, frozenset[str]]:
    """Return every version locked for each package, keyed by name.

    A name maps to several versions when uv forked the resolution.

    Raises:
        pydantic.ValidationError: The file is not a uv lockfile.
    """
    with lockfile.open("rb") as file:
        lock = Lockfile.model_validate(tomllib.load(file))
    versions: defaultdict[str, set[str]] = defaultdict(set)
    for package in lock.package:
        if package.version is not None and package.name not in OWN_PACKAGES:
            versions[package.name].add(package.version)
    return {name: frozenset(found) for name, found in versions.items()}


def find_drift(
    backend: Mapping[str, frozenset[str]], ingest: Mapping[str, frozenset[str]]
) -> list[Drift]:
    """Return the shared packages whose versions differ; pure."""
    return [
        Drift(name, backend[name], ingest[name])
        for name in sorted(backend.keys() & ingest.keys())
        if backend[name] != ingest[name]
    ]


def relock_command(drift: Sequence[Drift]) -> str | None:
    """Return the ``uv lock`` command that realigns ingest.

    Forked packages are left out (see ``Drift.forked``); ``None`` when
    every drifted package is forked.
    """
    pins = [
        f"-P {shlex.quote(f'{d.name}=={next(iter(d.backend_versions))}')}"
        for d in drift
        if not d.forked
    ]
    if not pins:
        return None
    return f"(cd ingest && uv lock {' '.join(pins)})"


def main(argv: Sequence[str] | None = None) -> int:
    """Compare the lockfiles; return 0 when they agree, 1 on drift."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--backend-lock", type=Path, default=REPO_ROOT / "backend" / "uv.lock"
    )
    parser.add_argument(
        "--ingest-lock", type=Path, default=REPO_ROOT / "ingest" / "uv.lock"
    )
    args = parser.parse_args(argv)

    backend = locked_versions(args.backend_lock)
    ingest = locked_versions(args.ingest_lock)
    drift = find_drift(backend, ingest)
    if not drift:
        shared = len(backend.keys() & ingest.keys())
        print(f"ingest/uv.lock matches backend/uv.lock on {shared} shared packages.")
        return 0

    print(
        f"ingest/uv.lock differs from backend/uv.lock on {len(drift)} package(s):",
        file=sys.stderr,
    )
    for d in drift:
        note = " (forked resolution: realign by hand)" if d.forked else ""
        print(
            f"  {d.name}: backend {_join(d.backend_versions)},"
            f" ingest {_join(d.ingest_versions)}{note}",
            file=sys.stderr,
        )
    print(
        "\nThe backend's versions win. If the backend should move instead,"
        " update backend/uv.lock first.",
        file=sys.stderr,
    )
    command = relock_command(drift)
    if command is not None:
        print(f"To realign ingest, run:\n\n  {command}", file=sys.stderr)
    return 1


def _join(versions: frozenset[str]) -> str:
    """Return the versions, sorted, as one string."""
    return ", ".join(sorted(versions))


if __name__ == "__main__":
    sys.exit(main())
