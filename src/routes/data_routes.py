import os
from flask import Blueprint, render_template, request, url_for, send_from_directory, flash, redirect, current_app
from src.forms.data_forms import GlossaryForm, ChecklistForm, DeleteObjetiveForm, DeleteTermForm
from src.models.glossary import Term
from src.models.scripts import Scripts
from src.models.write_ups import WriteUps
from src.models.theory import Theory
from src.models.checklist import Objetive
from src.utils.search_utils import search_whoosh
import mistune
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from extensions import db

# Función para buscar imágenes de manera inteligente
def find_image_intelligently(img_dir, filename):
    """
    Busca una imagen de manera inteligente en el directorio especificado.
    Primero intenta una coincidencia exacta, luego coincidencia parcial,
    y finalmente búsqueda especial para formatos específicos.
    
    Args:
        img_dir: Directorio donde buscar la imagen
        filename: Nombre del archivo a buscar
        
    Returns:
        El nombre del archivo encontrado o None si no se encuentra
    """
    # 1. Búsqueda exacta
    if os.path.exists(os.path.join(img_dir, filename)):
        return filename
        
    # 2. Búsqueda insensible a mayúsculas/minúsculas
    for file in os.listdir(img_dir):
        if file.lower() == filename.lower():
            return file
            
    # 3. Coincidencia parcial
    for file in os.listdir(img_dir):
        if filename.lower() in file.lower():
            return file
            
    # 4. Búsqueda para "Pasted image"
    if "Pasted image" in filename:
        # Extraer la parte numérica (fecha)
        match = re.search(r'(\d+)', filename)
        if match:
            date_part = match.group(1)
            for file in os.listdir(img_dir):
                if "Pasted image" in file and date_part in file:
                    return file
    
    # 5. Búsqueda para imágenes genéricas (image-X.png)
    match = re.search(r'image-?(\d*)', filename.lower())
    if match:
        num_part = match.group(1) or ""
        for file in os.listdir(img_dir):
            if file.lower().startswith(f"image-{num_part}") and file.lower().endswith(".png"):
                return file
    
    # No se encontró ninguna coincidencia
    return None

data_bp = Blueprint('data', __name__)

