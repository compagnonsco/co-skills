---
name: co-evaluate-library
description: Évaluer une lib (ou comparer 2-3 libs) avant adoption selon une grille à 10 critères qualitatifs (🟢🟡🔴⚪). Utiliser quand l'utilisateur dit "/co-evaluate-library", "évalue cette lib", "est-ce que je devrais utiliser X", "compare X et Y", ou veut un verdict structuré avant d'intégrer une dépendance. Couvre npm, NuGet, PyPI et autres écosystèmes.
---

**LANGUE**: Toujours répondre en français, ton naturel québécois. Aucun mot anglais sauf les noms techniques (npm, GitHub, CVE, etc.). L'input fourni par l'utilisateur donne la (ou les) lib à évaluer.

## Dépendances

- **Notion** (registres de gouvernance de l'équipe): le skill lit et écrit dans la BD `Régistre des librairies` (data source `bcc7aa67-d212-4815-9ee0-f2b911e602bc`). Nécessite un accès Notion dans le runtime (connecteur built-in, MCP installé, ou équivalent). Si Notion est absent, le skill produit quand même l'évaluation en chat, sans la vérification d'antériorité ni le push final.
- **Recherche web + accès registres paquets** (npm registry, api.nuget.org, pypi.org) et **GitHub** (idéalement `gh` CLI, sinon WebFetch): pour récupérer versions, sécurité, activité. Si absents, fiabilité réduite.
- **Agents secondaires** (optionnel): accélèrent le quick scan en le menant en parallèle si le runtime les supporte; sinon le skill investigue séquentiellement.

## Objectif

Produire un verdict structuré sur l'adoption d'une lib selon **10 critères qualitatifs** (verdict 🟢🟡🔴⚪ par critère + reco finale). Pas de score numérique — éviter la fausse précision. Output: tableau récap en chat + push automatique dans BD Notion `Régistre des librairies`.

Deux modes:
- **Deep dive** sur une lib (`/co-evaluate-library zod`)
- **Comparaison** de 2-3 libs (`/co-evaluate-library zod yup valibot`)
- **Interactif** si pas d'arg

Voir [REFERENCE.md](REFERENCE.md) pour les détails de sources par écosystème et le schema Notion. Voir [EXAMPLES.md](EXAMPLES.md) pour exemples concrets.

---

## Étape 1 — Parser l'input et déterminer le mode

Analyser l'input fourni par l'utilisateur:

- **0 nom**: mode interactif → demander "Quelle lib tu veux évaluer? Ou tu veux comparer 2-3 libs?"
- **1 nom**: mode deep dive
- **2-3 noms**: mode comparaison
- **4+ noms**: dire "trop de libs pour une comparaison utile, on en garde combien?" et trancher avec l'utilisateur

Pour chaque lib, **détecter l'écosystème** automatiquement:
- URL GitHub fournie → cloner mentalement et regarder `package.json` / `*.csproj` / `pyproject.toml` via `gh api` ou `WebFetch`
- Nom avec scope `@x/y` → npm
- Nom court (ex: `zod`) → tester npm en priorité (le plus courant)
- Si ambigu → demander à l'utilisateur

---

## Étape 1.5 — Vérifier si déjà évaluée dans Notion (PRIORITAIRE)

**Avant de lancer les agents secondaires** (qui coûtent du temps et des tokens), vérifier dans la BD `Régistre des librairies` si la lib a déjà été évaluée. Évite de refaire le travail et donne à l'utilisateur le contexte historique.

Pour chaque lib parsée:

1. **Chercher dans la data source Notion** `bcc7aa67-d212-4815-9ee0-f2b911e602bc` (BD `Régistre des librairies`, URL https://www.notion.so/3e13180f1cd048af9bedfdfceee1c318). Utiliser l'outil de recherche Notion disponible dans ton runtime (selon le client: outil `notion-search`/`search` du connecteur Notion built-in, du MCP Notion installé, ou équivalent), filtré sur cette data source, avec query = nom de la lib. Fallback si rien de probant: fetcher la data source au complet et parcourir les rows. Match: case-insensitive, ignorer scope npm si pertinent (ex: `@vee-validate/zod` peut matcher `vee-validate/zod`).

2. **Si match trouvé**, présenter à l'utilisateur:

   > **On a déjà évalué [Lib] le [Date évaluation]. Reco finale: [Reco finale].**
   >
   > Stack ciblée: [Stack ciblée si présent] · Licence: [Licence type si présent]
   > Notes/caveats: [résumé 1-2 lignes si présent]
   >
   > 📄 Page Notion: [URL de la page Notion existante]
   > 🔗 Repo: [URL repo si présent]
   >
   > Tu veux:
   > - **(a)** Juste consulter — on s'arrête ici
   > - **(b)** Refaire l'évaluation pour un contexte différent (autre stack, autre projet — préciser lequel)
   > - **(c)** Refaire parce qu'une nouvelle version majeure / CVE / changement de mainteneur est sorti (préciser quoi)
   >
   > Si (b) ou (c), je relance l'éval complète et on crée une nouvelle row (l'historique est conservé).

   **Attendre la réponse de l'utilisateur avant de continuer.** Si (a) → terminer le skill. Si (b) ou (c) → passer à Étape 2 en gardant en tête le contexte précis fourni (à intégrer dans les prompts des agents secondaires et la détection de stack).

3. **Si aucun match**, mentionner brièvement (« Pas d'éval existante pour [Lib], on part de zéro ») et enchaîner sur Étape 2.

4. **Mode comparaison (2-3 libs)**: faire la recherche pour chaque lib. Possible que certaines soient déjà évaluées et d'autres pas — présenter le portrait clair et demander à l'utilisateur quoi faire (réutiliser les anciens verdicts ou tout refaire à neuf pour homogénéité).

---

## Étape 2 — Détecter la stack du projet

Si invoqué dans un dossier projet:
- Lire `package.json` → Node/npm
- Lire `*.csproj` ou `*.sln` → .NET/NuGet
- Lire `pyproject.toml` ou `requirements.txt` → Python/PyPI
- Lire `nuxt.config.*`, `next.config.*`, `vite.config.*` → frontend stack
- Lire `prisma/schema.prisma` → ORM Prisma
- Identifier la version du framework principal

Si pas dans un projet (cwd = home, ou pas de manifest), demander:
> "Tu évalues pour quel projet/stack? (ex: Nuxt 4, .NET 8 + Umbraco, etc.)"

Le résultat alimente le critère **Stack fit**.

---

## Étape 3 — Quick scan parallèle

**Quick scan** (1-2 min). 3-4 sources à investiguer simultanément. **Si ton runtime supporte des agents secondaires parallèles** (ex: Claude Code `Agent`/Task, Cursor Background Agents): déléguer une source par agent secondaire. **Sinon**: investiguer séquentiellement avec output compact (5-10 lignes max par source). Voir [REFERENCE.md](REFERENCE.md) pour les endpoints exacts par écosystème.

Sources prioritaires (quick scan):
1. **Registre paquet** (npm registry, api.nuget.org, pypi.org) — version, license, dépendances, dernière publication
2. **GitHub** (via `gh api`) — releases récentes, contributors actifs, issues backlog, stars, last commit
3. **Sécurité** — GitHub Security Advisories (`gh api /repos/X/Y/security-advisories`) ou `npm audit` pour npm

Format de prompt pour chaque investigation (exemple npm):
> "Récupère ces infos pour la lib `<nom>` depuis npm registry (https://registry.npmjs.org/<nom>): version courante, license, deps directes/transitives count, dernière publication, mainteneurs listés. Retourne en 5-10 lignes max."

Agréger les retours.

---

## Étape 4 — Synthèse et détection de drapeaux rouges

Après le quick scan, évaluer les premiers critères:
- **Maintenance** 🟢 si release < 6 mois, 🟡 si 6-18 mois, 🔴 si > 18 mois ou 0 release
- **Adoption** 🟢 si > 100k downloads/sem ou > 5k stars, 🟡 entre, 🔴 obscure
- **Sécurité** 🟢 si 0 CVE actives, 🟡 si CVE résolues récentes, 🔴 si CVE actives non patchées
- **Licence** 🟢 si MIT/Apache/BSD, 🟡 si LGPL/MPL, 🔴 si GPL/AGPL/proprio incompatible
- **Pérennité** 🟢 si 5+ contributors actifs, 🟡 si 2-4, 🔴 si bus factor 1
- **TCO** 🟢 si gratuit/OSS, 🟡 si freemium raisonnable, 🔴 si vendor lock-in cher

**Drapeaux rouges** = au moins un critère 🔴 ou deux 🟡. Si oui → escalader (Étape 5). Si tout 🟢 → sauter à Étape 6.

---

## Étape 5 — Auto-escalade si red flag

Investiguer ces sources secondaires (en parallèle si agents secondaires supportés, sinon séquentiellement):
1. **Bundlephobia** (npm) ou équivalent — taille du bundle, treeshaking
2. **Reviews web** — recherche web pour "<lib> vs alternatives review 2025", "<lib> security audit", issues réelles vécues
3. **Lecture doc** — fetch du site officiel pour évaluer DX, types, exemples

Compléter les critères restants:
- **Stack fit** — match avec stack détectée à l'étape 2 (peer deps OK? version compat? API compatible avec le framework?)
- **Performance** 🟢 si bundle < 20KB gzip ou pas critique, 🟡 entre, 🔴 si > 100KB ou perf-critique
- **Accessibilité** (UI libs seulement) — chercher mentions a11y, ARIA, focus management

---

## Étape 5.5 — Contre-vérification des critères 🔴 critiques (OBLIGATOIRE)

**Si un critère critique tombe à 🔴 (Sécurité, Licence, Privacy/Loi 25, Pérennité), NE PAS conclure tout de suite.** Un seul 🔴 critique peut faire basculer la reco finale vers 🔴 No-go. L'enjeu est élevé. Faut creuser avant de confirmer.

### Pourquoi contre-vérifier?

Un verdict 🔴 basé sur une lecture rapide peut être injuste:
- "Absence d'info" ≠ "interdit explicitement"
- Une lib peut avoir un fork actif, une alternative communautaire, ou une version commercialement supportée
- Une CVE peut être patchée dans une version récente mais le scan retourne l'historique
- Une licence peut avoir une exception commerciale (ex: AGPL avec dual license)
- Le bus factor "1" peut masquer un sponsor stable (entreprise qui maintient en interne)

### Comment contre-vérifier

Lancer **2-3 investigations supplémentaires** sur le 🔴 suspect (en parallèle si agents secondaires supportés, sinon séquentiellement):

1. **Deep dive doc** — Relire EN PROFONDEUR le repo (LICENSE, SECURITY.md, CONTRIBUTING.md, doc officielle), chercher contradictions, identifier nuances
2. **Alternatives & forks** — Chercher si la communauté maintient un fork actif, une alternative drop-in (ex: pour une lib abandonnée), ou si un acteur commercial l'a repris
3. **Industry context** — Chercher comment d'autres projets gèrent ce même critère 🔴 (ex: une lib AGPL utilisée avec dual licensing, une CVE résolue dans une release récente non scannée, etc.)

### Distinguer 3 catégories de 🔴

| Catégorie | Action |
|-----------|--------|
| **🔴 définitif** | Problème confirmé sans remédiation viable (ex: CVE active critique, licence absolument incompatible). Verdict 🔴 No-go confirmé. Pas d'adoption. |
| **🔴 contournable** | Problème réel MAIS remédiation possible (ex: fork communautaire actif, version récente patchée, dual license commercial dispo). Verdict révisé à 🟡 Go w/ caveats avec conditions. |
| **🔴 d'apparence** | Lecture initiale superficielle. La contre-vérification révèle que le problème n'existe pas vraiment (ex: CVE déjà fixée, mainteneur supporté par entreprise stable). Verdict révisé à 🟢 ou 🟡. |

### Format de présentation à l'utilisateur

Après contre-vérification, présenter:

> **Critère X = 🔴 (suspect no-go)** — Contre-vérifié:
> - Source initiale: [URL + observation]
> - Contre-source 1: [URL + observation]
> - Contre-source 2: [URL + observation]
> - **Catégorie**: [🔴 définitif / 🔴 contournable / 🔴 d'apparence]
> - **Verdict révisé**: [verdict final + justification]
> - **Conditions de remédiation** (si 🔴 contournable): [actions précises, ex: "fork à utiliser X, version min Y, sponsor entreprise Z"]

---

## Étape 6 — Check-ins humains obligatoires

**Privacy/Loi 25** — TOUJOURS demander après avoir cherché:
> "Pour Privacy/Loi 25, ce que j'ai trouvé: [résumé en 2-3 lignes — telemetry détectée? Données envoyées au cloud? Conformité GDPR/DPA mentionnée?]. Tu veux flagger 🟢/🟡/🔴/⚪?"

**Accessibilité** — SI UI lib détectée:
> "C'est une lib UI. Pour l'a11y, j'ai trouvé: [résumé]. Verdict?"

Sinon mettre `N/A`.

---

## Étape 7 — Reco finale + sortie chat

Calculer la reco finale selon ces règles simples:
- Tout 🟢 ou 1-2 🟡 mineurs → **🟢 Go**
- Plusieurs 🟡 ou 1 🟡 critique (Sécurité/Licence/Privacy) → **🟡 Go w/ caveats**
- Au moins 1 🔴 sur Sécurité/Licence/Privacy/Pérennité → **🔴 No-go**
- Pas assez d'info → **⚪ À revoir**

Afficher tableau récap en chat:

```
**[nom-lib]** — [écosystème] — `<version>`

| Critère          | Verdict | Notes |
|------------------|---------|-------|
| Stack fit        | 🟢      | Compatible Nuxt 4, types OK |
| Maintenance      | 🟢      | release/sem, 5 mainteneurs |
| Adoption         | 🟢      | 8M dl/sem, 32k stars |
| Sécurité         | 🟢      | 0 CVE 2y |
| Licence          | 🟢      | MIT |
| Privacy/Loi 25   | 🟢      | no telemetry |
| Pérennité        | 🟡      | bus factor 2 |
| TCO              | 🟢      | Free, OSS |
| Performance      | 🟡      | +12KB gzip |
| Accessibilité    | —       | N/A (pas UI) |

→ **Reco: 🟢 Go** — caveat: bus factor à surveiller.
```

**Mode comparaison**: tableau côte-à-côte (1 colonne par lib + colonne Critère). Reco finale comparative à la fin.

---

## Étape 8 — Push Notion (avec confirmation)

**Confirmation obligatoire avant push** (demander confirmation avant toute action irréversible):

> "Je pousse l'évaluation dans la BD `Régistre des librairies`? (oui / non / ajuster d'abord)"

Si oui:
- Utiliser l'outil de création de page Notion disponible dans ton runtime (selon le client: `notion-create-pages`/`create-pages` du connecteur Notion built-in, du MCP Notion installé, ou équivalent)
- Cible: data source `bcc7aa67-d212-4815-9ee0-f2b911e602bc` (BD `Régistre des librairies`, https://www.notion.so/3e13180f1cd048af9bedfdfceee1c318)
- Mapper chaque critère du tableau aux champs Notion (voir [REFERENCE.md](REFERENCE.md) pour le schema complet)
- Date évaluation: date du jour
- Projet (relation): demander à l'utilisateur quel projet, ou laisser vide

**Mode comparaison**: pousser 1 row par lib (les 3 d'un coup).

Confirmer le push avec l'URL de chaque page créée.

---

## Règles

- **Toujours en français**, ton naturel
- **Pas de score numérique** — verdicts qualitatifs seulement
- **Investigations en parallèle si possible** — agents secondaires si le runtime les supporte, sinon séquentiel avec output compact
- **Check-ins humains obligatoires** pour Privacy/Loi 25 (toujours) et Accessibilité (si UI)
- **Confirmation avant push Notion** — demander confirmation avant toute action irréversible
- **Pas de demande inutile** — si la stack est détectable par lecture de fichiers, lire avant de demander
- **Auto-escalade smart** — pousser plus loin seulement si red flag détecté au quick scan
