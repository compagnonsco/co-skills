# REFERENCE — /co-efvp

## IDs Notion

| BD | Data source ID | URL page |
|----|---------------|----------|
| Audits des outils (services tiers) | `c88611ab-240d-413d-a45e-ae8608a437b6` | https://www.notion.so/d18c7a098fb14b7fa01e948e14699d1d |
| Registre ÉFVP | `a1f45d7a-b325-4294-89e3-76364e2f439b` | https://www.notion.so/c1b99a14fa1e42e895db35d08d9eb1a5 |
| Politiques d'usage acceptable | `11dd28ba-c387-4b0b-ba3b-84b4bbd62ddb` | (page parente ÉFVP) |
| Régistre des services approuvés | `b131ae79-0ef0-407e-b83d-1d5022f854d2` | https://www.notion.so/8357446469cb4285a170664cfb5f943c |

**ID utilisateur (Responsable)**: chercher via l'outil get-users (par nom ou courriel) au moment du push.

---

## Schema BD — Registre ÉFVP

| Champ | Type Notion | Valeurs / Notes |
|-------|-------------|-----------------|
| `Outil / Système` | title | Nom de l'outil (ex: "Claude Team — Anthropic") |
| `Fournisseur` | rich_text | Entité légale + siège (ex: "Anthropic PBC (San Francisco, CA, USA)") |
| `Verdict` | select | `✅ Acceptable`, `⚠️ Conditions`, `🔴 Non acceptable`, `🔄 En évaluation` |
| `Date ÉFVP` | date | Date ISO (YYYY-MM-DD) |
| `RPRP` | person | Array d'IDs utilisateur Notion (responsable de la protection des RP) |
| `Lié à l'audit` | relation | Array d'URLs pages audit (BD `c88611ab-...`) |
| `Scope` | select | usage interne à l'organisation, ou projet client. Reprendre les **libellés exacts** des options du select tels qu'ils existent dans la BD (dans le registre actuel: `Interne Compagnons`, `Projet client`) |
| `Priorité` | select | `🔴 Haute`, `🟡 Moyenne`, `🟢 Basse` |
| `Statut` | **status** | `Not started`, `In progress`, `Done` |
| `Révision prévue` | date | Date ISO. Défaut: +3 mois si ⚠️ Conditions, +12 mois si ✅ |
| `Notes` | rich_text | Résumé du verdict + liste numérotée des conditions à remplir |

`Statut` est de type **status**, pas select: il suit l'avancement des conditions. `⚠️ Conditions` avec
conditions non remplies = `In progress`. Toutes remplies (ou `✅ Acceptable` sans condition) = `Done`.

Il n'y a **pas** de champ `Conditions` distinct: les conditions vont dans `Notes`, en liste numérotée,
précédées d'une ligne de contexte (verdict d'audit + score + date). Le détail complet des 9 sections
va dans le **body** de la page, pas dans les propriétés.