# Renderer personalizado para mistune
class MyRenderer(mistune.HTMLRenderer):
    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def image(self, *args, **kwargs):
        """
        Renderiza imágenes en Markdown, manejando diferentes formatos de enlaces.
        """
        # Extraer parámetros según cómo mistune los pasa
        if 'url' in kwargs:
            # Mistune pasa alt como primer arg y url como kwarg
            alt = args[0] if args else ''
            src = kwargs['url']
            title = kwargs.get('title', '')
        else:
            # Fallback para otros formatos
            src = args[0] if args else kwargs.get('src', '')
            alt = args[1] if len(args) > 1 else kwargs.get('alt', '')
            title = args[2] if len(args) > 2 else kwargs.get('title', '')
        
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
                return f'<img src="{src}" alt="{alt}" title="{title}" />'

            print(f"DEBUG: base_dir='{base_dir}', category='{category}'")

            # Extraer el nombre del archivo de imagen de forma inteligente
            filename = None
            
            # Detectar imágenes que vienen del preprocesamiento de Obsidian
            if src and src.startswith('obsidian:'):
                # Decodificar el nombre de archivo del src (después del prefijo)
                import base64
                try:
                    encoded_filename = src[len('obsidian:'):]
                    obsidian_filename = base64.b64decode(encoded_filename).decode('utf-8')
                    current_app.logger.info(f"Detectada imagen de Obsidian: {obsidian_filename}")
                    filename = obsidian_filename
                except Exception as e:
                    current_app.logger.error(f"Error decodificando nombre de archivo Obsidian: {e}")
                    filename = None
            
            # Si src es un enlace directo (termina en imagen)
            elif src.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                filename = src.strip()
                current_app.logger.info(f"Detectado enlace directo a imagen: {filename}")
                
            # Si src contiene "alt " al principio (indicando que Mistune pasó el alt como src)
            elif src.startswith('alt '):
                # Extraer el nombre del archivo directamente del texto alt
                current_app.logger.info(f"Analizando src con 'alt': {src}")
                # Quitar el prefijo 'alt ' para obtener el texto del alt
                alt_text = src[4:].strip()
                
                # Búsqueda más amplia de patrones de imagen
                image_pattern = re.search(r'(Pasted image \d+\.png|image-\d+\.png|image\d*\.png|.*\.(png|jpg|jpeg|gif|webp))', alt_text, re.IGNORECASE)
                
                if image_pattern:
                    # Usar el nombre de archivo encontrado en el texto alt
                    filename = image_pattern.group(1)
                    current_app.logger.info(f"Nombre de archivo extraído del alt: {filename}")
                else:
                    # Si no se encuentra un patrón de imagen, intentar buscar por el nombre en el directorio
                    current_app.logger.warning(f"No se encontró patrón de imagen en: {alt_text}")
                    filename = None
            # Construir la ruta de la imagen
            if not filename:
                current_app.logger.warning(f"No se pudo extraer un nombre de archivo válido: {src}")
                return f'<img src="{src}" alt="{alt}" title="{title}" />'
                
            # Obtener ruta del directorio de imágenes
            img_dir = os.path.abspath(os.path.join(
                current_app.root_path,
                'data',
                base_dir,
                category,
                'img'
            ))
            
            # Buscar de manera inteligente la imagen
            matched_filename = find_image_intelligently(img_dir, filename)
            
            if matched_filename:
                # Crear URL para la imagen encontrada
                image_url = url_for(
                    'data.view_image', 
                    base_dir=base_dir, 
                    category=category, 
                    filename=matched_filename
                )
                
                current_app.logger.info(f"URL de imagen generada: {image_url}")
                return f'<img src="{image_url}" alt="{alt}" title="{title}" class="markdown-image" loading="lazy" />'
            else:
                current_app.logger.warning(f"No se encontró ninguna imagen que coincida con: {filename}")
                return f'<img src="{src}" alt="{alt}" title="{title}" />'

        except Exception as e:
            current_app.logger.error(f"Error al renderizar la imagen: {src} - {e}", exc_info=True)
            return f'<img src="{src}"  title="{title}" alt="{alt}"/>'

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

# Función para pre-procesar el contenido Markdown y convertir formato Obsidian a estándar
def preprocess_markdown(content):
    """
    Preprocesa el contenido Markdown para manejar formatos de imágenes Obsidian
    y mejorar el procesamiento de saltos de línea y listas.
    """
    # Convertir enlaces de imágenes tipo Obsidian (![[imagen.png]]) a formato compatible
    obsidian_pattern = r'!\[\[(.*?)\]\]'
    
    def obsidian_to_markdown(match):
        filename = match.group(1).strip()
        current_app.logger.info(f"Convirtiendo enlace Obsidian: {filename}")
        
        # Codificar el nombre del archivo para evitar problemas con espacios
        import base64
        encoded_filename = base64.b64encode(filename.encode('utf-8')).decode('utf-8')
        
        # Crear una referencia markdown estándar pero con un marcador especial
        # para identificarla fácilmente en el proceso de renderizado
        return f'![{filename}](obsidian:{encoded_filename})'
    
    processed_content = re.sub(obsidian_pattern, obsidian_to_markdown, content)
    
    # Mejorar el procesamiento de saltos de línea
    # Asegurar que las líneas con dos espacios al final se conviertan en <br>
    processed_content = re.sub(r' {2,}$', '  \n', processed_content, flags=re.MULTILINE)
    
    # Asegurar que las listas tengan el formato correcto
    # Agregar línea en blanco antes de listas si no existe
    processed_content = re.sub(r'([^\n])\n([-*+]|\d+\.)', r'\1\n\n\2', processed_content)
    
    current_app.logger.info("Procesando enlaces de imágenes Obsidian y mejorando formato")
    return processed_content
        
