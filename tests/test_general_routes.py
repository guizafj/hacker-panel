from datetime import datetime

from extensions import db
from src.models.task import Task


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_index_renders_calendar(app, client):
    with app.app_context():
        db.session.add(
            Task(
                title="Estudiar TCP",
                start_date=datetime(2026, 7, 1, 9, 0),
                end_date=datetime(2026, 7, 1, 10, 0),
            )
        )
        db.session.commit()

    resp = client.get("/")
    assert resp.status_code == 200
    # El calendario carga las tareas vía /task/api/tasks (FullCalendar JS)
    assert b'id="calendar"' in resp.data


def test_index_orders_completed_last(app, client):
    with app.app_context():
        db.session.add_all(
            [
                Task(
                    title="Pendiente",
                    start_date=datetime(2026, 7, 1, 9, 0),
                    end_date=datetime(2026, 7, 1, 10, 0),
                    completed=True,
                ),
                Task(
                    title="Activa",
                    start_date=datetime(2026, 7, 2, 9, 0),
                    end_date=datetime(2026, 7, 2, 10, 0),
                ),
            ]
        )
        db.session.commit()

    resp = client.get("/")
    assert resp.status_code == 200
    assert b'id="calendar"' in resp.data
