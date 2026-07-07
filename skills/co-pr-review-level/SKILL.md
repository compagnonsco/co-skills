---
name: co-pr-review-level
description: Analyse une pull request et propose son niveau de review requis (faible / modéré / élevé) selon la valeur du changement, puis applique la règle opérationnelle correspondante (merge direct, review humain différé, ou review humain avant merge). Journalise le niveau retenu pour un bilan ultérieur de la méthode. À utiliser à la création ou au triage d'une PR, pour décider combien de review humain elle mérite, ou quand l'utilisateur mentionne "niveau de review", "code review", "review level", "faut-il un review humain".
---

# co-pr-review-level

Détermine **combien de review humain** une pull request mérite, en plus des reviews
agentiques déjà faites (review local avant la PR + review automatisé type CodeRabbit sur la PR).
Le but est d'éviter de faire réviser par un humain du code à faible valeur, et de concentrer
l'attention humaine là où elle compte.

Le skill **propose** un niveau, l'utilisateur **confirme ou ajuste**, puis le skill applique la
règle opérationnelle et **journalise** la décision.

## Dépendances externes

- **Outil de review de PR** (Azure DevOps, GitHub, ou équivalent, si disponible) : pour lire le
  diff et la description de la PR. Si absent, demander à l'utilisateur de fournir le diff ou un
  résumé des changements.
