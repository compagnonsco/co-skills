# Reference - /co-approve-service

Le skill lit dans deux BD (les audits, le registre ÉFVP) et écrit dans une troisième (la liste pérenne).

## BD source: `Régistre des outils (services tiers)` (les audits)

- **URL**: https://www.notion.so/d18c7a098fb14b7fa01e948e14699d1d
- **Data source ID**: `c88611ab-240d-413d-a45e-ae8608a437b6`
- Produite par `/co-evaluate-service`. C'est la source du verdict.

**Champs à lire** (pour l'approbation):

| Champ Notion | Usage dans /co-approve-service |
|--------------|--------------------------|
| `Name` | nom de l'outil (match) |
| `userDefined:URL` | reporté dans `URL` de l'approbation |
| `Verdict global` | détermine la règle d'approbation (vert/jaune/orange/rouge) |
| `Score total` | contexte affiché |
| `Notes / Caveats` | affiché comme caveats sur jaune/orange |
| `Conditions remédiation` | affiché comme caveats sur jaune/orange |
| `ÉFVP requise` | **gate de l'étape 3.5** (voir ci-dessous) |
| `Date évaluation` | aide à choisir si plusieurs audits |
| (URL/ID de la page) | cible de la relation `Audit` |

Valeurs possibles de `Verdict global`: `🟢 Vert (>60)`, `🟡 Jaune (45-60)`, `🟠 Orange (30-45)`, `🔴 Rouge (<30 ou no-go)`, `⚪ À évaluer`. Mapper la couleur en ignorant le suffixe entre parenthèses.

Valeurs possibles de `ÉFVP requise`: `🔴 Oui`, `🟡 Selon usage`, `🟢 Non`. **Vide = traiter comme `🟡 Selon usage`** (audit antérieur à l'ajout du champ, pas une dispense).

## BD de vérification: `Registre ÉFVP`

- **URL**: https://www.notion.so/c1b99a14fa1e42e895db35d08d9eb1a5
- **Data source ID**: `a1f45d7a-b325-4294-89e3-76364e2f439b`
- Produite par `/co-efvp`. Consultée en lecture seule par ce skill.

**Champs à lire**:

| Champ Notion | Usage dans /co-approve-service |
|--------------|--------------------------|
| `Outil / Système` | title, match case-insensitive sur le nom de l'outil |
| `Verdict` | `✅ Acceptable` / `⚠️ Conditions` / `🔴 Non acceptable` / `🔄 En évaluation` |
| `Notes` | conditions à afficher avec les caveats si verdict `⚠️ Conditions` |
| `Statut` | status. `In progress` = conditions pas toutes remplies |
| (URL/ID de la page) | cible de la relation `ÉFVP` |

`🔴 Non acceptable` bloque l'approbation sans override. `🔄 En évaluation` se traite comme une ÉFVP absente.

## BD cible: `Régistre des outils approuvés` (liste pérenne)

- **URL**: https://app.notion.com/p/8357446469cb4285a170664cfb5f943c
- **Data source ID**: `b131ae79-0ef0-407e-b83d-1d5022f854d2`
- Source de vérité des adoptions de l'équipe.

### Mapping des champs

| Champ Notion | Type | Source |
|--------------|------|--------|
| `Tool` | title | nom de l'outil |
| `Audit` | relation → `c88611ab-...` | page d'audit liée |
| `ÉFVP` | relation → `a1f45d7a-...` | page ÉFVP liée (étape 3.5) |
| `Verdict` | select (`🟢 Vert`, `🟡 Jaune`, `🟠 Orange`, `🔴 Rouge`) | repris de l'audit |
| `userDefined:URL` | url | `userDefined:URL` de l'audit |
| `Statut` | select (`Actif`, `En essai`, `Suspendu`, `Résilié`) | saisi (défaut `Actif`) |
| `Licence choisie` | rich text | saisi |
| `Frais par mois total (tous les sièges)` | number (dollar) | saisi |
| `Devise` | select (`CAD`, `USD`) | saisi |
| `Récurrence` | select (`mensuel`, `annuel`, `usage-based`, `one-time`, `gratuit`) | saisi |
| `Coût annualisé` | formula | **auto, ne pas remplir** |
| `Nb de sièges` | number | saisi |
| `Date d'abonnement` | date | saisi |
| `Date de renouvellement` | date | saisi |
| `Comptes (courriels)` | rich text | saisi (courriel(s) du ou des comptes) |
| `Responsable interne` | person | saisi |
| `Approuvé par` | person | l'utilisateur courant (auto) |
| `Date d'approbation` | date | date du jour (auto) |
| `Raison d'utilisation` | rich text | saisi |
| `Données transmises (Loi 25)` | rich text | saisi (données qui transitent) |

**Note**: champ URL = `userDefined:URL` dans le payload (convention Notion API). Le `Coût annualisé` est une formule (mensuel ×12, annuel ×1, one-time ×1, usage-based/gratuit = 0).

### Exemple de payload

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "b131ae79-0ef0-407e-b83d-1d5022f854d2"
  },
  "pages": [{
    "properties": {
      "Tool": "Granola",
      "Verdict": "🟡 Jaune",
      "userDefined:URL": "https://granola.ai",
      "Statut": "En essai",
      "Licence choisie": "Business annuel",
      "Frais par mois total (tous les sièges)": 18,
      "Devise": "USD",
      "Récurrence": "mensuel",
      "Nb de sièges": 5,
      "date:Date d'abonnement:start": "2026-06-03",
      "date:Date de renouvellement:start": "2027-06-03",
      "Comptes (courriels)": "compte@exemple.com",
      "Raison d'utilisation": "Notes de réunion automatiques pour l'équipe.",
      "Données transmises (Loi 25)": "Audio + transcriptions de réunions internes. Pas de données client sensibles.",
      "date:Date d'approbation:start": "2026-06-03"
    }
  }]
}
```

`Audit`, `ÉFVP`, `Responsable interne` et `Approuvé par` sont des relations/personnes: les setter en passant un **array JSON** (URLs de page pour les relations, IDs utilisateur pour les personnes). Pour les personnes, chercher l'ID via get-users d'abord (par nom ou courriel).

Exemple person + relations:
```json
"Approuvé par": "[\"<id-utilisateur>\"]",
"Audit": "[\"https://app.notion.com/p/<page_audit>\"]",
"ÉFVP": "[\"https://app.notion.com/p/<page_efvp>\"]"
```
