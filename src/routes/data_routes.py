import os
from flask import Blueprint, render_template, request, url_for, send_from_directory, flash, redirect, current_app
from src.forms.data_forms import GlossaryForm, ChecklistForm, DeleteObjetiveForm, DeleteTermForm
from src.models.glossary import Term
from src.models.scripts import Scripts
from src.models.write_ups import WriteUps
from src.models.theory import Theory
from src.models.checklist import Objetive
from src.utils.search_utils import search_whoosh
import asyncio
from collections import OrderedDict
import mistune
import re
import logging
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from extensions import db

data_bp = Blueprint('data', __name__)

# Renderer personalizado para mistune
class MyRenderer(mistune.HTMLRenderer):
    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def image(self, src, alt="", title=None, **kwargs):
        """
        Renderiza imágenes en Markdown, manejando diferentes formatos de enlaces.
        """
        try:
            # Determinar la categoría y el directorio base según el tipo de objeto
            if isinstance(self.obj, Theory):
                category = self.obj.category
                base_dir = 'theory'
            elif isinstance(self.obj, WriteUps):
                category = self.obj.category
                base_dir = 'writeups'
            elif isinstance(self.obj, Scripts):
                category = self.obj.category
                base_dir = 'scripts'
            else:
                return f'<img src="{src}" alt="{alt}" title="{title or alt}" />'

            # Manejar enlaces internos de Obsidian (![[Pasted image.png]])
            if re.match(r"!\[\[(.*?)\]\]", src):
                match = re.match(r"!\[\[(.*?)\]\]", src)
                filename = match.group(1)  # Extraer el nombre del archivo
            # Manejar enlaces estándar de Markdown (![alt texto](image.png))
            elif re.match(r"!\[.*?\]\((.*?)\)", src):
                match = re.match(r"!\[.*?\]\((.*?)\)", src)
                filename = match.group(1)
            else:
                filename = src  # Usar el nombre del archivo tal como está

            # Validar que filename no sea None o vacío
            if not filename:
                current_app.logger.warning(f"Nombre de archivo de imagen vacío o None: {src}")
                return f'<img src="{src}" alt="{alt}" title="{title or alt}" />'

            # Limpiar el nombre del archivo
            filename = filename.strip()  # Eliminar espacios en blanco al principio y al final

            # Generar la URL para la imagen
            image_url = url_for('data.view_image', base_dir=base_dir, category=category, filename=os.path.join('img', filename))
            current_app.logger.info(f"URL de la imagen generada: {image_url}")  # Agrega esta línea
            return f'<img src="{image_url}" alt="{alt}" title="{title or alt}" />'

        except Exception as e:
            current_app.logger.error(f"Error al renderizar la imagen: {src} - {e}", exc_info=True)
            return f'<img src="{src}" alt="{alt}" title="{title or alt}" />'

    def block_code(self, code, lang=None, info=None):
        """
        Renderiza bloques de código con resaltado de sintaxis.
        """
        try:
            lexer = get_lexer_by_name(lang or 'text', stripall=True)
            formatter = HtmlFormatter(cssclass="codehilite")
            return highlight(code, lexer, formatter)
        except Exception as e:
            current_app.logger.error(f"Error al resaltar el bloque de código (lang={lang}): {e}", exc_info=True)
            return f'<pre><code>{mistune.escape(code)}</code></pre>'
        
@data_bp.route('/<base_dir>/<category>/<path:filename>')
def view_image(base_dir, category, filename):
    """Sirve las imágenes desde el directorio de contenido."""
    img_dir = os.path.join('data', base_dir, category)
    return send_from_directory(img_dir, filename)

@data_bp.route("/search")
async def search():
    """Realiza la búsqueda en el índice de Whoosh."""
    query = request.args.get('q')
    results = await search_whoosh(query)

    # Buscar términos del glosario en la base de datos
    glossary_results = Term.query.filter(
        Term.term.ilike(f"%{query}%") | 
        Term.translation.ilike(f"%{query}%") | 
        Term.description.ilike(f"%{query}%")
    ).all()
    
    # Buscar términos de la checklist en la base de datos
    checklist_results = Objetive.query.filter(
        Objetive.objetive.ilike(f"%{query}%") | 
        Objetive.methodology.ilike(f"%{query}%") | 
        Objetive.description.ilike(f"%{query}%")
    ).all()

    return render_template(
        'search.html',
        results=results,
        glossary_results=glossary_results,
        checklist_results = checklist_results,
        query=query
    )

@data_bp.route("/glosario")
def glosario():
    glosario = Term.query.all()
    form = DeleteTermForm()  # Crear una instancia del formulario
    return render_template('glosario.html', glosario=glosario, form=form)

