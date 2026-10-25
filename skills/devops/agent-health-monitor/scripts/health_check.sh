#!/bin/bash
# Test de sante reel : la reponse attendue (42) n'apparait pas dans la requete.
# Sortie : /tmp/health-profiles.txt  ->  profil|STATUT|duree
OUT="/tmp/health-profiles.txt"
: > "$OUT"

PROFILES="${*:-architecte dev-web dev-mobile qa devops secu maintenance video marketing}"

for p in $PROFILES; do
  START=$(date +%s)
  R=$(timeout 150 hermes -p "$p" chat -q "Combien font 17+25 ? Reponds uniquement par le resultat, sans texte." --oneshot 2>&1 | tr '\n' ' ')
  DUR=$(( $(date +%s) - START ))
  if printf '%s' "$R" | grep -qiE "404|not found|isn't available|401|403|Traceback"; then
    STATUS="ERREUR"
  elif printf '%s' "$R" | grep -qE "(^|[^0-9])42([^0-9]|$)"; then
    STATUS="OK"
  else
    STATUS="DOUTEUX"
  fi
  printf '%s|%s|%ss\n' "$p" "$STATUS" "$DUR" >> "$OUT"
  printf '%-14s %-9s %ss\n' "$p" "$STATUS" "$DUR"
done

echo "---"
echo "OK: $(grep -c '|OK|' "$OUT")  ERREUR: $(grep -c '|ERREUR|' "$OUT")  DOUTEUX: $(grep -c '|DOUTEUX|' "$OUT")"
echo "Resultats: $OUT"
