---
name: co-pr-canvas
description: >-
  Présente la revue de diff d'une pull request Azure DevOps sous forme de
  Cursor Canvas : regroupe les changements selon l'importance pour le
  relecteur, sépare le bruit du cœur métier et met en avant le code délicat
  ou inattendu. À utiliser pour une revue Azure Repos, un résumé de diff ADO,
  ou lorsque l'utilisateur demande un canvas de revue PR, une passe sur le
  diff ou une vue d'ensemble des changements pour des liens PR
  dev.azure.com ou visualstudio.com ; invoquer aussi sous le nom co-pr-canvas.
---

# Canvas de revue de PR Azure DevOps

Construire un canvas qui présente le diff d'une PR réorganisé pour la compréhension du relecteur — pas dans l'ordre de l'arborescence des fichiers. Équivalent Azure DevOps Repos du skill GitHub `pr-review-canvas` : même structure de revue et règles canvas, outillage différent pour récupérer la PR.

## Prérequis

Lire d'abord `~/.cursor/skills-cursor/canvas/SKILL.md`. On y trouve la politique de génération, les repères de design, les règles anti-bruit, l'auto-vérification et les conventions de chemins de fichiers à respecter. La surface complète des composants et hooks est déclarée dans `~/.cursor/skills-cursor/canvas/sdk/index.d.ts` et les autres fichiers `.d.ts` du même dossier — les lire pour connaître les exports et les formes de props exacts plutôt que d'inventer.

## Azure DevOps CLI

