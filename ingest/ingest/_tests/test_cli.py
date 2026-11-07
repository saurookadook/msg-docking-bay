from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from _factories.ingest_run.db import IngestRunDBFactory
from constants.catalog import IngestRunStatus, SourceKind
from ingest.cli import main
from ingest.runs import SessionFactory
from ingest.schema import MIGRATE_HINT, expected_heads

WATERMARK = datetime(2025, 9, 1, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def wide_console(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep rich from truncating table cells in captured output."""
    monkeypatch.setenv("COLUMNS", "200")


class TestStatus:
    def test_lists_every_source_kind_before_any_run(
        self, run_sessions: SessionFactory, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main(["status"], session_factory=run_sessions) == 0

        out = capsys.readouterr().out
        assert f"Schema at head: {expected_heads()[0]}" in out
        for kind in SourceKind:
            assert kind.value in out
        assert out.count("never") == len(SourceKind)

    def test_shows_the_latest_run_and_the_last_succeeded_watermark(
        self,
        test_db_session: Session,
        mock_utcnow: datetime,
        run_sessions: SessionFactory,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        IngestRunDBFactory(
            finished_at=mock_utcnow,
            status=IngestRunStatus.SUCCEEDED,
            watermark_at=WATERMARK,
        )
        IngestRunDBFactory(
            error_summary="ValueError",
            finished_at=mock_utcnow,
            status=IngestRunStatus.FAILED,
        )
        test_db_session.commit()

        assert main(["status"], session_factory=run_sessions) == 0

        [fandom_row] = [
            line
            for line in capsys.readouterr().out.splitlines()
            if SourceKind.FANDOM_PAGE.value in line
        ]
        assert "failed (ValueError)" in fandom_row
        assert WATERMARK.isoformat(timespec="seconds") in fandom_row

    def test_folds_rather_than_truncates_on_an_80_column_console(
        self,
        test_db_session: Session,
        mock_utcnow: datetime,
        run_sessions: SessionFactory,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A pipe or a container without a TTY gets 80 columns."""
        monkeypatch.setenv("COLUMNS", "80")
        IngestRunDBFactory(
            error_summary="23514 ck_ingest_runs_pages_seen_not_negative",
            finished_at=mock_utcnow,
            status=IngestRunStatus.FAILED,
            watermark_at=WATERMARK,
        )
        test_db_session.commit()

        assert main(["status"], session_factory=run_sessions) == 0

        out = capsys.readouterr().out
        assert "…" not in out
        assert max(len(line) for line in out.splitlines()) <= 80
        for kind in SourceKind:
            assert kind.value in out

    def test_exits_1_with_the_fix_when_the_schema_is_not_at_head(
        self,
        run_sessions: SessionFactory,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        monkeypatch.setattr("ingest.schema.expected_heads", lambda: ["3333aaaa3333"])

        assert main(["status"], session_factory=run_sessions) == 1

        assert MIGRATE_HINT in caplog.text
        assert "Traceback" not in caplog.text


class TestUsage:
    def test_exits_2_without_a_command(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main([])

        assert exc_info.value.code == 2
        assert "required: command" in capsys.readouterr().err

    def test_lists_the_registered_commands_in_help(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])

        assert exc_info.value.code == 0
        assert "status" in capsys.readouterr().out
