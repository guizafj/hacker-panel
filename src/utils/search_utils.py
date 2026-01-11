import os
import json
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer
from src.models.scripts import Scripts
from src.models.write_ups import WriteUps
from src.models.theory import Theory

# import spacy
import asyncio

WHOOSH_INDEX_DIR = "whoosh_index"

# Cargar modelos de spaCy - temporalmente deshabilitado
# try:
#     nlp_es = spacy.load("es_core_news_sm")
# except OSError:
#     print("Descargando modelo de spaCy para español...")
#     spacy.cli.download("es_core_news_sm")
#     nlp_es = spacy.load("es_core_news_sm")

# try:
#     nlp_en = spacy.load("en_core_web_sm")
# except OSError:
#     print("Descargando modelo de spaCy para inglés...")
#     spacy.cli.download("en_core_web_sm")
#     nlp_en = spacy.load("en_core_web_sm")

# Variables dummy para evitar errores
nlp_es = None
nlp_en = None

WHOOSH_INDEX_DIR = "whoosh_index"

# Cargar modelos de spaCy
# try:
#     nlp_es = spacy.load("es_core_news_sm")
# except OSError:
#     print("Descargando modelo de spaCy para español...")
#     spacy.cli.download("es_core_news_sm")
#     nlp_es = spacy.load("es_core_news_sm")

# try:
#     nlp_en = spacy.load("en_core_web_sm")
# except OSError:
#     print("Descargando modelo de spaCy para inglés...")
#     spacy.cli.download("en_core_web_sm")
#     nlp_en = spacy.load("en_core_web_sm")


def create_whoosh_index():
    """Crea el índice de Whoosh con stemming."""
    if not os.path.exists(WHOOSH_INDEX_DIR):
        os.makedirs(WHOOSH_INDEX_DIR)

    # Usar StemmingAnalyzer para aplicar stemming al contenido
    schema = Schema(
        id=ID(unique=True, stored=True),
        title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        content=TEXT(analyzer=StemmingAnalyzer()),
        category=TEXT(stored=True),
        model_type=ID(
            stored=True
        ),  # Tipo de modelo (script, writeup, theory, glosario, checklist)
    )
    ix = create_in(WHOOSH_INDEX_DIR, schema)
    return ix


async def preprocess_text(text, lang="es"):
    """Procesa el texto usando spaCy de forma asíncrona."""
    if lang == "es":
        nlp = nlp_es
    elif lang == "en":
        nlp = nlp_en
    else:
        raise ValueError("Idioma no soportado")

    doc = await asyncio.to_thread(nlp, text)  # Ejecutar nlp en un hilo separado

    # Lematización y stop word removal
    tokens = [token.lemma_ for token in doc if not token.is_stop]

    return " ".join(tokens)


async def add_document_to_index(writer, doc_id, title, content, category, model_type):
    """Añade un documento al índice de forma asíncrona."""
    content = await preprocess_text(content, lang="es")  # Preprocesar el contenido
    print(f"Contenido después del preprocesamiento: {content}")  # Agrega este log
    writer.add_document(
        id=doc_id,
        title=title,
        content=content,
        category=category,
        model_type=model_type,
    )