@data_bp.route('/view_image/<base_dir>/<category>/<path:filename>')
def view_image(base_dir, category, filename):
    """Sirve las imágenes desde el directorio de contenido."""
    try:
        # Decodificar el nombre del archivo si es necesario
        filename = filename.replace('%20', ' ')
        
        # Construir la ruta completa del directorio de imágenes
        img_dir = os.path.abspath(os.path.join(
            current_app.root_path,
            'data',
            base_dir,
            category,
            'img'
        ))
        
        # Depuración
        current_app.logger.info(f"Buscando imagen en: {img_dir}/{filename}")
        
        # Usar nuestra función inteligente para encontrar la imagen
        matched_filename = find_image_intelligently(img_dir, filename)
        
        if matched_filename:
            current_app.logger.info(f"Imagen encontrada: {matched_filename}")
            return send_from_directory(img_dir, matched_filename)
        
        # Si aún no se ha encontrado, intenta buscar en subdirectorios
        for root, dirs, files in os.walk(img_dir):
            if root == img_dir:
                continue  # Ya revisamos este directorio
                
            for file in files:
                if file.lower() == filename.lower() or filename.lower() in file.lower():
                    current_app.logger.info(f"Imagen encontrada en subdirectorio: {os.path.relpath(root, img_dir)}/{file}")
                    return send_from_directory(root, file)
        
        # Si no se encuentra ninguna coincidencia
        current_app.logger.error(f"No se encontró ninguna imagen que coincida con: {filename}")
        return "Imagen no encontrada", 404
            
    except Exception as e:
        current_app.logger.error(f"Error al servir la imagen {filename}: {e}", exc_info=True)
        return "Error al cargar la imagen", 500

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

@data_bp.route('/add_term', methods=['GET', 'POST'])
def add_term():
    form = GlossaryForm()
    if form.validate_on_submit():
        try: 
            term = Term(
                term=form.term.data,
                translation=form.translation.data,
                description=form.description.data
            )
            db.session.add(term)
            db.session.commit()
            flash('Término agregado de manera exitosa', 'success')
            return redirect(url_for('data.glosario'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear el término: {e}", exc_info=True)
            flash('Error al agregar el término.', 'error')
    else:
        current_app.logger.info("El formulario no es válido")
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
            content_md = f.read()
            
        # Pre-procesar el contenido para manejar formato Obsidian
        content_md = preprocess_markdown(content_md)
            
        # se pasa la categoria al render
        renderer = MyRenderer(script)
        markdown = mistune.create_markdown(
            renderer=renderer,
            plugins=[
                'table',
                'task_lists',
                'strikethrough',
                'footnotes',
                'url',
                'abbr'
            ]
        )
        content_html = markdown(content_md)
        return render_template('scripts_detail.html', title=script.title, content=content_html)
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
            
        # Pre-procesar el contenido para manejar formato Obsidian
        content_md = preprocess_markdown(content_md)
            
        # se pasa la categoria al render
        renderer = MyRenderer(writeup)
        markdown = mistune.create_markdown(
            renderer=renderer,
            plugins=[
                'table',
                'task_lists',
                'strikethrough',
                'footnotes',
                'url',
                'abbr'
            ]
        )
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
    """Renderiza el contenido de teoría con soporte mejorado para Markdown."""
    theory = Theory.query.get_or_404(theory_id)
    try:
        with open(theory.file_path, 'r', encoding='utf-8') as f:
            content_md = f.read()
            
        # Pre-procesar el contenido para manejar formato Obsidian
        content_md = preprocess_markdown(content_md)
            
        # Configurar el renderizador personalizado
        renderer = MyRenderer(theory)
        markdown = mistune.create_markdown(
            renderer=renderer,
            plugins=[
                'table',
                'task_lists',
                'strikethrough',
                'footnotes',
                'url',
                'abbr'
            ]
        )
        
        # Renderizar el contenido
        content_html = markdown(content_md)
        
        return render_template(
            'theory_detail.html',
            title=theory.title,
            content=content_html,
            theory=theory
        )
        
    except FileNotFoundError:
        current_app.logger.error(f"Archivo no encontrado: {theory.file_path}")
        return "Archivo no encontrado", 404
    except Exception as e:
        current_app.logger.error(f"Error al renderizar el contenido: {e}", exc_info=True)
        return "Error al procesar el contenido", 500



