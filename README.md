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
- Crear tareas **recurrentes** (en desarrollo).
- Visualización integrada con FullCalendar.

### 📝 Write-Ups

- Visualización de informes técnicos en formato Markdown convertido a HTML.
- Ideal para documentar laboratorios, retos o procesos complejos.

### 🐍 Scripts

- Lista de scripts con descripción funcional y propósito.
- Planeado: descarga directa de cada script y documentación adicional.

### 📖 Glosario Técnico

- Archivo JSON con términos clave del ámbito técnico y de seguridad.
- En continuo crecimiento a medida que se avanza en el estudio.

### 🔍 Buscador Global

- Motor de búsqueda con **Whoosh** que indexa todo el contenido del directorio `/data`.
- Soporte para búsqueda por palabra, frase o términos múltiples.
- Implementación futura de:
  - Diccionario de sinónimos.
  - Fragmentos (extractos) de contenido relevante en los resultados.

---

## 🧱 Estructura del Proyecto

```plaintext
hacker-panel/
├── app.py
├── templates/            ← Plantillas HTML (Jinja2)
├── static/               ← Estilos y scripts JS (Tailwind, FullCalendar)
├── data/                 ← Contenido de aprendizaje (writeups, scripts, glosario...)
├── instance/             ← Base de datos SQLite
├── src/                  ← Código organizado por módulos y rutas
│   ├── routes/
│   ├── models/
│   ├── forms/
│   └── utils/
├── whoosh_index/         ← Índices de búsqueda
├── requirements.txt
└── README.md
```

## ⚙️ Tecnologías Utilizadas

| Área       | Tecnología                 |
| ---------- | -------------------------- |
| Backend    | Flask + SQLAlchemy         |
| Frontend   | Tailwind CSS + HTML + JS   |
| Calendario | FullCalendar.js            |
| Markdown   | mistune                    |
| Búsqueda   | Whoosh                     |
| Plantillas | Jinja2                     |
| DB local   | SQLite                     |

## 📸 Capturas de Pantalla
_(En proceso de desarrollo)_

## 💡 Ejemplo de Uso

Imagina que eres un estudiante de ciberseguridad que está aprendiendo sobre redes. Puedes utilizar Hacker Panel para:

1.  Crear tareas en el calendario para estudiar diferentes protocolos de red (TCP, UDP, IP).
2.  Almacenar write-ups de laboratorios de redes que hayas completado.
3.  Documentar scripts de automatización que hayas creado para analizar el tráfico de red.
4.  Agregar términos clave al glosario, como "SYN flood" o "ARP spoofing".
5.  Utilizar el buscador para encontrar rápidamente información sobre un concepto específico.

## 📦 Instalación

1.  Clona el repositorio:

    ```bash
    git clone <https://github.com/guizafj/hacker-panel.git>
    cd hacker-panel
    ```

2.  Crea un entorno virtual e instala las dependencias:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  Crea los directorios `data` e `instance` en la raíz del proyecto.

    ```bash
    mkdir -p data/writeups data/scripts data/theory whoosh_index instance
    ```

4.  Ejecuta la aplicación para inicializar la base de datos:

    ```bash
    flask --app app run  # Ejecuta una vez para crear `hacker-panel.db`
    Ctrl + C             # Detén la aplicación
    ```

5.  Ejecuta el comando para escanear los directorios y crear los índices de búsqueda:

    ```bash
    flask scan-directories # Escanea /data y crea los índices de búsqueda
    ```

## Uso

1.  Inicia la aplicación:

    ```bash
    python app.py
    ```

2.  Accede al "Hacker Panel" en tu navegador.
    Accede desde: http://127.0.0.1:5000

3.  Utiliza las diferentes funcionalidades para organizar tu aprendizaje, realizar un seguimiento de tu progreso y acceder a información relevante.

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
