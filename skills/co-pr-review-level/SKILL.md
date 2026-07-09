---
name: co-pr-review-level
description: Analyse une pull request et propose son niveau de review requis (faible / modéré / élevé) selon la valeur du changement, puis applique la règle opérationnelle correspondante (merge direct, review humain différé, ou review humain avant merge). Journalise le niveau retenu pour un bilan ultérieur de la méthode. À utiliser à la création ou au triage d'une PR, pour décider combien de review humain elle mérite, ou quand l'utilisateur mentionne "niveau de review", "code review", "review level", "faut-il un review humain", "débordement de discipline", "reviewer cross-discipline".
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

À ce niveau de valeur s'ajoute un troisième axe : le **débordement de discipline**. Une PR qui
sort de la spécialité de son auteur (beaucoup de FE dans une PR d'un auteur BE, ou l'inverse) a
un angle mort et peut monter d'un cran (voir l'étape 3). Le niveau final est le plus élevé des
deux.

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

### 3. Évaluer le débordement de discipline

Un review vaut ce que vaut l'œil qui le fait. Une PR qui sort de la discipline de son auteur a
un angle mort : l'auteur couvre mal la partie hors de sa spécialité. Cet axe s'ajoute à la
valeur du changement (étape suivante), il ne la remplace pas.

1. **Discipline de l'auteur.** La déduire du roster dans
   [`references/disciplines-reviewers.md`](references/disciplines-reviewers.md), à partir de
   l'auteur de la PR (déjà connu : c'est le champ « Dev » journalisé). Auteur absent du roster
   → **demander** : « Tu te dirais plus FE ou BE, ou à l'aise des deux ? ». Auteur à l'aise des
   deux / full-stack → **pas de débordement possible**, sauter cette étape.

2. **Part off-discipline du diff.** Parmi les fichiers « À LIRE » du digest (code écrit à la
   main), repérer ceux de la discipline **opposée** à l'auteur (guide de classement dans le
   fichier de référence). Markup, contenu, config et glue triviale ne comptent pas.

3. **Calibrer selon la profondeur du travail off-discipline, pas le nombre de fichiers :**
   - **De base** → pas d'escalade, l'IA + le review automatisé couvrent, peu importe que ça
     touche l'autre discipline. Ex. BE : CRUD simple, config, mapping trivial, glue. Ex. FE :
     affichage, style/CSS, texte, binding simple, composant présentationnel, ajustement UX.
   - **Avancé** du côté opposé → **monter d'un cran** et **cibler un reviewer de la discipline
     débordée** (via le roster). Ex. BE : logique métier non triviale, nouveau système ou
     abstraction, changement d'architecture ou de schéma, refacto serveur. Ex. FE : store ou
     état réactif non trivial, composable qui porte des règles d'affaires, logique de
     formulaire/validation complexe, refacto de composants, nouvelle archi front (routing,
     SSR). Ce sont les mêmes signaux qui élèvent le niveau à l'étape 2 (« Signaux de lecture
     du diff »), appliqués au côté faible de l'auteur.

### 4. Proposer un niveau

Croiser type de projet × nature du changement dans la matrice → **proposer un niveau** avec une
**justification courte** (1-2 phrases) qui nomme la ligne de matrice utilisée.

En cas de PR mixte (plusieurs natures de changement), **retenir le niveau le plus élevé** parmi
les morceaux, et le dire.

Le niveau retenu est le **plus élevé** entre le niveau de valeur (matrice, étape 2) et le niveau
après débordement de discipline (étape 3). S'il vient du débordement, nommer le reviewer visé
dans la justification.

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

### 5. Appliquer la règle opérationnelle

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

  **Débordement de discipline (étape 3).** Si la PR déborde de façon significative, la carte de
  suivi vise un reviewer de la discipline débordée (roster). Si la PR a de la logique
  significative **des deux côtés** (FE et BE), créer **deux cartes** : une par discipline (ex.
  « review FE → Anne » et « review BE → un collègue BE »), chacune assignable et fermable
  indépendamment.

- **🟢 Élevé** : un review humain est **requis avant de merger**. Ne pas merger sur la seule base
  du review agentique. Indiquer que la PR doit être assignée à un review humain. Si le niveau
  vient (aussi) d'un débordement de discipline, le review humain avant merge doit inclure un
  reviewer de la discipline débordée.

### 6. Journaliser

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
- **Débordement** : discipline débordée + reviewer visé, si applicable (sinon —)

Si Notion est absent, produire la ligne en texte pour saisie manuelle.

## Ce que le skill ne fait pas

- Il ne remplace pas le review agentique (local + automatisé) : il présume qu'ils ont lieu.
- Il ne merge pas et ne ferme pas la PR à la place de l'utilisateur : il indique ce qui est
  permis selon le niveau.
- Il ne crée aucune tâche ni aucune entrée sans accord (sauf la ligne de journal, qui est le
  but explicite du skill).
