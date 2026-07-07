# Reference — /co-evaluate-service

Détails techniques pour le skill `/co-evaluate-service`. Le SKILL.md pointe ici quand nécessaire.

---

## 📊 Comment lire les scores

**Échelle 1-5**: **plus c'est élevé, mieux c'est.**

- **5/5 = IDÉAL** — position parfaite documentée par contrat
- **4/5 = TRÈS BIEN** — idéal partiellement documenté
- **3/5 = ACCEPTABLE** — position OK mais pas d'engagement clair
- **2/5 = À RISQUE** — position préoccupante
- **1/5 = SIGNAL D'ARRÊT** — position à éviter

**Le pictogramme ⚠️** = dimension critique avec no-go automatique si score = 1/5. Ça marque juste l'importance, pas un problème. Une dimension critique ⚠️ scorée 5/5 reste excellente.

---

## 🎯 Les 5 dimensions critiques — en vrai ça veut dire quoi

### Critère 4 ⚠️ — Le fournisseur peut-il utiliser tes données pour autre chose que te livrer le service?

| Score | En vrai |
|-------|---------|
| 5/5 | "Tes données restent **à toi**, point. Engagement écrit dans le contrat par défaut." |
| 4/5 | Même engagement, mais faut signer un papier séparé (DPA) |
| 3/5 | "On dit qu'on respecte ça mais c'est flou" |
| 2/5 | Il se réserve le droit d'utiliser tes données "pour améliorer son produit" sans option claire |
| 1/5 | Il partage tes données avec partenaires/marketing sans ton contrôle — **NO-GO** |

### Critère 5 ⚠️ — Sur quel sol physique sont tes données?

| Score | En vrai |
|-------|---------|
| 5/5 | **Canada**, et tu peux choisir la région |
| 4/5 | Europe ou Canada (conforme Loi 25 par défaut) |
| 3/5 | USA mais avec contrat (DPA, SCC) qui encadre les transferts |
| 2/5 | USA sans rien d'encadré clairement |
| 1/5 | Pays inconnu ou sans cadre légal protecteur — **NO-GO** |

### Critère 7 ⚠️ — Tes données peuvent-elles servir à entraîner l'IA du fournisseur (ou des tiers)?

| Score | En vrai |
|-------|---------|
| 5/5 | **PAS entraîné par défaut**, garanti par contrat. Tu n'as rien à faire. |
| 4/5 | **PAS entraîné par défaut**, opt-out documenté en plus si besoin |
| 3/5 | Entraîné par défaut, **MAIS opt-out faisable** (Dashboard, config claire). Action proactive requise mais possible. |
| 2/5 | Par défaut entraîné, **opt-out flou, caché, ou non disponible sur certains plans** |
| 1/5 | **Aucune option opt-out possible**, tes données nourrissent l'IA — **NO-GO** |

**Principe**: 3/5 reconnaît qu'un opt-out faisable est une vraie protection. 2/5 punit l'absence de mécanisme clair. 1/5 NO-GO seulement quand vraiment aucune option n'existe.

### Critère 10 ⚠️ — Le fournisseur a-t-il des certifications de sécurité vérifiables par des tiers?

| Score | En vrai |
|-------|---------|
| 5/5 | Combo complet (SOC2 Type II + ISO27001 + GDPR + spécifiques industries) |
| 4/5 | Les 3 majeures (SOC2 + ISO + GDPR) |
| 3/5 | Au moins une majeure (SOC2 OU ISO27001) |
| 2/5 | "En cours", partielles, ou seulement SOC2 Type I (pas Type II) |
| 1/5 | Aucune certification documentée — **NO-GO** |

### Critère 14 ⚠️ — Le fournisseur prend-il au sérieux les nouveaux risques propres à l'IA?

⚠️ **Critère 14 et 15 sont N/A si l'outil n'a aucune feature IA** (ex: pure infra, CRM simple).

| Score | En vrai |
|-------|---------|
| 5/5 | Équipe red team IA, publie ses tests prompt injection / vol de modèle / empoisonnement |
| 4/5 | Documente ses tests sur 2-3 vecteurs d'attaque IA |
| 3/5 | Mentionne génériquement "on fait de la sécu IA" sans détails |
| 2/5 | Programme bug bounty généraliste mais rien d'IA-spécifique |
| 1/5 | Aucune trace de réflexion sur ces risques — **NO-GO** (si outil AI core) |
| N/A | L'outil n'a aucune fonctionnalité IA — dimension non applicable |

