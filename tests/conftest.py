import os

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/tableturn_test"
)

from app.core.rate_limit import limiter

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session

from app.main import app
from app.db.database import engine


@pytest.fixture
def client():
    with Session(engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(table.delete())
        session.commit()

    limiter.reset()

    return TestClient(app)