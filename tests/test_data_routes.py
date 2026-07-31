import os

import pytest

from extensions import db
from src.models.checklist import Objective
from src.models.glossary import Term
from src.models.theory import Theory

DATA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_THEORY = os.path.join(
    "data",
    "theory",
    "Conceptos_básicos_de_redes",
    "Módulo_10_Formatos_y_reglas_de_direccionamiento_IPv6.md",
)
SAMPLE_IMG = os.path.join(
    "data",
    "theory",
    "Conceptos_básicos_de_redes",
    "img",
    "Pasted image 20250707153354.png",
)


@pytest.fixture()
def term(app):
    with app.app_context():
        t = Term(term="HTTP", translation="Protocolo", description="Hypertext")
        db.session.add(t)
        db.session.commit()
        yield t


class TestGlosario:
    def test_list(self, app, client, term):
        resp = client.get("/data/glosario")
        assert resp.status_code == 200
        assert b"HTTP" in resp.data

    def test_add_term(self, client):
        resp = client.post(
            "/data/add_term",
            data={
                "term": "TCP",
                "translation": "Protocolo",
                "description": "Transmisión",
            },
        )
        assert resp.status_code == 302
        with client.application.app_context():
            assert Term.query.filter_by(term="TCP").count() == 1

    def test_add_duplicate_rejected(self, app, client, term):
        resp = client.post(
            "/data/add_term",
            data={"term": "HTTP", "translation": "X", "description": ""},
        )
        assert resp.status_code == 200  # re-render con error de validación
        assert "ya existe" in resp.get_data(as_text=True)

    def test_add_invalid_chars_rejected(self, client):
        resp = client.post(
            "/data/add_term",
            data={"term": "HTTP/2<>", "translation": "X", "description": ""},
        )
        assert resp.status_code == 200
        assert "solo puede contener" in resp.get_data(as_text=True)

    def test_edit_term_same_name_ok(self, app, client, term):
        # Regresión: antes rechazaba como duplicado al editar sin cambiar el nombre
        resp = client.post(
            f"/data/edit_term/{term.id}",
            data={"term": "HTTP", "translation": "Protocolo", "description": "nueva"},
        )
        assert resp.status_code == 302
        with app.app_context():
            assert Term.query.get(term.id).description == "nueva"

    def test_edit_term_to_duplicate_rejected(self, app, client, term):
        with app.app_context():
            db.session.add(Term(term="OTRO", translation="X"))
            db.session.commit()
        resp = client.post(
            f"/data/edit_term/{term.id}",
            data={"term": "OTRO", "translation": "X", "description": ""},
        )
        assert resp.status_code == 200
        assert "ya existe" in resp.get_data(as_text=True)

    def test_delete_term(self, app, client, term):
        resp = client.post(f"/data/delete_term/{term.id}")
        assert resp.status_code == 302
        with app.app_context():
            assert Term.query.count() == 0


class TestChecklist:
    def test_list_empty(self, client):
        assert client.get("/data/checklist").status_code == 200

    def test_add_objective(self, client):
        resp = client.post(
            "/data/add_objective",
            data={
                "objective": "Aprender TCP",
                "methodology": "CTF",
                "description": "",
                "status": "Pendiente",
            },
        )
        assert resp.status_code == 302
        with client.application.app_context():
            assert Objective.query.filter_by(objective="Aprender TCP").count() == 1

    def test_edit_objective(self, app, client):
        with app.app_context():
            obj = Objective(objective="Viejo", methodology="Leer")
            db.session.add(obj)
            db.session.commit()
            obj_id = obj.id
        resp = client.post(
            f"/data/edit_objective/{obj_id}",
            data={
                "objective": "Nuevo",
                "methodology": "Leer",
                "description": "",
                "status": "En Progreso",
            },
        )
        assert resp.status_code == 302
        with app.app_context():
            assert Objective.query.get(obj_id).objective == "Nuevo"
            assert Objective.query.get(obj_id).status == "En Progreso"

    def test_delete_objective(self, app, client):
        with app.app_context():
            obj = Objective(objective="Objetivo", methodology="M")
            db.session.add(obj)
            db.session.commit()
            obj_id = obj.id
        resp = client.post(f"/data/delete_objective/{obj_id}")
        assert resp.status_code == 302
        with app.app_context():
            assert Objective.query.count() == 0


class TestSearch:
    def test_search_indexes_terms(self, app, client, term):
        resp = client.get("/data/search?q=HTTP")
        assert resp.status_code == 200
        assert b"HTTP" in resp.data

    def test_search_empty_query(self, client):
        assert client.get("/data/search?q=").status_code == 200


class TestTheoryPages:
    def test_list(self, client):
        assert client.get("/data/theory").status_code == 200

    def test_list_scripts(self, client):
        assert client.get("/data/scripts").status_code == 200

    def test_list_writeups(self, client):
        assert client.get("/data/writeups").status_code == 200

    def test_view_theory(self, app, client):
        if not os.path.exists(SAMPLE_THEORY):
            pytest.skip("no hay contenido real de data/theory")
        with app.app_context():
            theory = Theory(
                title="Módulo_10",
                file_path=SAMPLE_THEORY,
                category="Conceptos_básicos_de_redes",
            )
            db.session.add(theory)
            db.session.commit()
            theory_id = theory.id
        resp = client.get(f"/data/theory/{theory_id}")
        assert resp.status_code == 200
        assert b"markdown-image" in resp.data or b"<img" in resp.data

    def test_view_theory_missing_file(self, app, client):
        with app.app_context():
            theory = Theory(title="Fantasma", file_path="/no/existe.md", category="x")
            db.session.add(theory)
            db.session.commit()
            theory_id = theory.id
        assert client.get(f"/data/theory/{theory_id}").status_code == 404


class TestViewImage:
    def test_traversal_rejected(self, client):
        attempts = [
            "/data/view_image/../../etc/passwd/x.png",
            "/data/view_image/theory/Conceptos_b%C3%A1sicos_de_redes/..%2f..%2f..%2f..%2fetc%2fpasswd",
            "/data/view_image/theory/Conceptos_b%C3%A1sicos_de_redes/%2e%2e/%2e%2e/hacker-panel.db",
        ]
        for path in attempts:
            resp = client.get(path)
            assert resp.status_code in (400, 404)
            assert resp.headers.get("Content-Type", "").startswith("text/html")

    def test_invalid_dirname_rejected(self, client):
        resp = client.get(
            "/data/view_image/teoria/Conceptos_b%C3%A1sicos_de_redes/x.png"
        )
        assert resp.status_code in (400, 404)

    def test_serves_real_image(self, app, client):
        if not os.path.exists(SAMPLE_IMG):
            pytest.skip("no hay imágenes reales en data/theory")
        resp = client.get(
            "/data/view_image/theory/Conceptos_b%C3%A1sicos_de_redes/"
            "Pasted%20image%2020250707153354.png"
        )
        assert resp.status_code == 200
        assert resp.headers["Content-Type"] == "image/png"

    def test_missing_image_404(self, client):
        resp = client.get(
            "/data/view_image/theory/Conceptos_b%C3%A1sicos_de_redes/no_existe.png"
        )
        assert resp.status_code == 404
