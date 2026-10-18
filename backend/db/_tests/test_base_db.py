import pytest

from db.base_db import table_name_for


class TestTableNameFor:
    @pytest.mark.parametrize(
        "class_name, expected",
        [
            ("ProjectDB", "projects"),
            ("PropertyDB", "properties"),
            ("TaskStatusDB", "task_statuses"),
            ("BoxDB", "boxes"),
            ("ArticleBatchDB", "article_batches"),
            ("DayDB", "days"),
        ],
    )
    def test_derives_a_plural_snake_case_name(
        self, class_name: str, expected: str
    ) -> None:
        assert table_name_for(class_name) == expected
