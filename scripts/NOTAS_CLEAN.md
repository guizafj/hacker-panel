Instrucciones para limpieza de historial (git-filter-repo)

1) Requisitos
- git
- python3 + pip
- git-filter-repo (instalar con `pip install git-filter-repo`)

2) Uso
- Revisa que tu working tree esté limpio: `git status --porcelain`
- Ejecuta: `./scripts/clean_history.sh` y responde `YES` cuando te lo pregunte.

3) Verificación
- Después de ejecutarlo, ejecuta:
  - `git rev-list --all --objects | grep -i -E 'whoosh_index|\.pem|node_modules' || true`

4) Push forzado
- Si todo está correcto: `git push --force --all && git push --force --tags`

5) Notas de seguridad
- Rota cualquier certificado/clave que haya sido purgado del repositorio.