**Payload exemple** (création de page). L'enveloppe est la même que dans les deux autres skills de la suite: `parent` + `pages`, jamais `dataSourceId` + `properties` à la racine.

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "a1f45d7a-b325-4294-89e3-76364e2f439b"
  },
  "pages": [{
    "properties": {
      "Outil / Système": "Claude Team — Anthropic",
      "Fournisseur": "Anthropic PBC (San Francisco, CA, USA)",
      "Verdict": "⚠️ Conditions",
      "date:Date ÉFVP:start": "2026-06-24",
      "RPRP": "[\"<id-utilisateur>\"]",
      "Lié à l'audit": "[\"https://app.notion.com/p/<page_audit>\"]",
      "Scope": "Interne Compagnons",
      "Priorité": "🟡 Moyenne",
      "Statut": "In progress",
      "date:Révision prévue:start": "2026-09-24",
      "Notes": "Basé sur audit 🟡 Jaune (59/75, 2026-06-20).\n\nConditions à remplir:\n1. Activer les notifications de brèche côté admin.\n2. Former les utilisateurs avant l'ouverture générale."
    }
  }]
}
```

**Mise à jour** d'une ÉFVP existante (étape 1.5): viser la page par son ID avec l'opération de mise à jour de propriétés, en passant seulement les champs qui changent. Ne pas repasser par une création.

---

## Schema BD — Politiques d'usage acceptable

| Champ | Type Notion | Valeurs / Notes |
|-------|-------------|-----------------|
| `Outil / Système` | title | Même libellé que dans le Registre ÉFVP |
| `Version` | rich_text | ex: "1.0" |
| `Statut` | **status** | `Not started`, `In progress`, `Done` |
| `Responsable` | person | Array d'IDs utilisateur Notion |
| `Date de publication` | date | Date ISO. S'écrit `date:Date de publication:start` dans un payload |
| `Révision prévue` | date | Date ISO. S'écrit `date:Révision prévue:start`. Aligner sur la `Révision prévue` de l'ÉFVP |
| `ÉFVP associée` | **url** | URL de la page ÉFVP. C'est une url, pas une relation |
| `Notes` | rich_text | Contexte court |

Comme pour le Registre ÉFVP, les champs date prennent le préfixe `date:` et le suffixe `:start`. Écrire
`"Date de publication": "2026-07-27"` ne plante pas: le champ reste **silencieusement vide**.

**Payload exemple**:
```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "11dd28ba-c387-4b0b-ba3b-84b4bbd62ddb"
  },
  "pages": [{
    "properties": {
      "Outil / Système": "Claude Team — Anthropic",
      "Version": "1.0",
      "Statut": "Done",
      "Responsable": "[\"<id-utilisateur>\"]",
      "date:Date de publication:start": "2026-06-24",
      "date:Révision prévue:start": "2026-09-24",
      "ÉFVP associée": "https://app.notion.com/p/<page_efvp>",
      "Notes": "Politique liée à l'ÉFVP du 2026-06-24."
    }
  }]
}
```

Le corps de la politique (qui peut l'utiliser, quoi éviter, données interdites, responsabilité) va dans
le **body** de la page.

---

## Template 9 sections — contenu body de la page ÉFVP

### § 1 — Identification

| Champ | Valeur |
|-------|--------|
| Outil / Fournisseur | [Nom + URL officielle] |
| Catégorie | [AI/LLM, Comm, Dev tools, etc.] |
| Date ÉFVP | [YYYY-MM-DD] |
| Responsable ÉFVP | l'utilisateur courant |
| Basée sur l'audit | [lien vers la page d'audit dans Audits des outils] |
| Loi applicable | Loi 25 (Loi modernisant des dispositions législatives en matière de protection des renseignements personnels, Québec) — art. 17 |

---

### § 2 — Description du traitement

- **Rôle de l'organisation**: [Responsable du traitement / Sous-traitant / Les deux]
- **Rôle du fournisseur**: [Sous-traitant de données / Responsable conjoint]
- **Usage prévu**: [Description courte — ex: "Assistant IA pour les équipes internes: rédaction, analyse, code"]
- **Utilisateurs**: [Qui utilise l'outil chez l'organisation]
- **Compte**: [Compte org / comptes individuels / les deux]
- **Administrateurs**: [Qui gère le compte]

---

### § 3 — Inventaire des renseignements personnels (RP)

| Catégorie | Exemples concrets | Acteur concerné | Probabilité | Sensible? |
|-----------|------------------|-----------------|-------------|-----------|
| [Noms, emails pro] | [Noms d'employés dans les prompts] | Employés de l'organisation | Élevée | Non |
| [PII clients] | [Infos clients dans les prompts de debug] | Utilisateurs finaux clients | Faible | Selon le cas |
| [Données sensibles] | [Dossiers médicaux, financiers] | Individus | À éviter | Oui |

**Remarque**: Lister seulement les catégories réalistes selon le contexte de déploiement.

---

### § 4 — Flux de données et transferts

- **Hébergement**: [Région(s) selon audit critères 1+5]
- **Transfert hors Québec**: [Oui / Non] — [Juridiction: ex. États-Unis (US-Ouest, AWS/Azure)]
- **Base légale du transfert** (Loi 25 art. 17): [DPA signé / Clauses contractuelles types / À signer]
- **Sous-processeurs principaux**: [Liste selon audit ou site fournisseur]
- **Flux**: l'organisation → [Outil/Serveurs] → [Sous-processeurs si applicable]

---

### § 5 — Mesures de protection

#### Contractuelles
- [ ] DPA (Data Processing Agreement) signé ou auto-incorporé
- [ ] Clauses de suppression à la résiliation
- [ ] Obligation de notification de brèche (délai contractuel)
- [ ] Certification: [SOC 2, ISO 27001, etc. — selon audit critère 10]

#### Techniques (selon audit critères 1-2-3)
- Chiffrement en transit: [TLS 1.2+]
- Chiffrement au repos: [AES-256 ou équivalent]
- ZDR (Zero Data Retention): [Disponible / Non disponible / Disponible sur plan X]
- Conservation côté fournisseur: [Durée selon audit critère 3]

#### Organisationnelles (selon réponses contexte)
- [ ] SSO/MFA activé (compte org)
- [ ] Canal de notification brèche configuré
- [ ] Politique d'usage acceptable diffusée
- [ ] Formation des utilisateurs
- [ ] Procédure suppression compte lors d'un départ

---

### § 6 — Droits des personnes concernées

- **Droit d'accès / rectification / suppression**: [Comment c'est adressé selon le bloc C de l'étape 3 et la doc du fournisseur]
- **Délai de réponse contractuel**: [Si dans le DPA]
- **Contact DPO fournisseur**: [privacy@fournisseur.com si connu]
- **Contact responsable vie privée de l'organisation**: [courriel du responsable désigné]

---

### § 7 — Évaluation des risques

| Risque | Probabilité | Impact | Niveau | Mitigation |
|--------|-------------|--------|--------|------------|
| Transfert hors QC sans encadrement | [F/M/É] | [F/M/É] | [F/M/É/C] | [DPA, clauses contractuelles] |
| Entraînement LLM sur nos données | [F/M/É] | [F/M/É] | [F/M/É/C] | [Clause no-training, vérification param] |
| Rétention excessive | [F/M/É] | [F/M/É] | [F/M/É/C] | [ZDR si dispo, suppression manuelle] |
| Prompt injection / fuite données | [F/M/É] | [F/M/É] | [F/M/É/C] | [Formation, politique d'usage] |
| Accès non autorisé | [F/M/É] | [F/M/É] | [F/M/É/C] | [SSO/MFA, comptes org] |
| Données client exposées | [F/M/É] | [F/M/É] | [F/M/É/C] | [Politique d'usage, scope limité] |

**Légende**: F=Faible, M=Modéré, É=Élevé, C=Critique

---

### § 8 — Décision et conditions

**Verdict ÉFVP**: [✅ Acceptable / ⚠️ Conditions / 🔴 Non acceptable]

**Justification**:
[1-3 phrases expliquant la décision]

**Conditions à remplir** (si ⚠️):
- [ ] Condition 1 — [responsable] — [échéance]
- [ ] Condition 2 — [responsable] — [échéance]

**Décision applicable à**: [scope exact — ex: "équipes internes de l'organisation, comptes @exemple.com, usage professionnel seulement"]

---

### § 9 — Suivi et révision

| Événement déclencheur | Action |
|-----------------------|--------|
| Changement de politique fournisseur | Revoir §§ 4-5-7 et mettre à jour |
| Nouveaux types de données | Revoir § 3 et § 7 |
| Changement de plan (ex: Team → Enterprise) | Nouvelle ÉFVP |
| Brèche de données | Révision post-incident |
| Délai max sans révision | 2 ans |

**Prochaine révision**: [reprendre la date du champ `Révision prévue` de la page]

Deux horizons distincts, à ne pas confondre. Le champ `Révision prévue` porte la **prochaine révision de suivi**: +3 mois quand le verdict est `⚠️ Conditions` (pour vérifier où en sont les conditions), +12 mois quand il est `✅ Acceptable`. Le « 2 ans » ci-dessus est le **délai maximal** au-delà duquel une ÉFVP est périmée même sans événement déclencheur. La date écrite dans le body doit être celle du champ, jamais date + 2 ans.

---

## Grille de mapping audit → risque ÉFVP

Les numéros ci-dessous sont ceux de la grille d'audit réelle (voir `co-evaluate-service/REFERENCE.md`).
Se tromper de numéro fait lire la mauvaise colonne sans aucune erreur visible: le risque est calculé
sur un score qui mesure autre chose.

| Dimension audit | Score | Risque ÉFVP associé | Impact si ≤ 2 |
|----------------|-------|---------------------|---------------|
| 2 — Chiffrement | ≤ 2 | Fuite en transit/repos | Élevé |
| 3 — Conservation | ≤ 2 | Rétention excessive | Élevé |
| 4 — Droit d'utilisation | ≤ 2 | Le fournisseur s'octroie un usage des données au-delà de la prestation | Critique |
| 5 — Emplacement | ≤ 2 | Transfert hors QC non couvert | Critique |
| 7 — Entraînement | ≤ 2 | Entraînement LLM sur données | Élevé |
| 8 — Partage 3rd | ≤ 2 | Communication à des tiers non maîtrisée | Élevé |
| 10 — Conformité documentée | ≤ 2 | Absence de certifications et d'encadrement contractuel (SOC2, ISO, DPA) | Modéré |

**Logique**: Score ≤ 2 sur une dimension critique = risque Élevé ou Critique par défaut dans l'ÉFVP, sauf si des mesures organisationnelles (contexte Étape 3) viennent compenser.

**Les droits des personnes ne se dérivent pas de l'audit.** Aucun des 15 critères ne mesure la capacité
d'un individu à faire valoir ses droits d'accès, de rectification ou de suppression. Ce risque
s'évalue à partir du bloc C de l'étape 3 (cycle de vie organisationnel: qui a accès, comment un compte
et ses données sont supprimés) et de la documentation du fournisseur sur la suppression, pas d'un score.
Le déduire du critère 10 revient à confondre « pas de SOC2 » avec « les droits ne sont pas respectables ».
