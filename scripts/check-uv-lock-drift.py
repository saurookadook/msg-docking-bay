"""Check that ingest locks shared packages at the backend's versions.

ingest installs the backend as a path dependency and runs its code, so
the two lockfiles must agree on every package both hold; Dependabot
updates them in separate PRs, so they drift. ``backend/uv.lock`` is the
source of truth: on drift this prints the ``uv lock`` command that moves
ingest back to the backend's versions, and exits 1.

Run it with ``moon run ingest:lock-drift``, in ingest's environment
(for Pydantic).
"""

import argparse
import shlex
import sys
import tomllib
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
    backend_version: str
    ingest_version: str


def locked_versions(lockfile: Path) -> dict[str, str]:
    """Return each locked package's version, keyed by name.

    Raises:
        pydantic.ValidationError: The file is not a uv lockfile.
    """
    with lockfile.open("rb") as file:
        lock = Lockfile.model_validate(tomllib.load(file))
    return {
        package.name: package.version
        for package in lock.package
        if package.version is not None and package.name not in OWN_PACKAGES
    }


def find_drift(backend: Mapping[str, str], ingest: Mapping[str, str]) -> list[Drift]:
    """Return the shared packages whose versions differ; pure."""
    return [
        Drift(name, backend[name], ingest[name])
        for name in sorted(backend.keys() & ingest.keys())
        if backend[name] != ingest[name]
    ]


def relock_command(drift: Sequence[Drift]) -> str:
    """Return the ``uv lock`` command that realigns ingest."""
    pins = " ".join(
        f"-P {shlex.quote(f'{d.name}=={d.backend_version}')}" for d in drift
    )
    return f"(cd ingest && uv lock {pins})"


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
        print(
            f"  {d.name}: backend {d.backend_version}, ingest {d.ingest_version}",
            file=sys.stderr,
        )
    print(
        "\nThe backend's versions win. If the backend should move instead,"
        " update backend/uv.lock first. To realign ingest, run:\n\n"
        f"  {relock_command(drift)}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