---

## Les 15 dimensions — grille détaillée

### Grille de base — 11 dimensions

#### Critère 1 — Infrastructure du fournisseur
- **5**: Infrastructure privée dédiée documentée (single-tenant, isolation totale)
- **4**: Privée partielle (tenant logique, isolation app-level)
- **3**: Cloud public reconnu (Azure/AWS/GCP) sans détails d'isolation
- **2**: Cloud sans détails ou architecture floue
- **1**: Infrastructure non documentée

#### Critère 2 — Chiffrement des données
- **5**: CMK (Customer-Managed Keys) supporté, doc complète
- **4**: Chiffrement at-rest + in-transit avec rotation documentée
- **3**: Chiffrement at-rest + in-transit mentionné sans détails
- **2**: Chiffrement partiel ou ancien (TLS 1.1)
- **1**: Aucune mention de chiffrement

#### Critère 3 — Conservation des données
- **5**: Politique claire avec rétention max + suppression à la demande + délai documenté
- **4**: Politique claire avec rétention max
- **3**: Mention de rétention sans engagement précis
- **2**: Rétention indéfinie ou floue
- **1**: Aucune politique de rétention

#### Critère 4 ⚠️ — Droit d'utilisation des données (**NO-GO si 1**)
- **5**: Service-only explicite + clause contractuelle DPA
- **4**: Service-only mentionné ToS
- **3**: Usage limité au service mais clauses ambigües
- **2**: Usage étendu (amélioration produit) sans opt-out clair
- **1**: Usage partagé avec partenaires ou marketing sans contrôle = NO-GO

#### Critère 5 ⚠️ — Emplacement des données (**NO-GO si 1**)
- **5**: Canada + choix de région documenté
- **4**: Europe ou Canada (Loi 25 compatible) avec choix de région
- **3**: USA avec engagement DPA, transferts encadrés (SCC/EU-US DPF)
- **2**: USA sans engagement clair de transfert
- **1**: Régions inconnues ou pays sans cadre légal = NO-GO

#### Critère 6 — Propriété des données
- **5**: Ma propriété explicite ToS + export complet sur demande
- **4**: Ma propriété + export disponible
- **3**: Ma propriété mentionnée
- **2**: Propriété partagée ou ambigüe
- **1**: Cession de propriété au fournisseur

#### Critère 7 ⚠️ — Entraînement avec mes données (**NO-GO si 1**)
- **5**: Opt-out par défaut + engagement contractuel
- **4**: Opt-out activable facilement, doc claire
- **3**: Opt-out possible mais demande config
- **2**: Opt-in par défaut ou floue
- **1**: Entraînement activé sans option de retrait = NO-GO

#### Critère 8 — Partage avec tierces parties
- **5**: Liste publique de sous-processeurs + notification de changement + droit d'objection
- **4**: Liste publique + notification
- **3**: Liste publique
- **2**: Mention de tiers sans détails
- **1**: Partage non documenté

#### Critère 9 — Cryptage technique
- **5**: AES-256 at-rest + TLS 1.3 + détails certification
- **4**: AES-256 + TLS 1.3
- **3**: AES-256 + TLS 1.2+
- **2**: Cryptage mentionné, normes anciennes
- **1**: Aucun standard documenté

#### Critère 10 ⚠️ — Conformité documentée (**NO-GO si 1**)
- **5**: SOC2 Type II + ISO27001 + GDPR + autres pertinents (HIPAA, PCI-DSS)
- **4**: SOC2 Type II + ISO27001 + GDPR
- **3**: SOC2 Type II OU ISO27001
- **2**: Engagements en cours, certifications partielles
- **1**: Aucune certification = NO-GO

#### Critère 11 — Disponibilité du service
- **5**: > 99.99% SLA contractuel + status page historique
- **4**: > 99.9% SLA contractuel
- **3**: SLA mentionné sans contrat clair
- **2**: Status page sans SLA
- **1**: Aucun engagement uptime

### Extension cyber — 4 dimensions additionnelles

