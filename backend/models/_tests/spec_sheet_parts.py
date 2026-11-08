"""Setup shared by the four spec sheet part junction tests."""

import uuid
from typing import Final

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from db.base_db import RootDB

SUIT_ID: Final = uuid.UUID("019a1984-0750-7142-aedd-75295bd10001")
SOURCE_ID: Final = uuid.UUID("019a1984-0750-7142-aedd-75295bd10002")
SHEET_ID: Final = uuid.UUID("019a1984-0750-7142-aedd-75295bd10003")


def seed_sheet(test_db_session: Session) -> None:
    """Add the suit, source and sheet a part listing hangs from."""
    MobileSuitDBFactory(id=SUIT_ID)
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.flush()
    SpecSheetDBFactory(id=SHEET_ID, mobile_suit_id=SUIT_ID, source_id=SOURCE_ID)


def row_count(test_db_session: Session, model: type[RootDB]) -> int:
    """Count a table's rows, as ``SELECT count(*)`` would."""
    return test_db_session.execute(select(func.count()).select_from(model)).scalar_one()
