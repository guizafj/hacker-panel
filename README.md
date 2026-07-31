# 🧠 Hacker Panel

**Hacker Panel** es una herramienta de productividad y gestión del conocimiento diseñada para estudiantes de ciberseguridad, desarrolladores autodidactas y profesionales junior. Nace como una solución personal para organizar y optimizar el estudio en áreas como redes, hacking ético, programación y fundamentos técnicos. Con Hacker Panel, puedes gestionar tus CTF write-ups, organizar tus recursos de aprendizaje y crear un glosario personalizado, todo en un solo lugar.

Este proyecto está construido con **Flask**, usa archivos `.md` como fuente principal de conocimiento y permite integrarse fácilmente en flujos de trabajo autodidactas. Está publicado bajo **Licencia MIT**, por lo que puedes usarlo, modificarlo y adaptarlo libremente.

---

## 🎯 Objetivo del Proyecto

El objetivo principal es proporcionar una **plataforma centralizada** donde puedas:

- Planificar tareas y rutinas de estudio.
- Almacenar write-ups de laboratorios o CTFs.
- Documentar scripts de automatización y herramientas propias.
- Consultar rápidamente conceptos clave a través de un glosario.
- Buscar términos o ideas a través de un motor de búsqueda interno.

---

## 🚀 Funcionalidades Principales

### 📆 Calendario Interactivo

- Crear, editar y eliminar tareas fácilmente.
- Reorganizar eventos con **drag & drop**.
- Marcar tareas como completadas.
- Crear tareas **recurrentes** con días específicos de la semana.
- Visualización integrada con FullCalendar.
- API REST para gestión de tareas (`/task/api/tasks`).

### 📝 Write-Ups

- Visualización de informes técnicos en formato Markdown convertido a HTML.
- Renderizado personalizado de imágenes con soporte para enlaces Obsidian (`![[imagen.png]]`).
- Resaltado de sintaxis de código con Pygments.
- Ideal para documentar laboratorios, retos o procesos complejos.

### 🐍 Scripts

- Lista de scripts con descripción funcional y propósito.
- Indexado automático en el motor de búsqueda.
- Categorización por tipo de herramienta o funcionalidad.

### 📖 Glosario Técnico

- Gestión de términos técnicos con traducción y descripción.
- CRUD completo: agregar, editar, eliminar términos.
- Búsqueda integrada en el motor principal.
- Base de datos SQLite para persistencia.

### 🔍 Buscador Global

- Motor de búsqueda con **SQLite FTS5** que indexa todo el contenido del directorio `/data`.
- Soporte para búsqueda por palabra, frase o términos múltiples.
- Diccionario de sinónimos integrado (`src/utils/synonyms.json`).
- Indexado asíncrono con stemming y análisis de texto.
- Búsqueda combinada: archivos + glosario + checklist.

### ✅ Checklist de Objetivos

- Gestión de objetivos de aprendizaje con metodología y fechas objetivo.
- Estados de progreso con colores personalizables.
- Integración con el sistema de búsqueda.

---

## 🧱 Estructura del Proyecto

```plaintext
hacker-panel/
├── app.py                ← Aplicación Flask principal
├── config.py             ← Configuración de la aplicación
├── extensions.py         ← Extensiones Flask (DB, etc.)
├── pyproject.toml        ← Configuración PDM y dependencias
├── pdm.lock              ← Lockfile de dependencias
├── requirements.txt      ← Compatibilidad con pip/venv
├── templates/            ← Plantillas HTML (Jinja2)
├── static/               ← Assets frontend
│   ├── css/
│   │   ├── accessibility.css  ← Mejoras de accesibilidad
│   │   ├── markdown.css       ← Estilos para Markdown
│   │   └── ...
│   └── js/
│       ├── accessibility.js   ← Funciones de accesibilidad
│       └── fullcalendar/      ← Biblioteca de calendario
├── data/                 ← Contenido de aprendizaje
│   ├── writeups/
│   ├── scripts/
│   └── theory/
├── src/                  ← Código fuente organizado
│   ├── routes/           ← Blueprints de Flask
│   ├── models/           ← Modelos SQLAlchemy
│   ├── forms/            ← Formularios WTForms
│   └── utils/            ← Utilidades (búsqueda, scanner)
├── migrations/           ← Migraciones de base de datos
├── instance/             ← Base de datos SQLite
└── tests/                ← Tests unitarios
```

## ⚙️ Tecnologías Utilizadas

| Área       | Tecnología                 |
| ---------- | -------------------------- |
| Backend    | Flask + SQLAlchemy + Alembic |
| Frontend   | Tailwind CSS + HTML + JS   |
| Calendario | FullCalendar.js            |
| Markdown   | mistune + Pygments         |
| Búsqueda   | SQLite FTS5 + sinónimos + snippets BM25 |
| Plantillas | Jinja2                     |
| DB local   | SQLite                     |
| Seguridad  | Talisman + CSRF Protection |
| Gestión deps | PDM (Python Dependency Manager) |

