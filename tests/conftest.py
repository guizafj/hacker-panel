import pytest

from app import app as flask_app
from extensions import db
from src.utils.search_utils import initialize_search_index


@pytest.fixture()
def app(tmp_path):
    """App de Flask con BD SQLite temporal y CSRF desactivado."""
    db_path = tmp_path / "test.db"
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with flask_app.app_context():
        db.create_all()
        initialize_search_index(flask_app)

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
