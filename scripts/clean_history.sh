#!/usr/bin/env bash
set -euo pipefail

echo "*** Limpieza de historial con git-filter-repo (quirúrgico) ***"
echo "Rutas/objetos a eliminar: whoosh_index, node_modules, archivos .pem"

if ! command -v git >/dev/null 2>&1; then
  echo "git no está disponible en PATH" >&2
  exit 2
fi

if ! python -c "import importlib,sys; sys.exit(0 if importlib.util.find_spec('git_filter_repo') else 1)" 2>/dev/null; then
  echo "git-filter-repo (paquete Python) no está instalado. Instálalo con: pip install git-filter-repo" >&2
  echo "O instala la herramienta del repositorio: https://github.com/newren/git-filter-repo" >&2
  exit 2
fi

read -r -p "Esto reescribirá la historia del repositorio. Escribir YES para continuar: " CONFIRM
if [[ "$CONFIRM" != "YES" ]]; then
  echo "Aborted by user. No se realizaron cambios."
  exit 0
fi

# Comprobar árbol de trabajo limpio
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Tu árbol de trabajo no está limpio. Haz commit o stash de los cambios antes de continuar." >&2
  git status --porcelain
  exit 3
fi

echo "Creando rama de respaldo 'backup-main'..."
git branch -f backup-main

echo "Ejecutando git-filter-repo (eliminando paths especificados)... Esto puede tardar varios minutos."
# Usar el módulo python para evitar problemas de PATH
python -m git_filter_repo --force --invert-paths \
  --paths whoosh_index \
  --paths node_modules \
  --paths-glob '*.pem' \
  --paths cert.pem \
  --paths key.pem

echo "Optimización y limpieza local..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "Verifica que no quedan referencias a whoosh_index o .pem:" 
echo "  git rev-list --all --objects | grep -i -E 'whoosh_index|\\.pem' || true"

cat <<'EOF'
Siguientes pasos recomendados:
 1) Ejecuta el comando de verificación anterior. Si no hay resultados, procede.
 2) Forzar push a remoto (ADVERTENCIA: reescribe historial remoto):
      git push --force --all
      git push --force --tags
 3) Notifica a colaboradores: deberán clonar de nuevo o resetear sus ramas.
 4) Si se removieron claves/certificados (.pem), rota/revoca inmediatamente esas claves.

EOF

echo "Script finalizado. Revisa salidas y procede con el push forzado si estás listo."
