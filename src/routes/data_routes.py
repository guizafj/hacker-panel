import os
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    send_from_directory,
    flash,
    redirect,
    current_app,
)
from src.forms.data_forms import (
    GlossaryForm,
    ChecklistForm,
    DeleteObjectiveForm,
    DeleteTermForm,
)
from src.models.glossary import Term
from src.models.scripts import Scripts
from src.models.write_ups import WriteUps
from src.models.theory import Theory
from src.models.checklist import Objective
from src.utils.search_utils import (
    search_fts,
    resolve_search_objects,
    index_structured_entry,
    remove_from_index,
)
import mistune
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from extensions import db


# ---------------------------------------------------------------------------
# Helpers de imágenes
# ---------------------------------------------------------------------------


def find_image_intelligently(img_dir, filename):
    if os.path.exists(os.path.join(img_dir, filename)):
        return filename
    if not os.path.isdir(img_dir):
        return None
    for file in os.listdir(img_dir):
        if file.lower() == filename.lower():
            return file
    for file in os.listdir(img_dir):
        if filename.lower() in file.lower():
            return file
    if "Pasted image" in filename:
        match = re.search(r"(\d+)", filename)
        if match:
            date_part = match.group(1)
            for file in os.listdir(img_dir):
                if "Pasted image" in file and date_part in file:
                    return file
    match = re.search(r"image-?(\d*)", filename.lower())
    if match:
        num_part = match.group(1) or ""
        for file in os.listdir(img_dir):
            if file.lower().startswith(f"image-{num_part}") and file.lower().endswith(
                ".png"
            ):
                return file
    return None


data_bp = Blueprint("data", __name__)


# ---------------------------------------------------------------------------
# Renderer Markdown personalizado
# ---------------------------------------------------------------------------


class MyRenderer(mistune.HTMLRenderer):
    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def image(self, *args, **kwargs):
        if "url" in kwargs:
            alt = args[0] if args else ""
            src = kwargs["url"]
            title = kwargs.get("title", "")
        else:
            src = args[0] if args else kwargs.get("src", "")
            alt = args[1] if len(args) > 1 else kwargs.get("alt", "")
            title = args[2] if len(args) > 2 else kwargs.get("title", "")

        try:
            if isinstance(self.obj, Theory):
                category, base_dir = self.obj.category, "theory"
            elif isinstance(self.obj, WriteUps):
                category, base_dir = self.obj.category, "writeups"
            elif isinstance(self.obj, Scripts):
                category, base_dir = self.obj.category, "scripts"
            else:
                return f'<img src="{src}" alt="{alt}" title="{title}" />'

            filename = None

            if src and src.startswith("obsidian:"):
                import base64

                try:
                    filename = base64.b64decode(src[len("obsidian:") :]).decode("utf-8")
                except Exception as e:
                    current_app.logger.error(f"Error decodificando Obsidian img: {e}")

            elif src.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                filename = src.strip()
                current_app.logger.info(
                    f"Detectado enlace directo a imagen: {filename}"
                )

            elif src.startswith("alt "):
                alt_text = src[4:].strip()
                image_pattern = re.search(
                    r"(Pasted image \d+\.png|image-\d+\.png|image\d*\.png|.*\.(png|jpg|jpeg|gif|webp))",
                    alt_text,
                    re.IGNORECASE,
                )
                if image_pattern:
                    filename = image_pattern.group(1)

            if not filename:
                return f'<img src="{src}" alt="{alt}" title="{title}" />'

            img_dir = os.path.abspath(
                os.path.join(current_app.root_path, "data", base_dir, category, "img")
            )
            matched = find_image_intelligently(img_dir, filename)

            if matched:
                image_url = url_for(
                    "data.view_image",
                    base_dir=base_dir,
                    category=category,
                    filename=matched,
                )
                current_app.logger.info(f"URL de imagen generada: {image_url}")
                return (
                    f'<img src="{image_url}" alt="{alt}" title="{title}" '
                    f'class="markdown-image" loading="lazy" />'
                )
            else:
                current_app.logger.warning(f"Imagen no encontrada: {filename}")
                return f'<img src="{src}" alt="{alt}" title="{title}" />'

        except Exception as e:
            current_app.logger.error(
                f"Error al renderizar imagen {src}: {e}", exc_info=True
            )
            return f'<img src="{src}" alt="{alt}" title="{title}" />'

    def block_code(self, code, lang=None, info=None):
        try:
            lexer = get_lexer_by_name(lang or "text", stripall=True)
            formatter = HtmlFormatter(cssclass="codehilite")
            return highlight(code, lexer, formatter)
        except Exception as e:
            current_app.logger.error(
                f"Error resaltando código (lang={lang}): {e}", exc_info=True
            )
            return f"<pre><code>{mistune.escape(code)}</code></pre>"