#### Critère 12 — Authentification et IAM
- **5**: MFA obligatoire + SSO entreprise + IAM granulaire + moindre privilège
- **4**: MFA obligatoire + SSO + rôles
- **3**: MFA optionnelle + rôles basiques
- **2**: MFA optionnelle, pas de SSO
- **1**: Authentification simple sans MFA

#### Critère 13 — Sécurité des connecteurs et API
- **5**: OAuth 2.1 (si MCP) + authentification obligatoire + journalisation complète
- **4**: OAuth 2.0 + auth obligatoire + logs
- **3**: Auth API + logs basiques
- **2**: Auth partielle ou logs absents
- **1**: Connecteurs non authentifiés (1 800+ serveurs MCP exposés en 2025)

#### Critère 14 ⚠️ — Posture menaces IA-spécifiques (**NO-GO si 1**, CRITIQUE)
- **5**: Tests prompt injection + empoisonnement + vol modèle documentés + rapports d'audit
- **4**: Tests documentés sur 2-3 vecteurs
- **3**: Mention générique de tests sécu IA
- **2**: Référence vague sans détails
- **1**: Aucune posture documentée = NO-GO

#### Critère 15 — Procédure d'incident IA et notification
- **5**: Procédure dédiée IA + notification <72h + RACI + communication client
- **4**: Procédure + notification <72h
- **3**: Procédure générique adaptée
- **2**: Procédure générique sans IA
- **1**: Aucune procédure dédiée

---

## Sources typiques par fournisseur

### Pages standardisées à chercher

| Type | Patterns d'URL fréquents |
|------|--------------------------|
| Trust Center | `trust.<vendor>.com`, `<vendor>.com/trust`, `<vendor>.com/security` |
| DPA | `<vendor>.com/legal/dpa`, `<vendor>.com/dpa`, `<vendor>.com/data-processing-agreement` |
| Privacy Policy | `<vendor>.com/privacy`, `<vendor>.com/legal/privacy` |
| Terms of Service | `<vendor>.com/terms`, `<vendor>.com/legal/terms`, `<vendor>.com/tos` |
| Status Page | `status.<vendor>.com`, `<vendor>.statuspage.io` |
| Subprocessors | `<vendor>.com/subprocessors`, `<vendor>.com/legal/subprocessors` |
| Security | `<vendor>.com/security`, `security.<vendor>.com` |
| Compliance | `<vendor>.com/compliance`, `<vendor>.com/certifications` |

### WebSearch queries efficaces

- `"<tool>" SOC2 type II`
- `"<tool>" ISO27001 certification`
- `"<tool>" data residency Canada`
- `"<tool>" data processing agreement`
- `"<tool>" security incident 2024 2025 2026`
- `"<tool>" privacy policy training data`
- `"<tool>" subprocessors list`

---

## Schema BD Notion `Régistre des outils (services tiers)`

**URL**: https://www.notion.so/d18c7a098fb14b7fa01e948e14699d1d  
**Data source ID**: `c88611ab-240d-413d-a45e-ae8608a437b6`

### Mapping des champs