Utiliser l'**extension Azure DevOps pour Azure CLI** (`azure-devops`). Elle s'installe automatiquement au premier appel à `az repos` ou `az devops` ([Microsoft Learn](https://learn.microsoft.com/en-us/cli/azure/azure-cli-extensions-overview)).

Si les commandes échouent parce qu'**Azure CLI n'est pas installé** (par ex. `az` introuvable, erreur du type « command not found ») ou parce que l'**extension `azure-devops` est absente ou cassée** (message indiquant l'extension, échec systématique de `az repos` / `az devops`), **s'arrêter** et expliquer à l'utilisateur comment installer ou réparer l'outil, sans poursuivre la revue sur des données inventées. Indiquer au minimum : installer [Azure CLI](https://learn.microsoft.com/fr-fr/cli/azure/install-azure-cli) selon son OS, puis ajouter ou mettre à jour l'extension avec `az extension add --name azure-devops` (ou `az extension update --name azure-devops` si elle est déjà présente mais obsolète).

Authentification (choisir ce que l'utilisateur utilise déjà) :

- **Azure AD :** `az login`, puis vérifier que le compte peut lire l'organisation.
- **PAT :** `az devops login --organization <ORG_URL>` (enregistre un jeton pour les appels REST DevOps).

Si les commandes échouent (auth ou droits), s'arrêter et indiquer à l'utilisateur d'exécuter `az login` et/ou `az devops login` pour cette organisation — ne pas inventer le contenu de la PR.

## Analyser l'URL de la PR

Attendre une **URL complète** de pull request Azure Repos. Formes courantes :

- `https://dev.azure.com/<Org>/<Project>/_git/<Repo>/pullrequest/<PullRequestId>`
- `https://dev.azure.com/<Org>/<Project>/_git/<Repo>/pullrequest/<PullRequestId>?_a=files` (et autres paramètres de requête — retirer `?…` avant l'analyse)
- `https://<Org>.visualstudio.com/<Project>/_git/<Repo>/pullrequest/<PullRequestId>`

Extraire :

| Élément | Règle |
| --- | --- |
| **URL d'organisation** (`--org`) | `https://dev.azure.com/<Org>/` ou `https://<Org>.visualstudio.com/` (barre oblique finale facultative selon le quoting du shell ; les deux conviennent à Azure CLI) |
| **Projet** | Segment de chemin juste après le segment hôte d'org (`<Project>`) |
| **Nom du dépôt** | `<Repo>` dans `/_git/<Repo>/` |
| **Identifiant de la pull request** (`--id`) | Entier à la fin de `/pullrequest/<id>` |

**Si l'utilisateur n'a pas fourni d'URL de PR, s'arrêter et demander.** Ne pas deviner à partir de la branche courante ou de l'historique du chat. Attendre un lien PR explicite ou des valeurs explicites `org`, `project`, `repository` et `id`.

## Configurer les valeurs par défaut de la CLI à partir de l'URL

Pour que les commandes `az repos pr …` ne dépendent pas d'un remote git ambigu, fixer les défauts pour cette exécution (PowerShell ou bash) :

```bash
az devops configure --defaults organization=<ORG_URL> project=<PROJECT>
```

Utiliser les valeurs analysées. Le nom du dépôt n'est pas toujours une clé de défaut séparée pour toutes les commandes `az repos` ; récupérer le **GUID** du dépôt via `az repos pr show` (voir ci-dessous) pour les appels à `az devops invoke`.

## Collecter les métadonnées de la PR (obligatoire)

Exécuter :

```bash
az repos pr show --id <PullRequestId> --org <ORG_URL> -o json
```

Depuis le JSON, retenir au minimum : `title`, `description`, `status`, `isDraft`, `sourceRefName`, `targetRefName`, `creationDate`, `createdBy`, `reviewers`, `labels`, `repository.id`, `repository.name`, `lastMergeSourceCommit`, `lastMergeTargetCommit`, `forkSource`, et les champs liés au merge s'ils sont présents.

Contexte optionnel (appeler quand c'est utile pour le canvas) :

```bash
az repos pr reviewer list --id <PullRequestId> --org <ORG_URL> -o json
az repos pr work-item list --id <PullRequestId> --org <ORG_URL> -o json
```

## Collecter le diff (texte du patch)

`az repos pr` n'a **aucune** sous-commande équivalente à `gh pr diff`. Utiliser l'une des options suivantes, par ordre de préférence :

### 1) Clone git local du même dépôt (mieux pour un diff unifié complet)

Si l'espace de travail (ou un chemin indiqué par l'utilisateur) est un clone dont l'URL `origin` correspond à ce projet/dépôt, utiliser git avec les refs de pull Azure DevOps ([récupérer la PR en local](https://learn.microsoft.com/en-us/azure/devops/repos/git/pull-requests?view=azure-devops&tabs=git-command-line#checkout-locally-on-the-command-line)) :

```bash
git fetch origin refs/pull/<PullRequestId>/merge:refs/remotes/origin/pr/<PullRequestId>
git diff origin/<target-branch>...refs/remotes/origin/pr/<PullRequestId>
```

Déduire `<target-branch>` depuis `targetRefName` dans `az repos pr show` (retirer le préfixe `refs/heads/`). Adapter le nom du remote s'il n'est pas `origin`.

Si les refs de pull ne sont pas disponibles sur ce serveur, récupérer les branches à partir de `sourceRefName` / `targetRefName`, puis :

```bash
git diff <merge-base> <source-commit>
```

Utiliser `git merge-base` correctement ; en cas de doute, privilégier la même sémantique d'ancêtre commun que le serveur.

### 2) Commits issus de `az repos pr show` (rapide, peut manquer des cas limites si les branches ont bougé)

Quand git est disponible et que les remotes/commits sont fiables, on peut utiliser :

```bash
git diff <lastMergeTargetCommit.commitId> <lastMergeSourceCommit.commitId>
```

Uniquement si la PR est encore bien représentée par ces SHA ; sinon, revenir aux changements d'itération (ci-dessous) ou demander à l'utilisateur de mettre à jour son fetch.

### 3) `az devops invoke` — liste de fichiers et métadonnées d'itération (disponible dès qu'il y a une auth)

Utiliser la surface REST Git via `az devops invoke` pour une **liste de fichiers modifiés** fiable sans clone local. Si un nom de `--resource` échoue après une mise à jour d'extension, le redécouvrir :

```bash
az devops invoke --org <ORG_URL> --query "[?area=='git' && contains(resource, 'pull')].{resource:resource, routeTemplate:routeTemplate}" -o table
```

**Lister les itérations** (`repositoryId` peut être le GUID ou le nom du dépôt depuis `az repos pr show` ; `project` est le segment d'URL du projet) :

```bash
az devops invoke --org <ORG_URL> --area git --resource pullRequestIterations --route-parameters project=<PROJECT> repositoryId=<REPO_ID_OR_NAME> pullRequestId=<PullRequestId> --query-parameters includeCommits=true --api-version 7.1 --http-method GET -o json
```

Choisir la **dernière** itération : le plus grand `id` dans le tableau retourné (les nouveaux push créent de nouvelles itérations).

**Lister les changements** pour cette itération. Paginer avec `$top` / `$skip` (et `nextTop` / `nextSkip` dans la réponse) tant que `nextTop` n'est pas 0 :

```bash
az devops invoke --org <ORG_URL> --area git --resource pullRequestIterationChanges --route-parameters project=<PROJECT> repositoryId=<REPO_ID_OR_NAME> pullRequestId=<PullRequestId> iterationId=<ITERATION_ID> --query-parameters '$top=2000' --api-version 7.1 --http-method GET -o json
```

Les entrées de changement donnent chemins, types de changement et identifiants d'objets — suffisant pour structurer le canvas. Ce n'est **pas** un diff unifié complet. Si des **hunks ligne par ligne** sont nécessaires et que git n'est pas disponible, le dire clairement dans le canvas et résumer à partir des métadonnées plutôt que d'inventer un diff.

**Commits sur la PR** (chronologie optionnelle pour le canvas) : mêmes paramètres de route avec la ressource `commits` et les paramètres de requête `$top` / `continuationToken` comme dans [DevOps Notes](https://oshamrai.wordpress.com/2023/07/19/using-az-devops-invoke-to-work-with-azure-devops-rest-api/).

## Regrouper les changements pour la compréhension

Ne **pas** présenter les fichiers par ordre alphabétique ou arborescence. Réorganiser en sections ordonnées par valeur pour le relecteur :

1. **Cœur métier** — Nouveau comportement, changements d'algorithme, transitions d'état, évolution de surface d'API. Montrer les diffs complets avec le contexte autour.
2. **Câblage et intégration** — Enregistrement de routes, injection de dépendances, branchements de configuration qui relient le cœur métier. Version condensée — assez pour valider la cohérence.
3. **Boilerplate et mécanique** — Réordonnancement d'imports, renommages, code généré, formatage, réexport de types. Résumer par liste de noms de fichiers et statistiques. Pas de diffs inline sauf si vraiment pertinent.

Commencer par le cœur métier. L'attention du relecteur est maximale en haut de page.

## Distiller la logique complexe en pseudo-code

Quand un changement central implique une logique dense ou tordue — conditions profondément imbriquées, machines à états, boucles retry/backoff, transformations en plusieurs étapes — ajouter un court pseudo-code à côté du diff. Le pseudo-code retire la syntaxe du langage, la gestion d'erreurs et le bruit pour exposer l'algorithme ou le flux de contrôle essentiel en quelques lignes. Cela permet de valider l'intention avant de lire le code réel.

Ne le faire que lorsque le diff réel est difficile à parcourir. Les changements simples n'ont pas besoin de miroir en pseudo-code.

## Tracer une logique délicate sur un exemple concret

Le pseudo-code donne la forme du changement ; un exemple de trace montre son exécution. Quand un hunk modifie le comportement de façon difficile à anticiper à la lecture — effets réordonnés, nouveaux courts-circuits, cas limites modifiés — choisir une entrée concrète et la faire passer dans les chemins ancien et nouveau côte à côte, en soulignant l'étape où ils divergent et le résultat observable. Garder l'entrée petite et réaliste.

Réserver cela aux changements de comportement vraiment surprenants, pas à chaque hunk central.

## Signaler les points délicats

Quand un hunk contient quelque chose de surprenant, risqué ou facile à manquer, le séparer visuellement du diff environnant et l'associer à une courte étiquette (par ex. « Subtil », « Changement cassant », « Condition de course », « Performance ») et une phrase d'explication pour que le relecteur voie le risque et le code ensemble.

Réserver ces encadrés aux vrais sujets délicats — en abuser tue le signal.

## Ton et contenu

Rédiger pour le relecteur, pas comme un journal de release. Mettre l'accent sur :

- **Pourquoi** cela a changé, pas seulement quoi a changé.
- Les interactions entre fichiers — par ex. « Le nouveau validateur dans `core.ts` est appelé par la route ajoutée dans `routes.ts`. »
- Tout ce que le diff seul ne rend pas évident.

Rester concis. Une ou deux phrases par remarque.

## Être créatif

Les sections ci-dessus sont un plancher, pas un plafond. L'objectif est le chemin le plus court pour que le relecteur comprenne **ce** changement précis — donc regarder le diff et choisir la représentation qui aide vraiment. Un petit diagramme d'états, un graphe d'appels avant/après, un tableau entrée→sortie, une frise des commits, une note de confiance par fichier, un gros encadré unique avec le reste replié — ce qui colle au changement.

Le SDK canvas offre graphiques, tableaux, vues de diff, mise en page DAG, cartes, statistiques, état interactif, etc. Choisir les composants qui servent le mieux le sujet. Une revue de refactor ne ressemble pas à une revue de correctif ni à une revue de nouvelle fonctionnalité — le canvas doit le refléter.
