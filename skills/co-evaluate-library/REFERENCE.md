# Reference — /co-evaluate-library

Détails techniques pour le skill `/co-evaluate-library`. Le SKILL.md pointe ici quand nécessaire.

---

## Sources par écosystème

### npm (JavaScript / TypeScript)

| Source | Endpoint | Utilité |
|--------|----------|---------|
| Registry | `https://registry.npmjs.org/<name>` | Version, license, deps, maintainers, dernière publication |
| npmjs.com | `https://www.npmjs.com/package/<name>` | Stats downloads/sem (page HTML) |
| Bundlephobia | `https://bundlephobia.com/package/<name>` | Taille bundle, treeshaking |
| npm-stat | `https://npm-stat.com/charts.html?package=<name>` | Tendances downloads |
| Snyk | `https://security.snyk.io/package/npm/<name>` | CVE history |

Commande: `curl -s https://registry.npmjs.org/<name> | jq '...'`

### NuGet (.NET)

| Source | Endpoint | Utilité |
|--------|----------|---------|
| Registry v3 | `https://api.nuget.org/v3-flatcontainer/<name>/index.json` | Versions disponibles |
| Catalog | `https://api.nuget.org/v3/registration5-semver1/<name>/index.json` | Metadata complet (license, deps, dates) |
| nuget.org | `https://www.nuget.org/packages/<name>` | Stats downloads (page HTML) |

Commande: `curl -s https://api.nuget.org/v3/registration5-semver1/<name-lowercase>/index.json | jq '...'`

### PyPI (Python)

| Source | Endpoint | Utilité |
|--------|----------|---------|
| JSON API | `https://pypi.org/pypi/<name>/json` | Metadata, versions, classifiers, license |
| pepy.tech | `https://pepy.tech/project/<name>` | Stats downloads |

Commande: `curl -s https://pypi.org/pypi/<name>/json | jq '...'`

### Cross-écosystème

| Source | Endpoint / Tool | Utilité |
|--------|-----------------|---------|
| GitHub repo | `gh api /repos/<owner>/<repo>` | Stars, forks, last commit, open issues |
| GitHub releases | `gh api /repos/<owner>/<repo>/releases?per_page=5` | Fréquence releases |
| GitHub contributors | `gh api /repos/<owner>/<repo>/contributors?per_page=10` | Bus factor |
| GitHub Security Advisories | `gh api /repos/<owner>/<repo>/security-advisories` | CVE actives |
| WebSearch | built-in | "<lib> vs alternatives", "<lib> production issues" |
| WebFetch | built-in | Site officiel pour doc, privacy, pricing |

---

## Schema BD Notion `Régistre des librairies`

**URL**: https://www.notion.so/3e13180f1cd048af9bedfdfceee1c318
**Data source ID**: `bcc7aa67-d212-4815-9ee0-f2b911e602bc`

### Champs à remplir

| Champ Notion | Type | Valeurs possibles | Source |
|--------------|------|-------------------|--------|
| `Name` | title | nom de la lib | input utilisateur |
| `URL repo` | url | URL GitHub | détecté ou demandé |
| `Catégorie` | select | `Validation`, `UI`, `State`, `Auth`, `Build`, `Test`, `Util`, `API/HTTP`, `DB/ORM`, `Other` | inféré ou demandé |
| `Stack ciblée` | multi-select | `Vue`, `Nuxt`, `React`, `React Native`, `.NET`, `Umbraco`, `SQL Server`, `Prisma`, `Node`, `Other` | détecté projet |
| `Reco finale` | select | `🟢 Go`, `🟡 Go w/ caveats`, `🔴 No-go`, `⚪ À revoir` | calculé Étape 7 |
| `Stack fit` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `Maintenance` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `Adoption` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `Sécurité` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `Licence` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `Licence type` | rich text | `MIT`, `Apache 2.0`, `GPL-3.0`, etc. | détecté |
| `Privacy/Loi 25` | select | `🟢`, `🟡`, `🔴`, `⚪` | **check-in humain** |
| `Pérennité` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `TCO` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `Performance` | select | `🟢`, `🟡`, `🔴`, `⚪` | verdict |
| `Accessibilité` | select | `🟢`, `🟡`, `🔴`, `⚪`, `N/A` | check-in si UI, sinon N/A |
| `Notes / Caveats` | rich text | 2-5 lignes texte libre | synthèse |
| `Alternatives` | rich text | libs considérées en parallèle | optionnel |
| `Date évaluation` | date | date du jour | auto |
| `Projet` | relation | vers `Liste des projets` | demandé optionnellement |