| Champ Notion | Type | Valeurs | Source |
|--------------|------|---------|--------|
| `Name` | title | nom de l'outil | input |
| `userDefined:URL` | url | URL officielle | détecté ou demandé |
| `Catégorie` | select | `AI/LLM`, `Comm`, `Dev tools`, `Design`, `Productivité`, `Infra/Hosting`, `Analytics`, `CRM/Marketing`, `Storage`, `Other` | inféré |
| `Verdict global` | select | `🟢 Vert (>60)`, `🟡 Jaune (45-60)`, `🟠 Orange (30-45)`, `🔴 Rouge (<30 ou no-go)`, `⚪ À évaluer` | calculé |
| `Score total` | number | 0-75 | calculé |
| `Nb no-go auto` | number | 0-5 | calculé |
| `Critère 1 — Infrastructure` | number | 1-5 | scoring |
| `Critère 2 — Chiffrement` | number | 1-5 | scoring |
| `Critère 3 — Conservation` | number | 1-5 | scoring |
| `Critère 4 ⚠️ Droit utilisation` | number | 1-5 | scoring (no-go si 1) |
| `Critère 5 ⚠️ Emplacement` | number | 1-5 | scoring (no-go si 1) |
| `Critère 6 — Propriété` | number | 1-5 | scoring |
| `Critère 7 ⚠️ Entraînement` | number | 1-5 | scoring (no-go si 1) |
| `Critère 8 — Partage 3rd` | number | 1-5 | scoring |
| `Critère 9 — Cryptage technique` | number | 1-5 | scoring |
| `Critère 10 ⚠️ Conformité documentée` | number | 1-5 | scoring (no-go si 1) |
| `Critère 11 — SLA disponibilité` | number | 1-5 | scoring |
| `Critère 12 — Authentification & IAM` | number | 1-5 | scoring |
| `Critère 13 — Sécurité connecteurs/API` | number | 1-5 | scoring |
| `Critère 14 ⚠️ Posture menaces IA` | number | 1-5 | scoring (no-go si 1) |
| `Critère 15 — Procédure incident IA` | number | 1-5 | scoring |
| `Notes / Caveats` | rich text | résumé textuel libre | synthèse |
| `Sources consultées` | rich text | liste URLs investiguées | citations |
| `Conditions remédiation` | rich text | conditions si Jaune/Orange | reco |
| `Date évaluation` | date | date du jour | auto |
| `Projet` | relation | vers `Liste des projets` | optionnel |

### Exemple de payload pour créer la page Notion

Format générique, transposable selon l'outil de création de page disponible (connecteur Notion built-in, MCP Notion, etc.). La convention `parent.type: "data_source_id"` + `pages: [{ properties: {...} }]` suit l'API officielle Notion.

```json
{
  "parent": {
    "type": "data_source_id",
    "data_source_id": "c88611ab-240d-413d-a45e-ae8608a437b6"
  },
  "pages": [{
    "properties": {
      "Name": "Granola",
      "userDefined:URL": "https://granola.ai",
      "Catégorie": "AI/LLM",
      "Verdict global": "🟠 Orange (30-45)",
      "Score total": 38,
      "Nb no-go auto": 0,
      "Critère 1 — Infrastructure": 3,
      "Critère 2 — Chiffrement": 4,
      "Critère 3 — Conservation": 3,
      "Critère 4 ⚠️ Droit utilisation": 2,
      "Critère 5 ⚠️ Emplacement": 2,
      "Critère 6 — Propriété": 3,
      "Critère 7 ⚠️ Entraînement": 2,
      "Critère 8 — Partage 3rd": 3,
      "Critère 9 — Cryptage technique": 4,
      "Critère 10 ⚠️ Conformité documentée": 2,
      "Critère 11 — SLA disponibilité": 2,
      "Critère 12 — Authentification & IAM": 3,
      "Critère 13 — Sécurité connecteurs/API": 2,
      "Critère 14 ⚠️ Posture menaces IA": 1,
      "Critère 15 — Procédure incident IA": 2,
      "Notes / Caveats": "Posture menaces IA non documentée. SOC2 en cours. Hébergement USA sans option Canada.",
      "Sources consultées": "https://granola.ai/security, https://granola.ai/privacy, https://granola.ai/terms",
      "Conditions remédiation": "1. Obtenir confirmation SOC2 Type II finalisée\n2. Activer opt-out training\n3. Documenter posture menaces IA",
      "date:Date évaluation:start": "2026-05-20"
    }
  }]
}
```

### Relation Projet

BD `Liste des projets`: `294964e9-7e73-4fe2-b222-8cd02cab5ed3`

Pour brancher: passer une valeur `"Projet"` avec une JSON array d'URLs de pages projets. Demander à l'utilisateur quel projet, ou laisser vide.

---

## Notes opérationnelles

- En mode comparaison, créer N rows séparées (pas une row avec arrays).
- Si l'utilisateur dit "skip le push Notion", afficher quand même le tableau en chat.
- Pour les outils où l'info est introuvable malgré recherche approfondie, **noter score 1 ou 2** (pas 3 par défaut) — l'absence d'info = risque documentaire.
- Si le total est < 45 ou ≥ 1 no-go: rappeler à l'utilisateur que c'est une **conversation contractuelle** à avoir avec le fournisseur, pas une élimination automatique. La grille structure la négociation.
