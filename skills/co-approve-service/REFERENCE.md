# Reference - /co-approve-service

Le skill lit dans une BD (les audits) et écrit dans une autre (la liste pérenne).

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
| `Date évaluation` | aide à choisir si plusieurs audits |
| (URL/ID de la page) | cible de la relation `Audit` |

Valeurs possibles de `Verdict global`: `🟢 Vert (>60)`, `🟡 Jaune (45-60)`, `🟠 Orange (30-45)`, `🔴 Rouge (<30 ou no-go)`, `⚪ À évaluer`. Mapper la couleur en ignorant le suffixe entre parenthèses.

## BD cible: `Régistre des outils approuvés` (liste pérenne)

- **URL**: https://app.notion.com/p/8357446469cb4285a170664cfb5f943c
- **Data source ID**: `b131ae79-0ef0-407e-b83d-1d5022f854d2`
- Source de vérité des adoptions de l'équipe.

### Mapping des champs

| Champ Notion | Type | Source |
|--------------|------|--------|
| `Tool` | title | nom de l'outil |
| `Audit` | relation → `c88611ab-...` | page d'audit liée |
| `Verdict` | select (`🟢 Vert`, `🟡 Jaune`, `🟠 Orange`, `🔴 Rouge`) | repris de l'audit |
| `userDefined:URL` | url | `userDefined:URL` de l'audit |
| `Statut` | select (`Actif`, `En essai`, `Suspendu`, `Résilié`) | saisi (défaut `Actif`) |
| `Licence choisie` | rich text | saisi |
| `Frais` | number (dollar) | saisi |
| `Devise` | select (`CAD`, `USD`) | saisi |
| `Récurrence` | select (`mensuel`, `annuel`, `usage-based`, `one-time`, `gratuit`) | saisi |
| `Coût annualisé` | formula | **auto, ne pas remplir** |
| `Nb de sièges` | number | saisi |
| `Date d'abonnement` | date | saisi |
| `Date de renouvellement` | date | saisi |
| `Compte (courriel)` | email | saisi |
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
      "Frais": 18,
      "Devise": "USD",
      "Récurrence": "mensuel",
      "Nb de sièges": 5,
      "date:Date d'abonnement:start": "2026-06-03",
      "date:Date de renouvellement:start": "2027-06-03",
      "Compte (courriel)": "compte@exemple.com",
      "Raison d'utilisation": "Notes de réunion automatiques pour l'équipe.",
      "Données transmises (Loi 25)": "Audio + transcriptions de réunions internes. Pas de données client sensibles.",
      "date:Date d'approbation:start": "2026-06-03"
    }
  }]
}
```

`Audit`, `Responsable interne` et `Approuvé par` sont des relations/personnes: les setter en passant un **array JSON** (URLs de page pour la relation, IDs utilisateur pour les personnes). Pour les personnes, chercher l'ID via get-users d'abord (par nom ou courriel).

Exemple person + relation:
```json
"Approuvé par": "[\"<id-utilisateur>\"]",
"Audit": "[\"https://app.notion.com/p/<page_audit>\"]"
```
