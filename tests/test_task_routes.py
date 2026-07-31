from datetime import datetime

from extensions import db
from src.models.task import Task

TASK_FORM = {
    "title": "Estudiar ARP",
    "description": "Entender el protocolo",
    "start_date": "2026-07-01T09:00",
    "end_date": "2026-07-01T10:00",
    "task_type": "study",
    "color": "#007bff",
    "recurring": "n",
}


def _add_task(app, **overrides):
    task = Task(
        title="Tarea base",
        start_date=datetime(2026, 7, 1, 9, 0),
        end_date=datetime(2026, 7, 1, 10, 0),
        task_type="study",
    )
    for k, v in overrides.items():
        setattr(task, k, v)
    with app.app_context():
        db.session.add(task)
        db.session.commit()
        return task.id


class TestAddTask:
    def test_create_redirects_to_index(self, app, client):
        resp = client.post("/task/add", data=TASK_FORM)
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/")
        with app.app_context():
            assert Task.query.count() == 1
            assert Task.query.first().title == "Estudiar ARP"

    def test_missing_title_rejected(self, client):
        data = dict(TASK_FORM)
        data["title"] = ""
        resp = client.post("/task/add", data=data)
        assert resp.status_code == 200  # re-render del formulario con errores
        with client.application.app_context():
            assert Task.query.count() == 0

    def test_get_form(self, client):
        assert client.get("/task/add").status_code == 200


class TestEditTask:
    def test_edit_updates_fields(self, app, client):
        task_id = _add_task(app)
        data = dict(TASK_FORM)
        data["title"] = "Tarea renombrada"
        resp = client.post(f"/task/edit/{task_id}", data=data)
        assert resp.status_code == 302
        with app.app_context():
            assert Task.query.get(task_id).title == "Tarea renombrada"

    def test_edit_missing_404(self, client):
        assert client.get("/task/edit/9999").status_code == 404


class TestApiTasks:
    def test_list_returns_events(self, app, client):
        _add_task(app)
        resp = client.get("/task/api/tasks")
        assert resp.status_code == 200
        events = resp.get_json()
        assert len(events) == 1
        assert events[0]["title"] == "Tarea base"
        assert events[0]["start"] == "2026-07-01T09:00:00"

    def test_recurring_expands_events(self, app, client):
        _add_task(
            app,
            recurring=True,
            days_of_week="1,3",
            start_recur=datetime(2026, 7, 1),
            end_recur=datetime(2026, 7, 8),
        )
        resp = client.get("/task/api/tasks")
        events = resp.get_json()
        weekdays = [datetime.fromisoformat(e["start"]).weekday() for e in events]
        assert set(weekdays) == {1, 3}
        assert len(events) >= 2

    def test_pending_only(self, app, client):
        _add_task(app, completed=True)
        _add_task(app, completed=False)
        resp = client.get("/task/api/tasks/pending")
        tasks = resp.get_json()
        assert len(tasks) == 1
        assert tasks[0]["completed"] is False

    def test_update_dates(self, app, client):
        task_id = _add_task(app)
        resp = client.put(
            f"/task/api/tasks/{task_id}",
            json={
                "start": "2026-08-01T09:00:00",
                "end": "2026-08-01T10:30:00",
            },
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "success"
        with app.app_context():
            task = Task.query.get(task_id)
            assert task.start_date == datetime(2026, 8, 1, 9, 0)

    def test_update_invalid_date_returns_400(self, app, client):
        task_id = _add_task(app)
        resp = client.put(
            f"/task/api/tasks/{task_id}",
            json={"start": "no-es-fecha"},
        )
        assert resp.status_code == 400

    def test_update_missing_returns_404(self, client):
        resp = client.put("/task/api/tasks/9999", json={"start": "2026-08-01T09:00"})
        assert resp.status_code == 404


class TestTaskActions:
    def test_toggle_complete(self, app, client):
        task_id = _add_task(app)
        resp = client.post(f"/task/toggle/{task_id}")
        assert resp.status_code == 200
        with app.app_context():
            assert Task.query.get(task_id).completed is True

    def test_toggle_complete_json(self, app, client):
        task_id = _add_task(app)
        resp = client.post(f"/task/toggle/{task_id}")
        assert resp.status_code == 200
        assert resp.get_json()["completed"] is True
        with app.app_context():
            assert Task.query.get(task_id).completed is True

    def test_delete(self, app, client):
        task_id = _add_task(app)
        resp = client.post(f"/task/delete/{task_id}")
        assert resp.status_code == 302
        with app.app_context():
            assert Task.query.count() == 0

    def test_delete_missing_404(self, client):
        assert client.post("/task/delete/9999").status_code == 404
