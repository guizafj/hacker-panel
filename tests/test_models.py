from datetime import datetime

import pytest

from extensions import db
from src.models.checklist import Objective
from src.models.glossary import Term
from src.models.task import Task


@pytest.fixture()
def term(app):
    with app.app_context():
        t = Term(term="HTTP", translation="Protocolo", description="Hypertext")
        db.session.add(t)
        db.session.commit()
        yield t


class TestTermValidarTerm:
    def test_valido(self, app):
        with app.app_context():
            assert Term.validar_term("IP Address") == "IP Address"

    def test_vacio_rechazado(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                Term.validar_term("   ")

    def test_caracteres_invalidos(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                Term.validar_term("HTTP/2<>")

    def test_duplicado_rechazado(self, app, term):
        with app.app_context():
            with pytest.raises(ValueError):
                Term.validar_term("HTTP")

    def test_mismo_registro_al_editar_no_rechaza(self, app, term):
        with app.app_context():
            assert Term.validar_term("HTTP", term_id=term.id) == "HTTP"


class TestTask:
    def test_to_dict_serializes(self, app):
        with app.app_context():
            task = Task(
                title="Estudiar",
                start_date=datetime(2026, 7, 1, 9, 0),
                end_date=datetime(2026, 7, 1, 10, 0),
                task_type="study",
                color="#007bff",
                completed=True,
            )
            data = task.to_dict()
            assert data["title"] == "Estudiar"
            assert data["type"] == "study"
            assert data["start"] == "2026-07-01T09:00:00"
            assert data["completed"] is True
            assert data["color"] == "#28a745"

    def test_to_dict_null_dates(self, app):
        with app.app_context():
            task = Task(title="Sin fechas")
            data = task.to_dict()
            assert data["start"] is None
            assert data["end"] is None


class TestObjective:
    def test_to_dict_serializes_date_target(self, app):
        with app.app_context():
            obj = Objective(
                objective="Aprender TCP",
                methodology="CTF",
                date_target=datetime(2026, 8, 15),
                status="En Progreso",
            )
            data = obj.to_dict()
            assert data["objective"] == "Aprender TCP"
            assert data["date_target"] == "2026-08-15T00:00:00"
            assert data["status"] == "En Progreso"

    def test_to_dict_null_date(self, app):
        with app.app_context():
            obj = Objective(objective="Sin fecha", methodology="Leer")
            assert obj.to_dict()["date_target"] is None