## 💡 Ejemplo de Uso

Imagina que eres un estudiante de ciberseguridad que está aprendiendo sobre redes. Puedes utilizar Hacker Panel para:

1.  Crear tareas recurrentes en el calendario para estudiar diferentes protocolos de red (TCP, UDP, IP).
2.  Almacenar write-ups de laboratorios de redes con imágenes y código resaltado.
3.  Documentar scripts de automatización para análisis de tráfico de red.
4.  Agregar términos clave al glosario, como "SYN flood" o "ARP spoofing".
5.  Utilizar el buscador global para encontrar rápidamente información sobre un concepto específico.


---

## ⚙️ Instalación y Entornos (actualizado)

Puedes usar **Hacker Panel** con dos flujos de trabajo según tu preferencia:

### Opción 1: Usando PDM (recomendado)

1. Clona el repositorio:
    ```bash
    git clone https://github.com/guizafj/hacker-panel.git
    cd hacker-panel
    ```
2. Instala PDM (si no lo tienes):
    ```bash
    pip install -U pdm
    ```
3. Instala las dependencias y crea el entorno:
    ```bash
    pdm install
    ```
4. Crea los directorios necesarios (si aún no existen):
    ```bash
    mkdir -p data/write_ups data/scripts data/theory instance
    ```
5. Aplica las migraciones para crear las tablas de la base de datos:
    ```bash
    pdm run flask db upgrade
    ```
6. Escanea los directorios y crea los índices de búsqueda:
    ```bash
    pdm run flask scan-directories
    ```
7. Inicia la aplicación:
    ```bash
    pdm run python app.py
    ```

### Opción 2: Usando venv + pip (compatibilidad)

1. Crea un entorno virtual e instala las dependencias:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
2. Crea los directorios necesarios:
    ```bash
    mkdir -p data/write_ups data/scripts data/theory instance
    ```
3. Aplica las migraciones para crear las tablas de la base de datos:
    ```bash
    flask db upgrade
    ```
4. Escanea los directorios y crea los índices de búsqueda:
    ```bash
    flask scan-directories
    ```
5. Inicia la aplicación:
    ```bash
    python app.py
    ```

---

### 🔄 Sincronización de dependencias (PDM ↔ pip)

El archivo principal de dependencias es `pyproject.toml` (usado por PDM). Flujo recomendado para mantener compatibilidad con usuarios que usan `pip`/`venv`:

1. Gestiona paquetes y actualizaciones con PDM.
2. Cuando tengas un estado listo para compartir, exporta a `requirements.txt`:

```bash
pdm export --without-hashes -o requirements.txt
```

3. Comprueba en CI que `requirements.txt` esté sincronizado (por ejemplo, añadiendo un job que ejecute el comando anterior y falle si hay diferencias).

Recomendación sobre `pdm.lock`: mantener `pdm.lock` en el repositorio es útil para reproducibilidad. Sin embargo, el archivo puede crecer mucho. Opciones:

- Mantener `pdm.lock` en el repo (recomendado para reproducibilidad) y revisar tamaño periódicamente.
- Si el repo crece demasiado, mover `pdm.lock` a Git LFS o generar artefactos en CI.

---

## Próximamente

*   Implementación del estado de los checks para un seguimiento más claro del progreso.
*   Integración con mi sitio web personal: [www.dguiza.dev](www.dguiza.dev) (backend en Django).

## 🤝 Contribuciones

Este proyecto está abierto a mejoras, correcciones y nuevas funcionalidades. Si tienes una idea que se alinea con el propósito del proyecto, ¡tu contribución es bienvenida! Puedes contribuir de las siguientes maneras:

*   Implementando nuevas funcionalidades.
*   Corrigiendo errores existentes.
*   Mejorando la documentación.
*   Proponiendo nuevas ideas y mejoras.

Para contribuir:

1.  Haz un fork del repositorio.
2.  Crea tu rama (git checkout -b feature/mi-mejora).
3.  Haz commit de tus cambios.
4.  Abre un pull request explicando tu propuesta.

## 📜 Licencia

Distribuido bajo la licencia MIT. Si te resulta útil, no dudes en usarlo, compartirlo o adaptarlo a tu flujo de trabajo.

## ✍️ Autor

guizafj
🌐 Sitio web: [www.dguiza.dev](www.dguiza.dev) — 🐙 GitHub: [https://github.com/guizafj](https://github.com/guizafj)
Creador y mantenedor de Hacker Panel. Enfocado en backend con Python, aprendizaje autodidacta y formación en ciberseguridad.