@data_bp.route('/add_term',  methods=['GET', 'POST'])
def add_term():
    form = GlossaryForm()
    if form.validate_on_submit():
        try: 
            term = Term(
                term = form.term.data,
                translation = form.translation.data,
                description = form.description.data
            )
            db.session.add(term)
            db.session.commit()
            flash('Termino agregado de manera exitosa', 'success')
            return redirect(url_for('data.glosario'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear el termino: {e}", exc_info=True)
            flash('Error al agregar el termino.', 'error')
            return render_template('add_term.html', form=form)
    else:
        current_app.logger.info("El formulario no es valido")
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.error(f"Error en el campo {field}: {error}")
    return render_template('add_term.html', form=form)

@data_bp.route('/edit_term/<int:term_id>', methods=['GET', 'POST'])
def edit_term(term_id):
    term = Term.query.get_or_404(term_id)
    form = GlossaryForm(obj=term)
    
    if form.validate_on_submit():
        term.term = form.term.data
        term.translation = form.translation.data
        term.description = form.description.data
        db.session.commit()
        flash('Termino actualizada exitosamente!', 'success')
        return redirect(url_for('data.glosario'))
        
    return render_template('edit_term.html', form=form, term=term)

@data_bp.route('/delete_term/<int:term_id>', methods=['POST'])
def delete_term(term_id):
    term = Term.query.get_or_404(term_id)
    try:
        db.session.delete(term)
        db.session.commit()
        flash('Termino eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el termino.', 'error')
        current_app.logger.error(f"Error deleting term {term_id}: {e}", exc_info=True)
    return redirect(url_for('data.glosario'))

@data_bp.route('/checklist')
def checklist():
    checklist = Objetive.query.all()
    form = DeleteObjetiveForm()
    return render_template('checklist.html', checklist=checklist, form=form)

@data_bp.route('/add_objetive', methods=['GET', 'POST'])
def add_objetive():
    form = ChecklistForm()
    if form.validate_on_submit():
        try:
            objetive = Objetive(
                objetive=form.objetive.data,
                methodology=form.methodology.data,
                description=form.description.data,
                date_target=form.date_target.data,
                status=form.status.data,
                color=form.color.data
            )
            db.session.add(objetive)
            db.session.commit()
            flash('Objetivo agregado de manera exitosa', 'success')
            return redirect(url_for('data.checklist'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error al crear el objetivo: {e}', exc_info=True)
            flash('Error al agregar el objetivo', 'error')
            return render_template('add_objetive.html', form=form)
    else:
        current_app.logger.info('El formulario no es válido')
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.error(f'Error en el campo {field}: {error}')
    return render_template('add_objetive.html', form=form)

@data_bp.route('/edit_objetive/<int:objetive_id>', methods=['GET', 'POST'])
def edit_objetive(objetive_id):
    objetive = Objetive.query.get_or_404(objetive_id)
    form = ChecklistForm(obj=objetive)
    
    if form.validate_on_submit():
        objetive.objetive=form.objetive.data
        objetive.methodology=form.methodology.data
        objetive.description=form.description.data
        objetive.date_target=form.date_target.data
        objetive.status=form.status.data
        objetive.color=form.color.data
        db.session.commit()
        flash('Objetivo actualizada exitosamente!', 'success')
        return redirect(url_for('data.checklist'))
        
    return render_template('edit_objetive.html', form=form, objetive=objetive)

@data_bp.route('/delete_objetive/<int:objetive_id>', methods=['POST'])
def delete_objetive(objetive_id):
    objetive = Objetive.query.get_or_404(objetive_id)
    try:
        db.session.delete(objetive)
        db.session.commit()
        flash('Objetivo eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el objetivo.', 'error')
        current_app.logger.error(f"Error deleting objetive {objetive_id}: {e}", exc_info=True)
    return redirect(url_for('data.checklist'))
    
@data_bp.route("/scripts")
def list_scripts():
    scripts = Scripts.query.all()
    return render_template('scripts.html', scripts=scripts)

@data_bp.route('/scripts/<int:script_id>')
def view_script(script_id):
    script = Scripts.query.get_or_404(script_id)
    try:
        with open(script.file_path, 'r', encoding='utf-8') as f:
            conten_md = f.read()
        # se pasa la categoria al render
        renderer = MyRenderer(script)
        markdown = mistune.create_markdown(renderer=renderer)
        conten_html = markdown(conten_md)
        return render_template('scripts_detail.html', title=script.title, content=conten_html)
    except FileNotFoundError:
        return "Archivo no encontrado", 404

@data_bp.route('/writeups')
def list_writeups():
    write_ups = WriteUps.query.all()
    return render_template('writeups.html', write_ups=write_ups)

@data_bp.route('/writeups/<int:writeup_id>')
def view_writeup(writeup_id):
    writeup = WriteUps.query.get_or_404(writeup_id)
    try:
        with open(writeup.file_path, 'r', encoding='utf-8') as f:
            content_md = f.read()
        # se pasa la categoria al render
        renderer = MyRenderer(writeup)
        markdown = mistune.create_markdown(renderer=renderer)
        content_html = markdown(content_md)
        return render_template('writeups_detail.html', title=writeup.title, content=content_html)
    except FileNotFoundError:
        return 'Archivo no encontrado', 404

@data_bp.route('/theory')
def list_data():
    categories = {}
    for theory in Theory.query.all():
        if theory.category not in categories:
            categories[theory.category] = []
        categories[theory.category].append(theory)
        
    return render_template('theory.html', categories=categories)

@data_bp.route('/theory/<int:theory_id>')
def view_theory(theory_id):
    theory = Theory.query.get_or_404(theory_id)
    try:
        with open(theory.file_path, 'r', encoding='utf-8') as f:
            content_md = f.read()
        print(content_md)  # Agrega esta línea
        # se pasa la categoria al render
        renderer = MyRenderer(theory)
        markdown = mistune.create_markdown(renderer=renderer)
        content_html = markdown(content_md)
        return render_template('theory_detail.html', title=theory.title, content=content_html)
    except FileNotFoundError:
        return "Archivo no encontrado", 404