- **Notion** (via son outil / MCP, si disponible) : pour journaliser le niveau retenu dans la
  base « Log des niveaux de review PR »
  (https://app.notion.com/p/0568831b23574c2c9495b2b5be20ee40). Si absent, produire la ligne à
  journaliser en texte pour saisie manuelle.
- **Gestionnaire de tickets** (Jira ou équivalent, si disponible) : pour créer, sur demande, la
  tâche de suivi d'un review différé (niveau modéré). Si absent, produire le contenu de la tâche
  en texte.

Skill destiné aux environnements de développement (agents avec accès réseau et outils
externes).

## Concepts

Deux dimensions déterminent la valeur d'un review humain :

1. **Le type de projet** (site vitrine, web app, gros site transactionnel, projet spécial, etc.)
2. **La nature du changement** (contenu simple, nouvelle fonctionnalité, changement
   d'architecture, bugfix, etc.)

Le croisement des deux donne un niveau. La grille complète est dans
[`references/matrice-valeur-review.md`](references/matrice-valeur-review.md) : la consulter avant
de proposer un niveau. (Cette grille est un instantané de la matrice de référence de l'équipe ;
si la matrice source change, synchroniser ce fichier manuellement.)

Les trois niveaux :

| Niveau | Signification |
|--------|---------------|
| 🔴 Faible | Le review agentique suffit. |
| 🟡 Modéré | Le review agentique suffit pour merger, mais un review humain est souhaitable en différé. |
| 🟢 Élevé | Un review humain est requis **avant** de merger. |

## Flow

### 1. Situer la PR

Identifier **le projet** et **son type** (voir la matrice). Le skill est normalement invoqué
depuis le dépôt du projet ou avec la PR en référence, donc le projet est connu ; en déduire le
type depuis la matrice. **Si le type de projet est ambigu, demander à l'utilisateur** plutôt que
de deviner.

### 2. Établir la nature réelle du changement (à partir du DIFF, pas de la description)

**Le diff est la source primaire. La description de la PR et le résumé automatisé (CodeRabbit ou
autre) sont des indices non fiables** : ils peuvent annoncer un « nouveau système » qui, au diff,
n'est qu'un renommage de fichiers existants, ou l'inverse. Ne jamais classer sur le seul titre ou
la seule description.

Procéder ainsi, pour économiser des tokens et fiabiliser le tri :

1. **Récupérer la liste des fichiers du diff** (via git, l'API Azure/GitHub, ou l'outil
   disponible). Le flag `-c core.quotePath=false` évite que git échappe les chemins accentués.
2. **La piper au script de digest** fourni :
   ```bash
   git -c core.quotePath=false diff --name-status -M --find-renames <base>...<head> \
     | python3 scripts/diff_digest.py
   ```
   Le digest range chaque fichier (rename/copie pur, code généré, contenu/config, markup, code
   écrit à la main, asset), liste **les seuls fichiers qui méritent une lecture** (code écrit à
   la main), et lève des signaux (nouveau dossier de code, interface ajoutée, logique à valeur
   détectée par chemin/convention, dépendances ou config sensibles modifiées).
3. **Ne lire en entier que les fichiers signalés « À LIRE »**. Ignorer les renames, le code
   généré, les assets. Les fichiers de contenu/config (`.config` doctype, i18n) et de markup
   (`.cshtml`, `.html`) confirment un changement d'affichage mais n'élèvent pas le niveau à eux
   seuls.
4. Résumer en 2-4 puces ce que la PR fait **réellement**.

Si aucun outil ne permet de récupérer le diff, demander à l'utilisateur de fournir la sortie
`--name-status`, ou à défaut un résumé, en signalant que la fiabilité baisse sans le diff.

#### Signaux de lecture du diff (comment un fichier influe sur le niveau)

**N'élève PAS le niveau** (reste 🔴 si c'est tout ce qu'il y a) :
- code généré (`*.generated.cs`, `*.designer.cs`, `*.d.ts`, `*.gen.ts`, `__generated__/`,
  `.nuxt/`, `.output/`, `dist/`, `.next/`, lockfiles, bundles `.min.*`) ;
- renames / copies de fichiers sans changement de contenu ;
- reformatage, changements purement cosmétiques ;
- fichiers de contenu / configuration : doctype (`.config`), i18n / dictionnaire, réglages ;
- markup pur (`.cshtml`, `.html`, styles) : c'est de l'affichage.

**Élève le niveau** (candidat 🟡, voire 🟢) :
- un **nouveau dossier / namespace de code** avec plusieurs fichiers, surtout une **interface**
  + un enregistrement d'injection de dépendances : c'est un nouveau système réutilisable ;
- de la **logique écrite à la main** qui branche sur des règles d'affaires ;
- un **changement d'architecture**, une intégration tierce **côté serveur** avec sa propre
  abstraction ;
- de la logique de **synchronisation** ou de conformité non triviale ;
- un **changement de schéma / modèle de données** (`schema.prisma`, migrations éditées à la
  main, `.sql`) ou de **dépendances** (`package.json`, `.csproj`) : nouvelle intégration ou
  impact données.

**Attention aux composants monofichiers** : `.vue`, `.svelte`, `.razor` contiennent leur logique
dans le même fichier que l'affichage. Le script les met **à lire** par défaut (il ne voit pas le
contenu). Un `.vue` peut être purement présentationnel (→ 🔴) ou plein de règles métier (→ 🟡+) :
c'est en l'ouvrant qu'on tranche, ne pas se fier à l'extension seule.

Un même diff peut mélanger les deux : retenir le niveau le plus élevé parmi les morceaux.

### 3. Proposer un niveau

Croiser type de projet × nature du changement dans la matrice → **proposer un niveau** avec une
**justification courte** (1-2 phrases) qui nomme la ligne de matrice utilisée.

En cas de PR mixte (plusieurs natures de changement), **retenir le niveau le plus élevé** parmi
les morceaux, et le dire.

Présenter à l'utilisateur :

```
PR : <titre> (<projet>, type : <type de projet>)
Changement : <résumé en 2-4 puces>

Niveau proposé : <🔴/🟡/🟢>
Justification : <pourquoi, en référence à la matrice>
```

**Attendre la confirmation ou l'ajustement de l'utilisateur.** Il peut retenir un autre niveau
que celui proposé ; c'est normal et attendu (l'écart proposé/retenu est justement une donnée
qu'on veut mesurer).

### 4. Appliquer la règle opérationnelle

Selon le **niveau retenu** :

- **🔴 Faible** : le review agentique suffit. Adresser (ou rejeter explicitement) les
  commentaires du review automatisé, puis la PR peut être mergée et la tâche fermée / déployée.
  Aucun review humain.

- **🟡 Modéré** : la PR peut être mergée sur la base du review agentique, mais un review humain
  est souhaitable **en différé**. **Proposer** de créer une tâche de suivi **non assignée** avec
  un lien vers la PR. **Ne jamais créer la tâche sans l'accord explicite de l'utilisateur.** Une
  fois l'accord donné, créer la tâche via le gestionnaire de tickets (ou en produire le contenu
  si l'outil est absent). La rattacher à la tâche/story parente si la PR en a une. Les
  commentaires du review différé pourront être adressés dans un commit (petit ajustement) ou une
  PR 🔴.

  Gabarit de la tâche de suivi (garder ce format pour la cohérence entre exécutions) :

  ```
  Titre : Review humain différé - PR <id> (<résumé court>, niveau 🟡)

  Description :
  - Niveau de review : 🟡 Modéré (co-pr-review-level). Mergée sur review agentique,
    review humain à faire en différé.
  - PR : <url>
  - Pourquoi 🟡 : <la même justification que celle journalisée>
  - À regarder en priorité : <2 à 4 points, tirés des fichiers « À LIRE » du digest>
  - Non assignée : à prendre par un dev pour le review différé.
  ```

- **🟢 Élevé** : un review humain est **requis avant de merger**. Ne pas merger sur la seule base
  du review agentique. Indiquer que la PR doit être assignée à un review humain.

### 5. Journaliser

Écrire **une ligne** dans la base Notion « Log des niveaux de review PR » (via l'outil Notion,
si disponible), avec :

- **PR** : titre court de la PR
- **Lien PR** : URL de la PR
- **Projet** : nom du projet
- **Type de projet** : valeur de la matrice
- **Niveau proposé** : le niveau suggéré par le skill
- **Niveau retenu** : le niveau confirmé par l'utilisateur
- **Justification** : la justification courte
- **Dev** : la personne responsable de la PR
- **Date** : la date du jour
- **Carte suivi (🟡)** : le lien de la tâche de suivi, si une a été créée (niveau modéré)

Si Notion est absent, produire la ligne en texte pour saisie manuelle.

## Ce que le skill ne fait pas

- Il ne remplace pas le review agentique (local + automatisé) : il présume qu'ils ont lieu.
- Il ne merge pas et ne ferme pas la PR à la place de l'utilisateur : il indique ce qui est
  permis selon le niveau.
- Il ne crée aucune tâche ni aucune entrée sans accord (sauf la ligne de journal, qui est le
  but explicite du skill).
