# Guía Didáctica: De pip/venv a PDM (y comparativa con pipenv)

---

## 1. ¿Por qué gestionar entornos y dependencias?

En Python, cada proyecto puede necesitar versiones distintas de librerías. Si instalas todo globalmente, puedes romper otros proyectos o tu sistema. Por eso, **virtualizar** (crear entornos aislados) y gestionar dependencias es fundamental para el desarrollo profesional y el aprendizaje.

---

## 2. Opciones populares para virtualización y gestión de paquetes

### A. pip + venv (la forma clásica)

- **¿Qué es?**
  - `venv` crea un entorno virtual aislado.
  - `pip` instala paquetes en ese entorno.
- **Comandos básicos:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- **Pros:**
  - Incluido en Python estándar.
  - Simple y universal.
  - Control total sobre el entorno.
- **Contras:**
  - No separa dependencias de desarrollo/producción.
  - No resuelve automáticamente conflictos de versiones.
  - No tiene lockfile por defecto (menos reproducible).

---

### B. pipenv (la opción intermedia)

- **¿Qué es?**
  - Herramienta que combina gestión de entornos virtuales y dependencias.
  - Usa `Pipfile` y `Pipfile.lock`.
- **Comandos básicos:**
  ```bash
  pipenv install
  pipenv shell
  pipenv install --dev <paquete>
  ```
- **Pros:**
  - Crea y gestiona el entorno virtual automáticamente.
  - Separa dependencias normales y de desarrollo.
  - Lockfile para reproducibilidad.
- **Contras:**
  - Más lento que pip puro.
  - Menos activo en desarrollo últimamente.
  - Puede ser confuso si ya tienes un `.venv` manual.

---

### C. PDM (la opción moderna y recomendada)

- **¿Qué es?**
  - Herramienta moderna basada en el estándar `pyproject.toml`.
  - Gestiona dependencias y entornos virtuales.
- **Comandos básicos:**
  ```bash
  pdm init
  pdm add flask
  pdm install
  pdm venv activate
  pdm run python app.py
  ```
- **Pros:**
  - Usa el estándar moderno (`pyproject.toml`).
  - Lockfile (`pdm.lock`) para máxima reproducibilidad.
  - Rápido, flexible y fácil de migrar desde pip/pipenv.
  - Soporta scripts, plugins y flujos avanzados.
- **Contras:**
  - Menos conocido en proyectos legacy.
  - Curva de aprendizaje si vienes de pip clásico.

---

## 3. Comparativa rápida

| Opción      | Virtualiza | Lockfile | Dev/Prod deps | Estándar moderno | Facilidad de uso | Velocidad |
|-------------|------------|----------|---------------|------------------|------------------|-----------|
| pip + venv  | Sí         | No       | No            | No               | Fácil            | Rápido    |
| pipenv      | Sí         | Sí       | Sí            | No               | Fácil            | Medio     |
| PDM         | Sí         | Sí       | Sí            | Sí               | Fácil/Media      | Rápido    |

---

## 4. Migración paso a paso: De pip/venv a PDM

### A. Pre-requisitos
- Python 3.8 o superior.
- Tener tu proyecto con un `requirements.txt` y/o un entorno `.venv`.

### B. Instala PDM
```bash
pip install --user pdm
# O mejor aún, con pipx:
pipx install pdm
```

### C. Elimina el entorno virtual antiguo (opcional pero recomendable)
```bash
rm -rf .venv
```

### D. Inicializa PDM en tu proyecto
```bash
pdm init
```
- Responde a las preguntas (nombre, versión, descripción, etc.).
- Si tienes un `requirements.txt`, puedes importar las dependencias automáticamente:
```bash
pdm import requirements requirements.txt
```

### E. Instala las dependencias y crea el entorno virtual
```bash
pdm install
```

### F. Activa el entorno virtual de PDM
```bash
pdm venv activate
```
- O ejecuta comandos directamente con:
  ```bash
  pdm run python app.py
  ```

### G. Verifica que todo funciona
- Prueba importar Flask u otros paquetes:
  ```bash
  pdm run python -c "import flask; print(flask.__version__)"
  ```
- Arranca tu aplicación:
  ```bash
  pdm run flask run
  ```

---


## 5. ¿Cómo gestionar y exportar dependencias en PDM?

- **Agregar una dependencia:**
  ```bash
  pdm add nombre_paquete
  ```
- **Agregar una dependencia de desarrollo:**
  ```bash
  pdm add --dev nombre_paquete
  ```
- **Actualizar dependencias:**
  ```bash
  pdm update
  ```
- **Bloquear versiones (lockfile):**
  ```bash
  pdm lock
  ```

### ¿Cómo se exporta un requirements.txt en PDM?

En PDM **no se usa** `pip freeze` ni se mantiene manualmente un `requirements.txt`.
PDM gestiona las dependencias en `pyproject.toml` y bloquea las versiones exactas en `pdm.lock`.

- Si necesitas un `requirements.txt` (por ejemplo, para deploy en un entorno que solo acepte pip), puedes generarlo así:
  ```bash
  pdm export > requirements.txt
  ```
Esto exporta las dependencias bloqueadas en el lockfile a un formato compatible con pip.

**Resumen:**
- No uses `pip freeze` con PDM.
- Usa `pdm export` si necesitas un `requirements.txt` para compatibilidad.
- El flujo moderno es trabajar solo con `pyproject.toml` y `pdm.lock`.

---

## 6. Consejos y buenas prácticas

- Lee la [documentación oficial de PDM](https://pdm.fming.dev/latest/).
- Usa siempre lockfiles para máxima reproducibilidad.
- Si colaboras en equipo, documenta el flujo de trabajo elegido.
- Si tienes scripts de automatización, actualízalos para usar `pdm run`.

---

## 7. ¿Cuándo elegir cada opción?

- **pip + venv:**  Proyectos simples, scripts rápidos, aprendizaje inicial.
- **pipenv:**  Proyectos legacy, transición suave desde pip, equipos acostumbrados a Pipfile.
- **PDM:**  Proyectos modernos, equipos que buscan estar a la vanguardia, máxima compatibilidad futura.

---

## 8. Recursos útiles

- [Documentación oficial de PDM](https://pdm.fming.dev/latest/)
- [Comparativa de gestores de dependencias Python (en inglés)](https://py-pkgs.org/04-dependencies)
- [Documentación oficial de pipenv](https://pipenv.pypa.io/en/latest/)

---

**¡Listo! Ahora tienes una visión clara y moderna para gestionar tus entornos Python y migrar tu proyecto a PDM de forma profesional y didáctica.**
