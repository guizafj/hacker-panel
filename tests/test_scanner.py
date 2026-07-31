from src.models.theory import Theory
from src.utils.scanner import scan_directory


def test_scan_adds_new_files(app, tmp_path):
    d = tmp_path / "teoria"
    d.mkdir()
    (d / "mod1.md").write_text("# Modulo 1", encoding="utf-8")
    (d / "mod2.md").write_text("# Modulo 2", encoding="utf-8")

    with app.app_context():
        counts = scan_directory(app, str(d), Theory, ".md")
        assert counts == {"added": 2, "updated": 0, "removed": 0}
        entries = Theory.query.all()
        assert len(entries) == 2


def test_scan_reindexes_changed_content(app, tmp_path):
    d = tmp_path / "teoria"
    d.mkdir()
    f = d / "mod1.md"
    f.write_text("# Modulo 1", encoding="utf-8")

    with app.app_context():
        assert scan_directory(app, str(d), Theory, ".md")["added"] == 1

        f.write_text("# Modulo 1 actualizado", encoding="utf-8")
        counts = scan_directory(app, str(d), Theory, ".md")
        assert counts == {"added": 0, "updated": 1, "removed": 0}

        entry = Theory.query.first()
        assert entry.content_hash is not None


def test_scan_removes_orphan_records(app, tmp_path):
    d = tmp_path / "teoria"
    d.mkdir()
    f = d / "mod1.md"
    f.write_text("# Modulo 1", encoding="utf-8")

    with app.app_context():
        assert scan_directory(app, str(d), Theory, ".md")["added"] == 1

        f.unlink()
        counts = scan_directory(app, str(d), Theory, ".md")
        assert counts == {"added": 0, "updated": 0, "removed": 1}
        assert Theory.query.count() == 0


def test_scan_ignores_other_extensions(app, tmp_path):
    d = tmp_path / "teoria"
    d.mkdir()
    (d / "script.py").write_text("print('x')", encoding="utf-8")

    with app.app_context():
        counts = scan_directory(app, str(d), Theory, ".md")
        assert counts == {"added": 0, "updated": 0, "removed": 0}
