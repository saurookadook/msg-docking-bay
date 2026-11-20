import json
from pathlib import Path

from scripts.export_openapi import main


class TestMain:
    def test_writes_the_schema_with_sorted_keys(self, tmp_path: Path) -> None:
        output = tmp_path / "generated" / "openapi.json"

        exit_code = main([str(output)])

        assert exit_code == 0
        text = output.read_text(encoding="utf-8")
        assert text.endswith("}\n")
        schema = json.loads(text)
        assert list(schema) == sorted(schema)
        assert (
            schema["paths"]["/api/health-check"]["get"]["operationId"]
            == "read_health_check"
        )

    def test_output_is_identical_across_runs(self, tmp_path: Path) -> None:
        """The CI drift check compares a fresh export with the committed
        one, so the same app must always produce the same bytes.
        """
        first = tmp_path / "first.json"
        second = tmp_path / "second.json"

        main([str(first)])
        main([str(second)])

        assert first.read_bytes() == second.read_bytes()
