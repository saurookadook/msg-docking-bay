import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_script() -> ModuleType:
    # The file name has hyphens, so it cannot be imported by name.
    path = Path(__file__).resolve().parent.parent / "check-uv-lock-drift.py"
    spec = importlib.util.spec_from_file_location("check_uv_lock_drift", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = _load_script()


def _write_lock(path: Path, packages: list[tuple[str, str | None]]) -> Path:
    entries: list[str] = []
    for name, version in packages:
        entry = f'[[package]]\nname = "{name}"\n'
        if version is not None:
            entry += f'version = "{version}"\n'
        entries.append(entry)
    path.write_text("version = 1\n\n" + "\n".join(entries), encoding="utf-8")
    return path


@pytest.fixture
def backend_lock(tmp_path: Path) -> Path:
    return _write_lock(
        tmp_path / "backend.lock",
        [
            ("msg-docking-bay-backend", None),
            ("pydantic", "2.14.2"),
            ("sqlalchemy", "2.1.6"),
            ("uvicorn", "0.40.0"),
        ],
    )


class TestLockedVersions:
    def test_skips_the_projects_and_versionless_packages(self, tmp_path: Path) -> None:
        lock = _write_lock(
            tmp_path / "uv.lock",
            [
                ("msg-docking-bay-backend", "0.1.0"),
                ("msg-docking-bay-ingest", "0.1.0"),
                ("local-tool", None),
                ("sqlalchemy", "2.1.6"),
            ],
        )

        assert script.locked_versions(lock) == {"sqlalchemy": frozenset({"2.1.6"})}

    def test_keeps_every_version_of_a_forked_package(self, tmp_path: Path) -> None:
        lock = _write_lock(
            tmp_path / "uv.lock", [("numpy", "1.26.4"), ("numpy", "2.3.0")]
        )

        assert script.locked_versions(lock) == {"numpy": frozenset({"1.26.4", "2.3.0"})}

    def test_rejects_a_file_that_is_not_a_lockfile(self, tmp_path: Path) -> None:
        lock = tmp_path / "uv.lock"
        lock.write_text('[[package]]\nversion = "1.0"\n', encoding="utf-8")

        with pytest.raises(ValueError, match="name"):
            script.locked_versions(lock)


class TestFindDrift:
    def test_ignores_packages_only_one_side_holds(self) -> None:
        backend = {
            "fastapi": frozenset({"0.142.2"}),
            "sqlalchemy": frozenset({"2.1.6"}),
        }
        ingest = {
            "factory-boy": frozenset({"3.3.3"}),
            "sqlalchemy": frozenset({"2.1.6"}),
        }

        assert script.find_drift(backend, ingest) == []

    def test_reports_shared_packages_at_other_versions_by_name(self) -> None:
        backend = {"sqlalchemy": frozenset({"2.1.6"}), "alembic": frozenset({"1.20.1"})}
        ingest = {"sqlalchemy": frozenset({"2.1.5"}), "alembic": frozenset({"1.20.0"})}

        assert [d.name for d in script.find_drift(backend, ingest)] == [
            "alembic",
            "sqlalchemy",
        ]

    def test_reports_a_fork_that_differs_in_one_branch(self) -> None:
        """One version per name hid this: 2.0 matches, 1.x does not."""
        backend = {"numpy": frozenset({"1.0", "2.0"})}
        ingest = {"numpy": frozenset({"1.1", "2.0"})}

        [drift] = script.find_drift(backend, ingest)

        assert drift.forked


class TestRelockCommand:
    def test_pins_each_package_to_the_backends_version(self) -> None:
        drift = [
            script.Drift("alembic", frozenset({"1.20.1"}), frozenset({"1.20.0"})),
            script.Drift("sqlalchemy", frozenset({"2.1.6"}), frozenset({"2.1.5"})),
        ]

        assert script.relock_command(drift) == (
            "(cd ingest && uv lock -P alembic==1.20.1 -P sqlalchemy==2.1.6)"
        )

    def test_leaves_out_forked_packages(self) -> None:
        drift = [
            script.Drift("numpy", frozenset({"1.0", "2.0"}), frozenset({"1.1", "2.0"})),
            script.Drift("sqlalchemy", frozenset({"2.1.6"}), frozenset({"2.1.5"})),
        ]

        assert script.relock_command(drift) == (
            "(cd ingest && uv lock -P sqlalchemy==2.1.6)"
        )

    def test_returns_none_when_every_package_is_forked(self) -> None:
        drift = [
            script.Drift("numpy", frozenset({"1.0", "2.0"}), frozenset({"1.1", "2.0"}))
        ]

        assert script.relock_command(drift) is None


class TestMain:
    def test_matching_lockfiles_exit_0(
        self,
        tmp_path: Path,
        backend_lock: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        ingest_lock = _write_lock(
            tmp_path / "ingest.lock",
            [
                ("msg-docking-bay-ingest", None),
                ("pydantic", "2.14.2"),
                ("sqlalchemy", "2.1.6"),
            ],
        )

        status = script.main(
            ["--backend-lock", str(backend_lock), "--ingest-lock", str(ingest_lock)]
        )

        assert status == 0
        assert "matches backend/uv.lock on 2 shared packages" in capsys.readouterr().out

    def test_drift_exits_1_with_the_versions_and_the_fix(
        self,
        tmp_path: Path,
        backend_lock: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        ingest_lock = _write_lock(
            tmp_path / "ingest.lock", [("pydantic", "2.14.2"), ("sqlalchemy", "2.1.5")]
        )

        status = script.main(
            ["--backend-lock", str(backend_lock), "--ingest-lock", str(ingest_lock)]
        )

        err = capsys.readouterr().err
        assert status == 1
        assert "differs from backend/uv.lock on 1 package(s)" in err
        assert "sqlalchemy: backend 2.1.6, ingest 2.1.5\n" in err
        assert "(cd ingest && uv lock -P sqlalchemy==2.1.6)" in err

    def test_a_forked_drift_says_to_realign_by_hand(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        backend_lock = _write_lock(
            tmp_path / "backend.lock", [("numpy", "1.0"), ("numpy", "2.0")]
        )
        ingest_lock = _write_lock(
            tmp_path / "ingest.lock", [("numpy", "1.1"), ("numpy", "2.0")]
        )

        status = script.main(
            ["--backend-lock", str(backend_lock), "--ingest-lock", str(ingest_lock)]
        )

        err = capsys.readouterr().err
        assert status == 1
        assert (
            "numpy: backend 1.0, 2.0, ingest 1.1, 2.0"
            " (forked resolution: realign by hand)"
        ) in err
        assert "uv lock" not in err