### Exemple de payload pour créer la page Notion

Format générique, transposable selon l'outil de création de page disponible (connecteur Notion built-in, MCP Notion, etc.). La convention `parent.type: "data_source_id"` + `pages: [{ properties: {...} }]` suit l'API officielle Notion.

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "bcc7aa67-d212-4815-9ee0-f2b911e602bc"
  },
  "pages": [{
    "properties": {
      "Name": "zod",
      "URL repo": "https://github.com/colinhacks/zod",
      "Catégorie": "Validation",
      "Stack ciblée": "[\"Nuxt\",\"Vue\",\"Node\"]",
      "Reco finale": "🟢 Go",
      "Stack fit": "🟢",
      "Maintenance": "🟢",
      "Adoption": "🟢",
      "Sécurité": "🟢",
      "Licence": "🟢",
      "Licence type": "MIT",
      "Privacy/Loi 25": "🟢",
      "Pérennité": "🟡",
      "TCO": "🟢",
      "Performance": "🟡",
      "Accessibilité": "N/A",
      "Notes / Caveats": "Bus factor 2 — colinhacks principal. Bundle +12KB gzip à surveiller pour apps mobile-first.",
      "Alternatives": "yup, valibot, arktype",
      "date:Date évaluation:start": "2026-05-20"
    }
  }]
}
```

### Relation Projet (optionnelle)

BD `Liste des projets`: `294964e9-7e73-4fe2-b222-8cd02cab5ed3`

Pour brancher: passer une `Projet` value avec la liste JSON des URLs de pages projets. Demander à l'utilisateur lequel choisir avant le push.

---

## Heuristiques pour les verdicts

### Maintenance
- 🟢: dernière release < 6 mois, issues < 200, types officiels (TS lib)
- 🟡: 6-18 mois, ou docs minces, ou backlog important
- 🔴: > 18 mois sans release, ou abandonné explicitement

### Adoption
- 🟢: > 100k downloads/sem (npm) ou > 1M (NuGet) ou > 5k stars
- 🟡: 10k-100k downloads/sem ou 1k-5k stars
- 🔴: < 10k downloads/sem, projet obscur

### Sécurité
- 🟢: 0 CVE actives, < 3 CVE résolues historiques
- 🟡: CVE résolues récentes (< 6 mois) sans critique active
- 🔴: CVE actives non patchées (severity high+)

### Licence
- 🟢: MIT, Apache 2.0, BSD, ISC
- 🟡: LGPL, MPL, Apache avec patent clauses
- 🔴: GPL, AGPL (incompatible projets commerciaux fermés), propriétaire restrictif

### Pérennité (bus factor)
- 🟢: 5+ contributors actifs (commits derniers 6 mois)
- 🟡: 2-4 contributors actifs
- 🔴: 1 seul mainteneur (bus factor 1) ou abandonné

### TCO & réversibilité
- 🟢: gratuit/OSS, peu de surface d'intégration, alternatives faciles
- 🟡: freemium avec pricing raisonnable, ou OSS avec surface d'intégration moyenne
- 🔴: vendor lock-in fort, pricing aggressif, pas d'alternative équivalente

### Performance / bundle (front-end)
- 🟢: < 20KB gzip ou pas perf-critique
- 🟡: 20-100KB gzip ou perf modeste mais acceptable
- 🔴: > 100KB gzip ou perf-critique mais lent

### Privacy/Loi 25 (jugement humain requis)
- 🟢: pas de telemetry, données restent locales, conformité Loi 25/GDPR/DPA explicite
- 🟡: telemetry opt-out, ou floue sur le traitement
- 🔴: telemetry obligatoire vers cloud, données envoyées sans contrôle, pas de DPA disponible

### Accessibilité (UI libs seulement)
- 🟢: ARIA correct, focus management documenté, tests a11y
- 🟡: a11y partielle, certains composants OK
- 🔴: a11y absente ou cassée

---

## Notes opérationnelles

- L'utilisateur peut demander à pré-remplir le champ `Projet` quand il invoque le skill depuis un dossier projet qui matche un projet Notion
- En mode comparaison, créer N rows séparées (pas 1 row avec des arrays)
- Si l'utilisateur dit "skip le push Notion", afficher quand même le tableau en chat
- Les commandes `gh` requièrent que `gh auth status` soit OK — vérifier silencieusement avant
