# dev-team — équipe d'agents IA

Configuration d'une équipe de **11 agents Hermes** répartis en **deux unités indépendantes** : une qui construit les applications, une qui produit le contenu.

Ce dépôt contient les **identités** (`SOUL.md`), les **règles de collaboration** et le **skill de surveillance** — c'est-à-dire le « cerveau » de l'équipe. Aucune clé API, aucun historique de conversation, aucune donnée personnelle.

## Les deux unités

```
                    ┌──────────────────────────┐
                    │  UNE INSTALLATION HERMES │
                    │  un gateway, 11 profils  │
                    └───────────┬──────────────┘
                                │
              ┌─────────────────┴──────────────────┐
              ▼                                    ▼
   ┌────────────────────┐              ┌────────────────────┐
   │ UNITÉ DEV          │              │ UNITÉ MÉDIA        │
   │ board: default     │              │ board: media       │
   │ orchestre: default │              │ orchestre:         │
   │                    │              │   media-lead       │
   ├────────────────────┤              ├────────────────────┤
   │ architecte         │              │ video              │
   │ dev-web            │              │ marketing          │
   │ dev-mobile         │              │                    │
   │ qa                 │              │                    │
   │ devops             │              │                    │
   │ secu               │              │                    │
   │ maintenance        │              │                    │
   └────────────────────┘              └────────────────────┘
      construit les                       produit vidéos
      applications                        et contenu
```

Chaque unité a son **propre board kanban**, ses **propres workspaces** et son **propre dispatcher** : les tâches ne peuvent pas se mélanger.

## Les 11 agents

| Agent | Unité | Rôle |
|---|---|---|
| `default` | Dev | orchestrateur + développeur fullstack |
| `architecte` | Dev | conception, découpage en tâches |
| `dev-web` | Dev | backend API + frontend web |
| `dev-mobile` | Dev | application Expo |
| `qa` | Dev | tests, rapports de bugs |
| `devops` | Dev | déploiement, infrastructure |
| `secu` | Dev | audit de sécurité (obligatoire avant production) |
| `maintenance` | Dev | corrections + surveillance de santé de l'équipe |
| `media-lead` | Média | orchestrateur de l'unité média |
| `video` | Média | motion design, animations, montage |
| `marketing` | Média | contenu écrit, posts, croissance |

Détail des rôles et des compétences requises : [`config/profils.md`](config/profils.md).

## Le pipeline

```
architecte → dev-web / dev-mobile → qa → secu → devops
```

`secu` est une étape **obligatoire** avant toute mise en production : c'est cette étape qui a révélé 8 failles qui n'avaient pas été vues par les autres agents.

## Installation

### Prérequis

- [Hermes Agent](https://hermes-agent.nousresearch.com/docs/) installé
- Une clé API pour le provider de ton choix (DeepSeek, OpenRouter, Anthropic…)

### Recréer les profils

```bash
git clone https://github.com/KINHOUE/dev-team-agents.git
cd dev-team-agents
bash scripts/install.sh
```

Le script crée chaque profil et y copie son `SOUL.md`. Il ne touche à aucune clé : tu configures le modèle et les secrets toi-même ensuite.

### Configurer au minimum

```bash
# un modèle pour tous les profils (exemple DeepSeek)
for p in architecte dev-web dev-mobile qa devops secu maintenance media-lead video marketing; do
  hermes -p $p config set model.provider deepseek
  hermes -p $p config set model.default deepseek/deepseek-v4-pro
done
```

Chaque profil a son `.env` : c'est là que va la clé, jamais dans `config.yaml`.

### Créer les deux boards

```bash
hermes kanban boards create media --name "Media - video et marketing"
```

## Surveillance de l'équipe

L'agent `maintenance` embarque le skill [`agent-health-monitor`](skills/devops/agent-health-monitor/SKILL.md) :

1. audit statique de chaque profil (modèle, provider, clé, skills)
2. **test réel** de chaque agent (une question dont la réponse n'est pas dans l'énoncé)
3. rapport daté
4. remontée du verdict à l'orchestrateur

Il s'exécute via une tâche kanban planifiée — un rapport par semaine, avec alerte si un agent tombe.

## Ce que ce dépôt ne contient pas

| Absent | Raison |
|---|---|
| Clés API, tokens | secrets — vivent dans les `.env` locaux |
| `state.db`, sessions | historique de conversation |
| `config.yaml` complets | propres à chaque machine |
| Skills tierces (68 par profil) | fournies par Hermes, réinstallables |

Le skill `agent-health-monitor` est le seul inclus : c'est une création originale de cette équipe.

## Licence

MIT — voir [LICENSE](LICENSE).
