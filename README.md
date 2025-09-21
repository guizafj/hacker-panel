# 🧠 Hacker Panel

**Hacker Panel** es una herramienta de productividad y gestión del conocimiento diseñada para estudiantes de ciberseguridad, desarrolladores autodidactas y profesionales junior. Nace como una solución personal para organizar y optimizar el estudio en áreas como redes, hacking ético, programación y fundamentos técnicos. Con Hacker Panel, puedes gestionar tus CTF write-ups, organizar tus recursos de aprendizaje y crear un glosario personalizado, todo en un solo lugar.

Este proyecto está construido con **Flask**, usa archivos `.md` como fuente principal de conocimiento y permite integrarse fácilmente en flujos de trabajo autodidactas. Está publicado bajo **Licencia MIT**, por lo que puedes usarlo, modificarlo y adaptarlo libremente.

---

## 🎯 Objetivo del Proyecto

2.  Instala [PDM](https://pdm.fming.dev/latest/) (gestor moderno de dependencias y entornos):

- Planificar tareas y rutinas de estudio.
- Almacenar write-ups de laboratorios o CTFs.
- Documentar scripts de automatización y herramientas propias.
- Consultar rápidamente conceptos clave a través de un glosario.

3.  Instala las dependencias y crea el entorno virtual con PDM:
- Buscar términos o ideas a través de un motor de búsqueda interno.

---

## 🚀 Funcionalidades Principales

### 📆 Calendario Interactivo

- Crear, editar y eliminar tareas fácilmente.
- Reorganizar eventos con **drag & drop**.
- Marcar tareas como completadas.
- Crear tareas **recurrentes** (en desarrollo).
- Visualización integrada con FullCalendar.

    pdm run flask --app app run  # Ejecuta una vez para crear `hacker-panel.db`

- Visualización de informes técnicos en formato Markdown convertido a HTML.
- Ideal para documentar laboratorios, retos o procesos complejos.

### 🐍 Scripts

    pdm run flask scan-directories # Escanea /data y crea los índices de búsqueda
- Planeado: descarga directa de cada script y documentación adicional.

### 📖 Glosario Técnico

- Archivo JSON con términos clave del ámbito técnico y de seguridad.
- En continuo crecimiento a medida que se avanza en el estudio.

    pdm run python app.py

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
## Próximamente
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


## 📦 Instalación y Entornos
# 😧 Hacker Panel

**Hacker Panel** es una herramienta de productividad y gestión del conocimiento diseñada para estudiantes de ciberseguridad, desarrolladores autodidactas y profesionales junior. Nace como una solución personal para organizar y optimizar el estudio en áreas como redes, hacking ético, programación y fundamentos técnicos. Con Hacker Panel, puedes gestionar tus CTF write-ups, organizar tus recursos de aprendizaje y crear un glosario personalizado, todo en un solo lugar.

Este proyecto está construido con **Flask**, usa archivos `.md` como fuente principal de conocimiento y permite integrarse fácilmente en flujos de trabajo autodidactas. Está publicado bajo **Licencia MIT**, por lo que puedes usarlo, modificarlo y adaptarlo libremente.

---

## 🎯 Resumen rápido de cambios recientes (auditado)

He escaneado el estado del repositorio y verificado los cambios más relevantes introducidos recientemente. A continuación encontrarás un resumen accionable para colaboradores:

- pyproject.toml: migración y declaración completa de dependencias (PDM).
- pdm.lock: archivo de lock grande generado por PDM (graph de dependencias completo).
- static/css/accessibility.css: nuevas reglas CSS enfocadas en accesibilidad (focus, contraste, skip links, etc.).
- static/js/accessibility.js: script con mejoras de accesibilidad (gestión de foco, aria, anuncios para lectores de pantalla, handlers de Escape, etc.).
- src/hacker_panel/__init__.py: marcador de paquete (boilerplate).
- tests/__init__.py: marcador de paquete para tests.
- cert.pem y key.pem: certificados/clave privada detectados en el repositorio (ver sección de seguridad abajo).

Si necesitas la lista de cambios con status git exacto, ejecuta en tu máquina:

```bash
git status --porcelain
git diff --name-status main..HEAD
```

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
    mkdir -p data/writeups data/scripts data/theory whoosh_index instance
    ```
5. Inicializa la base de datos (ejecuta y detén tras la primera ejecución):
    ```bash
    pdm run flask --app app run
    # Detén la app con Ctrl+C tras la primera ejecución
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
    mkdir -p data/writeups data/scripts data/theory whoosh_index instance
    ```
3. Inicializa la base de datos (ejecuta y detén tras la primera ejecución):
    ```bash
    flask --app app run
    # Detén la app con Ctrl+C tras la primera ejecución
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

## 🔐 Notas de seguridad (importante)

Durante la revisión encontré archivos de certificado/clave (`cert.pem` y `key.pem`) en la raíz del repositorio. Nunca dejes claves privadas comprometidas en el control de versiones público. Recomendaciones inmediatas:

1. Si esos archivos contienen claves privadas en uso, dales de baja (rotación/invalidación) inmediatamente y crea nuevas credenciales.
2. Elimina las claves del repositorio y del historial Git (no solo `rm`):

```bash
# Eliminar del índice y añadir a .gitignore
git rm --cached cert.pem key.pem
echo "cert.pem" >> .gitignore
echo "key.pem" >> .gitignore

# Para limpiar el historial (opcional y con precaución): usa la herramienta adecuada, por ejemplo BFG o git filter-repo
# bfg --delete-files key.pem
# ó
# git filter-repo --path key.pem --invert-paths
```

3. Mantén secretos fuera del repo: usa variables de entorno, servicios de secretos (HashiCorp Vault, GitHub Secrets, AWS Secrets Manager) o archivos en `instance/` que se excluyan del control de versiones.

Si quieres, puedo ayudarte a generar los pasos concretos para eliminar esas claves del historial con `git filter-repo` o `bfg`.

---

## 📝 Cambios funcionales (resumen técnico)

- Se añadió `static/css/accessibility.css` y `static/js/accessibility.js` para mejorar accesibilidad (focus, roles ARIA, live regions, gestión de modales y dropdowns).
- `pyproject.toml` actualizado con lista extensa de dependencias y `pdm` como backend de build.
- `pdm.lock` generado y añadido (lock completo de dependencias).

Si quieres que genere un CHANGELOG o un PR con estos cambios --y notas de retrocompatibilidad para desarrolladores-- puedo prepararlo.

---

## ✅ Comprobaciones rápidas que puedes ejecutar ahora

```bash
# Ver archivos modificados
git status --short

# Ver diferencias respecto a main (lista de nombres)
git diff --name-only main..HEAD

# Exportar requisitos (PDM → pip)
pdm export --without-hashes -o requirements.txt

# (Opcional) Comprobar que README actualizado está limpio
git add README.md && git commit -m "docs: actualizar README con resumen de cambios y notas de seguridad" || true
```

---

## 🤝 Contribuciones

Este proyecto está abierto a mejoras. Si encuentras alguna vulnerabilidad, problema con las dependencias o quieres mejorar la accesibilidad, por favor abre un issue o PR.

Para contribuir:

1. Haz un fork del repositorio.
2. Crea tu rama (git checkout -b feature/mi-mejora).
3. Haz commit de tus cambios.
4. Abre un pull request explicando tu propuesta.

## � Licencia

Distribuido bajo la licencia MIT.

## ✍️ Autor

guizafj — creador y mantenedor de Hacker Panel.
