# Conventions de rédaction des skills d'équipe

Comment écrire un skill qui fonctionne dans plusieurs outils, pas seulement celui où il a été créé.

## But

Un même `SKILL.md` doit fonctionner dans **Claude Code**, **Cursor** et **Claude web (Team)**. Gemini en bonus, jamais une contrainte.

## Les cibles et ce qu'elles partagent

| Cible | Système de skills | Exécute du code |
|-------|-------------------|-----------------|
| Claude Code | dossier de skills global | Python, Bash |
| Cursor | dossier de skills global | Python, Bash, Node, etc. |
| Claude web (Team) | upload au niveau organisation | Python, Bash |
| Gemini | instructions / Gems (copier le contenu) | non |

Les trois premières partagent le format `SKILL.md` (frontmatter + markdown) et exécutent du code. Le dénominateur commun pour les scripts est donc **Python et Bash**.

## Règles

### 1. Frontmatter minimal

Seulement `name` et `description`, le dénominateur commun des trois cibles.

- `name` : kebab-case, préfixe `co-`, **en anglais** même si le contenu du skill est en français (ex. `co-evaluate-service`). Exception : un terme légal ou officiel garde sa forme consacrée (ex. `co-efvp`, acronyme de la Loi 25).
- `description` : quand utiliser le skill (sert au matching automatique). La rédiger pour qu'un terme du Cadre ou du domaine y apparaisse, pour la découvrabilité.
- Pas de clés propres à un seul outil (par exemple `disable-model-invocation`, `allowed-tools`) : elles sont ignorées ailleurs et créent du bruit.

### 2. Aucune référence personnelle

- Pas de prénom réel, pas de chemin personnel, pas de jargon interne non expliqué.
- Parler de « l'utilisateur ».
- Les exemples eux-mêmes doivent être neutres : un chemin générique, un nom de projet fictif, un outil connu. Jamais un prénom ni un dossier personnel comme exemple.

### 3. Décrire le concept, pas l'outil propriétaire

Le concept existe dans tous les harness, seul le nom diffère. On écrit le concept.

| À éviter (spécifique à un outil) | À privilégier (agnostique) |
|----------------------------------|----------------------------|
| « lance un subagent / Task tool » | « délègue à un agent secondaire » |
| « TaskCreate / todo UI » | « tiens une liste de tâches » |
| « ajoute un hook » | « demande confirmation avant toute action irréversible » |
| « via le MCP X » | « via l'outil X (si disponible) » |

### 4. Dépendances externes signalées en tête

Si le skill a besoin d'un outil externe (Notion, Azure, etc.), le **nommer au début** et signaler quoi faire s'il est absent. On assume que l'outil (MCP ou équivalent) est disponible au préalable ; le skill le dit simplement s'il ne l'est pas.

### 5. Scripts : Python ou Bash, calcul local de préférence

- **Langage** : Python ou Bash uniquement. Node n'est pas exécutable côté Anthropic (Cursor l'accepte, mais on vise le commun).
- **Contrainte propre à Claude web (Team)** : là, le sandbox d'exécution a un réseau sortant restreint, un délai court par exécution, et pas d'accès aux MCP. Un skill qui doit tourner sur le web limite donc ses scripts au calcul déterministe local (parsing, scoring, formatage), sans appel réseau ni API.
- **Skills réservés au dev** (Cursor, Claude Code) : ces outils gèrent le réseau et les MCP, la contrainte ci-dessus ne s'applique pas. Écrire quand même les scripts en calcul local garde le skill portable vers le web, mais ce n'est pas obligatoire pour un skill dev only.
- **Actions externes** (lire ou écrire dans Notion, Azure, etc.) : déléguées à l'agent via son outil ou MCP, décrites en mots dans le `SKILL.md`. Jamais codées en dur dans un script qui appelle une API.
- **Structure** : `SKILL.md` à la racine, plus au besoin `scripts/`, `references/`, `assets/`.

## Distribution

- `skills/` : skills génériques, déployables vers les trois cibles.
- `cursor/skills/` : variantes spécifiques à Cursor uniquement.
- Tout ajout ou modification passe par une pull request.
