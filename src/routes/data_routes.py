import os
import json
from flask import Blueprint, render_template, request, url_for, send_from_directory
from src.models.scripts import Scripts
from models.write_ups import WriteUps
from src.models.theory import Theory
from src.utils.search_utils import search_whoosh
import asyncio
from collections import OrderedDict
import mistune
import re

data_bp = Blueprint('data', __name__)

# Renderer personalizado para mistune
class MyRenderer(mistune.HTMLRenderer):
    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def image(self, src, alt="", title=None):
        # Construir la ruta de la imagen dinámicamente
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
            # Manejar el caso en que el objeto no sea de un tipo conocido
            return None  # O lanzar una excepción

        # Verificar si es un enlace interno de Obsidian
        if src.startswith("![[") and src.endswith("]]"):
            filename = src[2:-2]  # Extraer el nombre del archivo
        elif re.match(r".*\((.*?)\).*", src):
            filename = re.match(r".*\((.*?)\).*", src).group(1)
        else:
            filename = src  # Usar el nombre del archivo tal como está

        image_url = url_for('data.view_image', base_dir=base_dir, category=category, filename=filename)
        return f'<img src="{image_url}" alt="{alt}" title="{title or alt}" />'

@data_bp.route("/search")
async def search():
    """Realiza la búsqueda en el índice de Whoosh."""
    query = request.args.get('q')
    results = await search_whoosh(query)
    return render_template('search.html', results=results, query=query)

@data_bp.route("/glosario")
def glosario():
    try:
        with open("data/glosario.json") as f:
            glosario = json.load(f)
    except FileNotFoundError:
        glosario = {"Glosario": []}
    except json.JSONDecodeError:
        glosario = {"Glosario": []}
    return render_template("glosario.html", glosario=glosario)

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
        markdown = mistune.Markdown(renderer=renderer)
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
        markdown = mistune.Markdown(renderer=renderer)
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
        markdown = mistune.Markdown(renderer=renderer)
        content_html = markdown(content_md)
        return render_template('theory_detail.html', title=theory.title, content=content_html)
    except FileNotFoundError:
        return "Archivo no encontrado", 404

@data_bp.route('/checklist')
def checklist():
    try:
        with open("data/checklist.json") as f:
            checklist = json.load(f)
    except FileNotFoundError:
        checklist = {"Checklist": []}
    except json.JSONDecodeError:
        checklist = {"Checklist": []}
    return render_template('checklist.html', checklist=checklist)

@data_bp.route('/data/<base_dir>/<category>/<path:filename>')
def view_image(base_dir, category, filename):
    """Sirve las imágenes desde el directorio de contenido."""
    img_dir = os.path.join('data', base_dir, category, 'img')
    return send_from_directory(img_dir, filename)

