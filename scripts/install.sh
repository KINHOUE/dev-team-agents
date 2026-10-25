#!/bin/bash
# Recrée les profils d'agents de ce dépôt dans une installation Hermes.
# Ne touche à aucune clé API : configure-les ensuite toi-même.
set -e

HERMES_HOME="${HERMES_HOME:-$HOME/AppData/Local/hermes}"
[ -d "$HERMES_HOME" ] || HERMES_HOME="$HOME/.hermes"

if [ ! -d "$HERMES_HOME" ]; then
  echo "Erreur : installation Hermes introuvable (cherché AppData/Local/hermes et ~/.hermes)."
  echo "Définis HERMES_HOME=/chemin/vers/hermes et relance."
  exit 1
fi

echo "Installation Hermes : $HERMES_HOME"
echo

for dir in agents/*/; do
  p=$(basename "$dir")
  if [ "$p" = "default" ]; then
    cp "$dir/SOUL.md" "$HERMES_HOME/SOUL.md"
    echo "✓ default (SOUL.md global)"
  else
    if hermes profile create "$p" --clone >/dev/null 2>&1; then
      echo "✓ $p (profil créé)"
    else
      echo "· $p (profil déjà présent)"
    fi
    cp "$dir/SOUL.md" "$HERMES_HOME/profiles/$p/SOUL.md"
  fi
done

echo
echo "Skill de surveillance :"
SKILL_DST="$HERMES_HOME/profiles/maintenance/skills/devops/agent-health-monitor"
mkdir -p "$SKILL_DST"
cp -r skills/devops/agent-health-monitor/. "$SKILL_DST/"
echo "✓ agent-health-monitor → maintenance"

echo
echo "Terminé. Étapes suivantes :"
echo "  1. Renseigner les clés API dans $HERMES_HOME/profiles/<profil>/.env"
echo "  2. Configurer le modèle de chaque profil (voir config/profils.md)"
echo "  3. Créer le board média : hermes kanban boards create media"
echo "  4. Démarrer le gateway : hermes gateway install --start-on-login"
