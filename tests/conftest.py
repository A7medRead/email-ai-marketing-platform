import os

# Must run before any `app` import: isolate from the real .env / production secrets.
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["ENCRYPTION_KEY"] = "BIHh9QLNMXtNBFcMT6hwoVVOgj38CuA048YT8meyNGA="
os.environ["ALGORITHM"] = "HS256"
os.environ["TRACKING_URL"] = "http://tracking.test"

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.features.model_registry  # noqa: F401  (registers all ORM models)
from app.core.config import ALGORITHM, SECRET_KEY
from app.infrastructure.database import Base, get_db
from app.infrastructure.email import smtp as smtp_module
from app.main import app as fastapi_app
from tests.factories import Scenario, make_user
from tests.helpers.fake_smtp import FakeSMTPController, make_fake_smtp_class


@pytest.fixture
def engine(tmp_path):
    """Fresh file-based SQLite database per test (same engine type as production)."""
    eng = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db(session_factory):
    session = session_factory()
    yield session
    session.close()


@pytest.fixture
def smtp(monkeypatch):
    """Replace smtplib.SMTP used by the app's SMTP layer. No real mail is ever sent."""
    ctl = FakeSMTPController()
    monkeypatch.setattr(smtp_module.smtplib, "SMTP", make_fake_smtp_class(ctl))
    return ctl


@pytest.fixture
def client(session_factory, smtp):
    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


def auth_for(user):
    token = jwt.encode({"sub": str(user.id)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def scenario(db):
    return Scenario(db)


@pytest.fixture
def headers(scenario):
    return auth_for(scenario.user)


@pytest.fixture
def make_headers():
    return auth_for


@pytest.fixture
def other_user(db):
    return make_user(db, email="other@example.com")