async def populate_whoosh_index():
    """Llena el índice con los datos de la base de datos y los archivos JSON."""
    ix = open_dir(WHOOSH_INDEX_DIR)
    writer = ix.writer()

    async def index_data():
        # Indexar Scripts
        for script in Scripts.query.all():
            try:
                with open(script.file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                await add_document_to_index(
                    writer,
                    f"script-{script.id}",
                    script.title,
                    content,
                    script.category,
                    "script",
                )
            except FileNotFoundError:
                print(f"Archivo no encontrado: {script.file_path}")

        # Indexar WriteUps
        for writeup in WriteUps.query.all():
            try:
                with open(writeup.file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                await add_document_to_index(
                    writer,
                    f"writeup-{writeup.id}",
                    writeup.title,
                    content,
                    writeup.category,
                    "writeup",
                )
            except FileNotFoundError:
                print(f"Archivo no encontrado: {writeup.file_path}")

        # Indexar Theory
        for theory in Theory.query.all():
            try:
                with open(theory.file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                await add_document_to_index(
                    writer,
                    f"theory-{theory.id}",
                    theory.title,
                    content,
                    theory.category,
                    "theory",
                )
            except FileNotFoundError:
                print(f"Archivo no encontrado: {theory.file_path}")

    await index_data()
    writer.commit()


async def search_whoosh(query):
    """Realiza la búsqueda en el índice de Whoosh con preprocesamiento spaCy e inclusion de diccionario de sinonimos"""
    results = []

    if query:
        ix = open_dir(WHOOSH_INDEX_DIR)
        with ix.searcher() as searcher:
            # Cargar sinónimos desde el archivo JSON
            try:
                with open(
                    "src/utils/synonyms.json", "r", encoding="utf-8"
                ) as f:  # Ajusta la ruta aquí
                    sinonimos = json.load(f)
            except FileNotFoundError:
                print("Archivo synonyms.json no encontrado")
                sinonimos = {}
            except json.JSONDecodeError:
                print("Error al decodificar synonyms.json")
                sinonimos = {}

            # Expandir la consulta con sinónimos
            expanded_query = query
            for palabra, lista_sinonimos in sinonimos.items():
                if palabra in query:
                    expanded_query += " OR " + " OR ".join(lista_sinonimos)

            # Preprocesar la consulta expandida
            expanded_query = await preprocess_text(expanded_query, lang="es")

            parser = QueryParser("content", ix.schema)
            q = parser.parse(expanded_query)
            results_whoosh = searcher.search(q, limit=10)

            for hit in results_whoosh:
                print(f"Contenido del hit: {hit}")  # Agrega este log
                model_type = hit["model_type"]
                item = None

                if model_type == "script":
                    item = Scripts.query.get(int(hit["id"].split("-")[1]))
                elif model_type == "writeup":
                    item = WriteUps.query.get(int(hit["id"].split("-")[1]))
                elif model_type == "theory":
                    item = Theory.query.get(int(hit["id"].split("-")[1]))
                if item:
                    results.append(
                        {
                            "title": hit["title"],
                            "category": hit["category"],
                            "model_type": model_type,
                            "object": item,
                        }
                    )

    return results


async def initialize_search_index():
    """Crea e inicializa el índice de búsqueda si no existe."""
    try:
        open_dir(WHOOSH_INDEX_DIR)
    except:
        create_whoosh_index()
        await populate_whoosh_index()


def index_glossary():
    """Indexa los términos del glosario en Whoosh."""
    from whoosh.fields import Schema, TEXT, ID
    from whoosh.index import create_in
    from src.models.glossary import Term

    schema = Schema(
        id=ID(stored=True),
        term=TEXT(stored=True),
        translation=TEXT(stored=True),
        description=TEXT(stored=True),
    )

    index_dir = "index/glossary"
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    ix = create_in(index_dir, schema)
    writer = ix.writer()

    for term in Term.query.all():
        writer.add_document(
            id=str(term.id),
            term=term.term,
            translation=term.translation,
            description=term.description,
        )

    writer.commit()


def index_checklist():
    """Indexar los objetivos del checklist en Whoosh"""
    from whoosh.fields import Schema, TEXT, ID
    from whoosh.index import create_in
    from src.models.checklist import Objetive

    schema = Schema(
        id=ID(stored=True),
        Objetive=TEXT(stored=True),
        methodology=TEXT(stored=True),
        description=TEXT(stored=True),
    )

    index_dir = "index/checklist"
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    ix = create_in(index_dir, schema)
    writer = ix.writer()

    for objetive in Objetive.query.all():
        writer.add_document(
            id=str(objetive.id),
            objetive=objetive.objetive,
            methodology=objetive.methodology,
            description=objetive.description,
        )

    writer.commit()
