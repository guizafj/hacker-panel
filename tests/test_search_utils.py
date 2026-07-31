import pytest

from extensions import db
from src.models.theory import Theory
from src.utils.search_utils import (
    _compute_hash,
    index_file_entry,
    remove_from_index,
    search_fts,
)


@pytest.fixture()
def theory_entry(app, tmp_path):
    md_file = tmp_path / "modulo_test.md"
    md_file.write_text("# Redes\n\nEl router funciona por IP.\n", encoding="utf-8")

    with app.app_context():
        entry = Theory(
            title="modulo_test",
            file_path=str(md_file),
            category="test",
        )
        db.session.add(entry)
        db.session.flush()
        db.session.commit()
        yield entry


class TestHash:
    def test_deterministic(self):
        assert _compute_hash("hola") == _compute_hash("hola")

    def test_different_content(self):
        assert _compute_hash("hola") != _compute_hash("hola ")


class TestIndexFileEntry:
    def test_indexes_new_entry(self, app, theory_entry):
        with app.app_context():
            assert theory_entry.content_hash is None
            reindexed = index_file_entry(app, theory_entry, "theory")
            assert reindexed is True
            assert theory_entry.content_hash is not None
            db.session.commit()

    def test_skips_unchanged(self, app, theory_entry):
        with app.app_context():
            index_file_entry(app, theory_entry, "theory")
            db.session.commit()
            assert index_file_entry(app, theory_entry, "theory") is False

    def test_missing_file_no_crash(self, app):
        with app.app_context():
            entry = Theory(title="fantasma", file_path="/no/existe.md")
            assert index_file_entry(app, entry, "theory") is False


class TestSearch:
    def test_finds_indexed_document(self, app, theory_entry):
        with app.app_context():
            index_file_entry(app, theory_entry, "theory")
            db.session.commit()
            results = search_fts(app, "router")
            assert any(r["object_id"] == theory_entry.id for r in results)
            assert results[0]["model_type"] == "theory"

    def test_empty_query(self, app):
        with app.app_context():
            assert search_fts(app, "") == []
            assert search_fts(app, "   ") == []

    def test_remove_from_index(self, app, theory_entry):
        with app.app_context():
            index_file_entry(app, theory_entry, "theory")
            db.session.commit()
            remove_from_index(app, "theory", theory_entry.id)
            results = search_fts(app, "router")
            assert not any(r["object_id"] == theory_entry.id for r in results)
