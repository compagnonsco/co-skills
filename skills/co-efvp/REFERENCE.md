# REFERENCE — /co-efvp

## IDs Notion

| BD | Data source ID | URL page |
|----|---------------|----------|
| Régistre des outils (audits) | `c88611ab-240d-413d-a45e-ae8608a437b6` | https://www.notion.so/d18c7a098fb14b7fa01e948e14699d1d |
| Registre ÉFVP | `a1f45d7a-b325-4294-89e3-76364e2f439b` | https://www.notion.so/c1b99a14fa1e42e895db35d08d9eb1a5 |
| Politiques d'usage acceptable | `11dd28ba-c387-4b0b-ba3b-84b4bbd62ddb` | (page parente ÉFVP) |
| Régistre des outils approuvés | `b131ae79-0ef0-407e-b83d-1d5022f854d2` | https://www.notion.so/8357446469cb4285a170664cfb5f943c |

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

**Payload exemple** (notion-create-pages):
```json
{
  "dataSourceId": "a1f45d7a-b325-4294-89e3-76364e2f439b",
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
}
```

---

## Schema BD — Politiques d'usage acceptable

| Champ | Type Notion | Valeurs / Notes |
|-------|-------------|-----------------|
| `Outil / Système` | title | Même libellé que dans le Registre ÉFVP |
| `Version` | rich_text | ex: "1.0" |
| `Statut` | **status** | `Not started`, `In progress`, `Done` |
| `Responsable` | person | Array d'IDs utilisateur Notion |
| `Date de publication` | date | Date ISO |
| `Révision prévue` | date | Date ISO. Aligner sur la `Révision prévue` de l'ÉFVP |
| `ÉFVP associée` | **url** | URL de la page ÉFVP. C'est une url, pas une relation |
| `Notes` | rich_text | Contexte court |

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
| Basée sur l'audit | [lien vers la page d'audit dans Régistre des outils] |
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

- **Hébergement**: [Région(s) selon audit dim. 1+5]
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
- [ ] Certification: [SOC 2, ISO 27001, etc. — selon audit dim. 8]

#### Techniques (selon audit dim. 1-2-3)
- Chiffrement en transit: [TLS 1.2+]
- Chiffrement au repos: [AES-256 ou équivalent]
- ZDR (Zero Data Retention): [Disponible / Non disponible / Disponible sur plan X]
- Conservation côté fournisseur: [Durée selon audit dim. 3]

#### Organisationnelles (selon réponses contexte)
- [ ] SSO/MFA activé (compte org)
- [ ] Canal de notification brèche configuré
- [ ] Politique d'usage acceptable diffusée
- [ ] Formation des utilisateurs
- [ ] Procédure suppression compte lors d'un départ

---

### § 6 — Droits des personnes concernées

- **Droit d'accès / rectification / suppression**: [Comment c'est adressé selon audit dim. 10]
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

**Prochaine révision**: [Date + 2 ans ou au prochain changement majeur]

---

## Grille de mapping audit → risque ÉFVP

| Dimension audit | Score | Risque ÉFVP associé | Impact si ≤ 2 |
|----------------|-------|---------------------|---------------|
| 3 — Conservation | ≤ 2 | Rétention excessive | Élevé |
| 4 — Utilisation données | ≤ 2 | Transfert sans encadrement | Critique |
| 5 — Hébergement/Juridiction | ≤ 2 | Transfert hors QC non couvert | Critique |
| 7 — No-training | ≤ 2 | Entraînement LLM sur données | Élevé |
| 8 — Certifications | ≤ 2 | Absence encadrement contractuel | Modéré |
| 10 — Droits accès/suppression | ≤ 2 | Droits individus non respectables | Élevé |
| 2 — Chiffrement | ≤ 2 | Fuite en transit/repos | Élevé |

**Logique**: Score ≤ 2 sur une dimension critique = risque Élevé ou Critique par défaut dans l'ÉFVP, sauf si des mesures organisationnelles (contexte Étape 3) viennent compenser.