def preprocess_markdown(content):
    obsidian_pattern = r"!\[\[(.*?)\]\]"

    def obsidian_to_markdown(match):
        import base64

        filename = match.group(1).strip()
        encoded = base64.b64encode(filename.encode("utf-8")).decode("utf-8")
        return f"![{filename}](obsidian:{encoded})"

    processed = re.sub(obsidian_pattern, obsidian_to_markdown, content)
    processed = re.sub(r" {2,}$", "  \n", processed, flags=re.MULTILINE)
    processed = re.sub(r"([^\n])\n([-*+]|\d+\.)", r"\1\n\n\2", processed)
    current_app.logger.info(
        "Procesando enlaces de imágenes Obsidian y mejorando formato"
    )
    return processed


def _build_markdown(obj):
    """Crea y devuelve una instancia de mistune configurada para el objeto dado."""
    renderer = MyRenderer(obj)
    return mistune.create_markdown(
        renderer=renderer,
        plugins=["table", "task_lists", "strikethrough", "footnotes", "url", "abbr"],
    )


# ---------------------------------------------------------------------------
# Imágenes
# ---------------------------------------------------------------------------


@data_bp.route("/view_image/<base_dir>/<category>/<path:filename>")
def view_image(base_dir, category, filename):
    try:
        filename = filename.replace("%20", " ")
        img_dir = os.path.abspath(
            os.path.join(current_app.root_path, "data", base_dir, category, "img")
        )
        current_app.logger.info(f"Buscando imagen en: {img_dir}/{filename}")

        matched = find_image_intelligently(img_dir, filename)
        if matched:
            current_app.logger.info(f"Imagen encontrada: {matched}")
            return send_from_directory(img_dir, matched)

        for root, dirs, files in os.walk(img_dir):
            if root == img_dir:
                continue
            for file in files:
                if file.lower() == filename.lower() or filename.lower() in file.lower():
                    return send_from_directory(root, file)

        current_app.logger.error(f"Imagen no encontrada: {filename}")
        return "Imagen no encontrada", 404

    except Exception as e:
        current_app.logger.error(
            f"Error sirviendo imagen {filename}: {e}", exc_info=True
        )
        return "Error al cargar la imagen", 500


# ---------------------------------------------------------------------------
# Búsqueda — ahora usa FTS5
# ---------------------------------------------------------------------------


@data_bp.route("/search")
def search():
    """Búsqueda unificada usando SQLite FTS5."""
    query = request.args.get("q", "").strip()

    raw_results = search_fts(current_app._get_current_object(), query)
    results = resolve_search_objects(raw_results)

    return render_template(
        "search.html",
        results=results,
        query=query,
    )


# ---------------------------------------------------------------------------
# Glosario
# ---------------------------------------------------------------------------


@data_bp.route("/glosario")
def glosario():
    glosario = Term.query.all()
    form = DeleteTermForm()
    return render_template("glosario.html", glosario=glosario, form=form)


