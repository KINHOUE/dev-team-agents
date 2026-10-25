---
name: agent-health-monitor
description: Use when auditing the health of every Hermes agent profile. Runs static config audit plus a real LLM health check per profile, writes a dated report and returns it to the orchestrator.
---

# Surveillance de santé des agents

Objectif : vérifier que **chaque** profil Hermes est réellement opérationnel — pas seulement bien configuré — puis produire un rapport daté et le remonter à l'orchestrateur.

## Quand l'utiliser

- Audit hebdomadaire planifié (cronjob).
- Après un changement de modèle, de clé API ou de provider.
- Quand un agent ne répond plus ou renvoie une erreur 404/401/403.

## Procédure

### 1. Audit statique

```bash
python "<SKILL_DIR>/scripts/audit_profiles.py"
```

Contrôle pour chaque profil : bloc `model` (modèle, provider, `base_url`), présence de la clé API du provider dans `.env`, skills métier installées, incohérence modèle/provider.

Sortie : un tableau + la liste des problèmes détectés. **Un profil peut passer cet audit et être cassé** (clé expirée) → l'étape 2 est obligatoire.

### 2. Test de santé réel

```bash
bash "<SKILL_DIR>/scripts/health_check.sh"
```

Envoie à chaque profil une question dont la réponse **n'est pas dans la question** (« Combien font 17+25 ? » → `42`), puis vérifie la sortie. Détecte les clés mortes et les modèles retirés que l'audit statique ne voit pas.

Durée : ~15-20 s par profil (environ 2-3 min au total). Sortie : `/tmp/health-profiles.txt` (`profil|statut|durée`).

**Ne jamais réutiliser un mot de la question comme critère de réussite** — un « Réponds OK » est validé par l'écho de la requête elle-même.

### 3. Rapport

Écrire `C:/Users/PC/dev-team/docs/rapports/sante-agents-YYYY-MM-DD.md` :

```markdown
# Santé des agents — YYYY-MM-DD

| Profil | Statut | Durée |
|---|---|---|
…

## Défaillances
- …

## Actions correctives appliquées
- …
```

Un rapport par date, jamais d'écrasement.

### 4. Remontée à l'orchestrateur

Terminer la tâche avec `kanban_complete` :

- `summary` : verdict en une phrase, ex. « 9/9 agents opérationnels » ou « 1 agent KO : secu (404 modèle) ».
- `metadata` : `{"agents_total": 10, "agents_ok": 9, "agents_ko": ["secu"], "duree_s": 180}`.
- `artifacts` : chemin absolu du rapport — il est ainsi transmis en pièce jointe à l'utilisateur.

Si un agent est KO, **ouvrir une tâche de correction** assignée au profil concerné (ou à `devops` pour un problème de configuration), avec le message d'erreur exact.

## Règles

- Ne jamais déclarer un agent « opérationnel » sans le test réel de l'étape 2.
- Ne jamais corriger un modèle ou une clé sans le re-tester ensuite.
- Signaler les points de vigilance structurels : modèle unique partagé, clé unique, absence de repli.