@data_bp.route("/add_term", methods=["GET", "POST"])
def add_term():
    form = GlossaryForm()
    if form.validate_on_submit():
        try:
            term = Term(
                term=form.term.data,
                translation=form.translation.data,
                description=form.description.data,
            )
            db.session.add(term)
            db.session.commit()
            # Indexar en FTS5 tras guardar
            index_structured_entry(current_app._get_current_object(), term, "glossary")
            flash("Término agregado de manera exitosa", "success")
            return redirect(url_for("data.glosario"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear el término: {e}", exc_info=True)
            flash("Error al agregar el término.", "error")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.error(f"Error en campo '{field}': {error}")
    return render_template("add_term.html", form=form)


@data_bp.route("/edit_term/<int:term_id>", methods=["GET", "POST"])
def edit_term(term_id):
    term = db.session.get(Term, term_id)
    if term is None:
        from flask import abort

        abort(404)
    form = GlossaryForm(obj=term)

    if form.validate_on_submit():
        term.term = form.term.data
        term.translation = form.translation.data
        term.description = form.description.data
        db.session.commit()
        # Re-indexar en FTS5 tras actualizar
        index_structured_entry(current_app._get_current_object(), term, "glossary")
        flash("Término actualizado exitosamente!", "success")
        return redirect(url_for("data.glosario"))

    return render_template("edit_term.html", form=form, term=term)


@data_bp.route("/delete_term/<int:term_id>", methods=["POST"])
def delete_term(term_id):
    term = db.session.get(Term, term_id)
    if term is None:
        from flask import abort

        abort(404)
    try:
        remove_from_index(current_app._get_current_object(), "glossary", term_id)
        db.session.delete(term)
        db.session.commit()
        flash("Término eliminado.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar el término.", "error")
        current_app.logger.error(f"Error borrando term {term_id}: {e}", exc_info=True)
    return redirect(url_for("data.glosario"))


# ---------------------------------------------------------------------------
# Checklist
# ---------------------------------------------------------------------------


@data_bp.route("/checklist")
def checklist():
    checklist = Objective.query.all()
    form = DeleteObjectiveForm()
    return render_template("checklist.html", checklist=checklist, form=form)


@data_bp.route("/add_objective", methods=["GET", "POST"])
def add_objective():
    form = ChecklistForm()
    if form.validate_on_submit():
        try:
            objective = Objective(
                objective=form.objective.data,
                methodology=form.methodology.data,
                description=form.description.data,
                date_target=form.date_target.data,
                status=form.status.data,
                color=form.color.data,
            )
            db.session.add(objective)
            db.session.commit()
            index_structured_entry(
                current_app._get_current_object(), objective, "checklist"
            )
            flash("Objetivo agregado de manera exitosa", "success")
            return redirect(url_for("data.checklist"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear objetivo: {e}", exc_info=True)
            flash("Error al agregar el objetivo", "error")
            return render_template("add_objective.html", form=form)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.error(f"Error en campo '{field}': {error}")
    return render_template("add_objective.html", form=form)


@data_bp.route("/edit_objective/<int:objective_id>", methods=["GET", "POST"])
def edit_objective(objective_id):
    objective = db.session.get(Objective, objective_id)
    if objective is None:
        from flask import abort

        abort(404)
    form = ChecklistForm(obj=objective)

    if form.validate_on_submit():
        objective.objective = form.objective.data
        objective.methodology = form.methodology.data
        objective.description = form.description.data
        objective.date_target = form.date_target.data
        objective.status = form.status.data
        objective.color = form.color.data
        db.session.commit()
        index_structured_entry(
            current_app._get_current_object(), objective, "checklist"
        )
        flash("Objetivo actualizado exitosamente!", "success")
        return redirect(url_for("data.checklist"))

    return render_template("edit_objective.html", form=form, objective=objective)


@data_bp.route("/delete_objective/<int:objective_id>", methods=["POST"])
def delete_objective(objective_id):
    objective = db.session.get(Objective, objective_id)
    if objective is None:
        from flask import abort

        abort(404)
    try:
        remove_from_index(current_app._get_current_object(), "checklist", objective_id)
        db.session.delete(objective)
        db.session.commit()
        flash("Objetivo eliminado.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar el objetivo.", "error")
        current_app.logger.error(
            f"Error borrando objetivo {objective_id}: {e}", exc_info=True
        )
    return redirect(url_for("data.checklist"))


# ---------------------------------------------------------------------------
# Scripts
# ---------------------------------------------------------------------------


@data_bp.route("/scripts")
def list_scripts():
    scripts = Scripts.query.all()
    return render_template("scripts.html", scripts=scripts)


@data_bp.route("/scripts/<int:script_id>")
def view_script(script_id):
    script = db.session.get(Scripts, script_id)
    if script is None:
        from flask import abort

        abort(404)
    try:
        content_md = preprocess_markdown(
            open(script.file_path, "r", encoding="utf-8").read()
        )
        content_html = _build_markdown(script)(content_md)
        return render_template(
            "scripts_detail.html", title=script.title, content=content_html
        )
    except FileNotFoundError:
        return "Archivo no encontrado", 404


# ---------------------------------------------------------------------------
# Write-ups
# ---------------------------------------------------------------------------


@data_bp.route("/writeups")
def list_writeups():
    write_ups = WriteUps.query.all()
    return render_template("writeups.html", write_ups=write_ups)


@data_bp.route("/writeups/<int:writeup_id>")
def view_writeup(writeup_id):
    writeup = db.session.get(WriteUps, writeup_id)
    if writeup is None:
        from flask import abort

        abort(404)
    try:
        content_md = preprocess_markdown(
            open(writeup.file_path, "r", encoding="utf-8").read()
        )
        content_html = _build_markdown(writeup)(content_md)
        return render_template(
            "writeups_detail.html", title=writeup.title, content=content_html
        )
    except FileNotFoundError:
        return "Archivo no encontrado", 404


# ---------------------------------------------------------------------------
# Theory
# ---------------------------------------------------------------------------


@data_bp.route("/theory")
def list_data():
    categories = {}
    for theory in Theory.query.all():
        categories.setdefault(theory.category, []).append(theory)
    return render_template("theory.html", categories=categories)


@data_bp.route("/theory/<int:theory_id>")
def view_theory(theory_id):
    theory = db.session.get(Theory, theory_id)
    if theory is None:
        from flask import abort

        abort(404)
    try:
        content_md = preprocess_markdown(
            open(theory.file_path, "r", encoding="utf-8").read()
        )
        content_html = _build_markdown(theory)(content_md)
        return render_template(
            "theory_detail.html",
            title=theory.title,
            content=content_html,
            theory=theory,
        )
    except FileNotFoundError:
        current_app.logger.error(f"Archivo no encontrado: {theory.file_path}")
        return "Archivo no encontrado", 404
    except Exception as e:
        current_app.logger.error(f"Error renderizando teoría: {e}", exc_info=True)
        return "Error al procesar el contenido", 500
