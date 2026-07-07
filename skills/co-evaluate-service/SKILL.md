---
name: co-evaluate-service
description: Évaluer un outil/service SaaS avant adoption selon la grille de gouvernance IA (15 dimensions). Score 1-5 par dimension, total /75, no-go automatique sur 5 dimensions critiques (4, 5, 7, 10, 14). Utiliser quand l'utilisateur dit "/co-evaluate-service", "évalue cet outil/service", "est-ce qu'on devrait signer avec X", "compare X et Y comme outils SaaS", ou veut un verdict structuré avant de signer un fournisseur SaaS (Granola, Otter, Notion AI, ChatGPT, etc.). Cousin de /co-evaluate-library mais pour les services SaaS (vs dépendances code).
---

**LANGUE**: Toujours répondre en français, ton naturel québécois. Aucun mot anglais sauf les noms techniques (SOC2, ISO27001, DPA, MCP, etc.). L'input fourni par l'utilisateur donne l'outil (ou les outils) à évaluer.

## Dépendances

- **Notion** (registres de gouvernance de l'équipe): le skill lit et écrit dans la BD `Régistre des outils (services tiers)` (data source `c88611ab-240d-413d-a45e-ae8608a437b6`). Nécessite un accès Notion dans le runtime (connecteur built-in, MCP installé, ou équivalent). Si Notion est absent, le skill peut quand même produire l'évaluation en chat, mais sans la vérification d'antériorité ni le push final.
- **Recherche web**: pour investiguer les sources publiques (Trust Center, DPA, Privacy, etc.). Si absente, l'évaluation se base sur les infos fournies par l'utilisateur, avec une fiabilité réduite.
- **Agents secondaires** (optionnel): accélèrent les investigations en les menant en parallèle si le runtime les supporte; sinon le skill investigue séquentiellement.

## Objectif

Évaluer un SaaS via la **grille 15 dimensions** de gouvernance IA. Score numérique 1-5 par dimension, total /75, verdict 🟢🟡🟠🔴. **No-go automatique** sur 5 dimensions critiques (4, 5, 7, 10, 14) si score = 1. Output: tableau récap en chat + push BD Notion `Régistre des outils (services tiers)`.

Trois modes:
- **Deep dive** sur 1 outil (`/co-evaluate-service Granola`)
- **Comparaison** 2-3 outils (`/co-evaluate-service Granola Otter Fireflies`)
- **Interactif** si pas d'arg

Voir [REFERENCE.md](REFERENCE.md) pour la grille détaillée + sources + schema Notion. Voir [EXAMPLES.md](EXAMPLES.md) pour exemples concrets.

---

## Étape 1 — Parser l'input

- **0 nom**: interactif → "Quel outil tu veux évaluer? Ou comparer 2-3 outils?"
- **1 nom**: deep dive
- **2-3 noms**: comparaison
- **4+ noms**: "trop pour une comparaison utile, on garde combien?"

Pour chaque outil, identifier:
- Nom officiel + URL du site officiel (chercher si pas évident)
- Catégorie (AI/LLM, Comm, Dev tools, Design, Productivité, Infra, Analytics, CRM, Storage, Other)

---

## Étape 1.5 — Vérifier si déjà évalué dans Notion (PRIORITAIRE)

**Avant de lancer les agents secondaires** (qui coûtent du temps et des tokens), vérifier dans la BD `Régistre des outils (services tiers)` si l'outil a déjà été évalué. Évite de refaire le travail et donne à l'utilisateur le contexte historique.

Pour chaque outil parsé:

1. **Chercher dans la data source Notion** `c88611ab-240d-413d-a45e-ae8608a437b6` (BD `Régistre des outils (services tiers)`, URL https://www.notion.so/d18c7a098fb14b7fa01e948e14699d1d). Utiliser l'outil de recherche Notion disponible dans ton runtime (selon le client: outil `notion-search`/`search` du connecteur Notion built-in, du MCP Notion installé, ou équivalent), filtré sur cette data source, avec query = nom de l'outil. Fallback si rien de probant: fetcher la data source au complet et parcourir les rows. Match: case-insensitive, ignorer accents et ponctuation mineure (ex: "ChatGPT" = "chatgpt" = "Chat GPT").

2. **Si match trouvé**, présenter à l'utilisateur:

   > **On a déjà évalué [Outil] le [Date évaluation]. Verdict: [Verdict global] (score [Score total]/75, [Nb no-go auto] no-go auto).**
   >
   > Notes/caveats: [résumé 1-2 lignes si présent]
   >
   > 📄 Page Notion: [URL de la page Notion existante]
   > 🔗 Site officiel: [userDefined:URL si présent]
   >
   > Tu veux:
   > - **(a)** Juste consulter — on s'arrête ici
   > - **(b)** Refaire l'évaluation dans un contexte plus précis (préciser lequel)
   > - **(c)** Refaire parce qu'une nouvelle version / changement de politique est sortie (préciser quoi)
   >
   > Si (b) ou (c), je relance l'éval complète et on crée une nouvelle row (l'historique est conservé).

   **Attendre la réponse de l'utilisateur avant de continuer.** Si (a) → terminer le skill. Si (b) ou (c) → passer à Étape 2 en gardant en tête le contexte précis fourni (à intégrer dans les prompts des agents secondaires).

3. **Si aucun match**, mentionner brièvement (« Pas d'éval existante pour [Outil], on part de zéro ») et enchaîner sur Étape 2.

4. **Mode comparaison (2-3 outils)**: faire la recherche pour chaque outil. Possible que certains soient déjà évalués et d'autres pas — présenter le portrait clair (qui est dans la BD, qui ne l'est pas) et demander à l'utilisateur quoi faire (réutiliser les anciens scores pour ceux déjà en BD, ou tout refaire à neuf pour homogénéité).

---

## Étape 2 — Investiguer les sources en parallèle

Investiguer 5-7 sources distinctes. **Si ton runtime supporte des agents secondaires parallèles** (ex: Claude Code `Agent`/Task, Cursor Background Agents, etc.): déléguer une source par agent secondaire en parallèle. **Sinon**: faire les investigations séquentiellement avec une output compacte par source (5-10 lignes max chacune) pour ne pas saturer le contexte.

Voir [REFERENCE.md](REFERENCE.md) pour les pages typiques à chercher par fournisseur.

Sources à investiguer (1 investigation par source):
1. **Trust Center / Security page** — `trust.<vendor>.com` ou `<vendor>.com/security`
2. **DPA (Data Processing Agreement)** — clauses contractuelles, sous-processeurs, hébergement
3. **Privacy Policy** — collecte, conservation, opt-out training
4. **Terms of Service** — propriété données, suspension, juridiction
5. **Status page / SLA** — uptime historique, engagement contractuel
6. **Subprocessors list** — pages dédiées (souvent depuis Trust Center)
7. **Recherche web reviews** — "<tool> SOC2", "<tool> security audit", incidents passés

Format de prompt pour chaque investigation (agent secondaire ou recherche directe):
> "Trouve la [Trust Center / DPA / etc.] pour le SaaS <nom>. Ramène les URLs sources + faits citables pour les dimensions [liste des dim qu'il couvre]. Format: 5-10 lignes max avec citations URLs."

Agréger les retours en notes structurées.

---

## Étape 3 — Scorer les 15 dimensions

Pour chaque dimension, attribuer un score 1-5 selon la grille (voir [REFERENCE.md](REFERENCE.md) pour le détail + traductions "en vrai ça veut dire"). **Citation URL obligatoire** pour les scores ≥ 3.

**⚠️ IMPORTANT — Échelle de scoring** (un humain qui lit doit comprendre tout de suite):

```
5/5 = IDÉAL          — position parfaite documentée
4/5 = TRÈS BIEN      — idéal partiellement documenté
3/5 = ACCEPTABLE     — position OK mais pas d'engagement clair
2/5 = À RISQUE       — position préoccupante
1/5 = SIGNAL D'ARRÊT — position à éviter

Plus le score est élevé, mieux c'est. 5 = bon, 1 = mauvais.
```

**Le pictogramme ⚠️ devant une dimension** = "dimension critique avec no-go automatique si score = 1". Ça ne veut PAS dire "il y a un problème ici" — c'est juste un marqueur pour les 5 dimensions où un score 1 force un verdict rouge peu importe le total. Une dim ⚠️ scorée 5/5 reste excellente.

**Critère 14 et 15 — applicabilité IA** (logique N/A élargie):

Le Critère 14 (Posture menaces IA) et 15 (Procédure incident IA) ne s'appliquent **que si l'outil expose une surface IA** au sens de la gouvernance (prompt injection, empoisonnement, vol de modèle). Pour décider:

| Type d'outil | Critère 14 | Critère 15 | Exemple |
|--------------|------------|------------|---------|
| **IA générative exposée** (LLM API, ChatGPT-style, transcription IA, génération de contenu) | Scorer 1-5 | Scorer 1-5 | Claude API, ChatGPT, Granola, Otter |
| **Features IA en feature secondaire** (IA optionnelle, addon AI) | Scorer 1-5 (noter portion AI dans justification) | Scorer 1-5 | Jotform (Jotform AI), Notion (Notion AI) |
| **ML interne non exposé** (ranking, classification, semantic search sans prompt user) | **N/A** | **N/A** | SiteSearch360 (vector search), Algolia search |
| **Aucune feature IA** (pure infra, CRM simple, paiement) | **N/A** | **N/A** | Stripe, Mailchimp basique |

**Pourquoi**: Si l'outil n'expose pas de prompt LLM ou n'utilise pas de modèle génératif, les menaces "prompt injection" et "vol de modèle" ne s'appliquent pas. Pas la peine de pénaliser un outil qui n'a juste pas de surface IA.

Quand N/A: le total est calculé sur les dimensions applicables. Ex: si Critère 14 et 15 = N/A, total max = 13 × 5 = 65 (au lieu de 75).

**Pièges à éviter** (rappels de la grille):
- **Notation indulgente par défaut** = mauvais signal. Si l'info n'existe pas, c'est un risque, pas un confort. Note 1 ou 2.
- **Indulgence pour les gros fournisseurs** — la taille n'absout pas l'absence d'engagement spécifique.
- **Évitement du no-go automatique** — sur dim critique, c'est binaire. Score 1 = no-go.
- **Score ≠ opinion** — le score est documentaire (URL/citation requise), pas personnel.

---

## Étape 3.5 — Contre-vérification des no-go potentiels (OBLIGATOIRE)

**Si un score critique (Critère 4, 5, 7, 10, 14) tombe à 1/5 dans le scoring initial, NE PAS conclure tout de suite.** Un score 1 force un verdict 🔴 Rouge, donc l'enjeu est élevé. Faut creuser avant de le confirmer.

### Pourquoi contre-vérifier?

Un no-go basé sur une lecture rapide peut être injuste:
- Le fournisseur peut avoir l'info ailleurs (Trust Center vs AI Policy vs DPA — chacun peut contredire l'autre)
- "Absence d'info publique" ≠ "interdit explicitement"
- Distinguer **OpenAI API** (no-training par défaut depuis 2023) vs **ChatGPT consumer** (training par défaut) — Jotform en est un cas typique
- Plans Enterprise/HIPAA peuvent offrir des protections invisibles sur la version gratuite/publique
- Une clause contractuelle dans un DPA à signer peut combler ce qui manque dans la doc publique

### Comment contre-vérifier

Lancer **2-3 investigations supplémentaires** sur le no-go suspect (en parallèle si agents secondaires supportés, sinon séquentiellement):

1. **Deep dive doc** — Relire EN PROFONDEUR la doc concernée (AI Policy + DPA + Privacy + Subprocessors), chercher contradictions internes, citer les phrases exactes
2. **Industry standard** — Vérifier la politique standard de l'industrie pour ce type de risque (ex: OpenAI API no-training depuis mars 2023, AWS subprocessor obligations, etc.)
3. **Plan tiers** — Vérifier si plans Enterprise/HIPAA/BAA offrent des protections supplémentaires non visibles sur les plans publics

### Distinguer 3 catégories de no-go

| Catégorie | Action |
|-----------|--------|
| **No-go définitif** | Clauses explicites qui interdisent ce qu'on veut (ex: "we share data with marketing partners"). Score 1 confirmé. Pas de signature. |
| **No-go contractuel** | Doc publique défavorable, MAIS possible remédiation via DPA signé ou plan upgrade. Score 1 maintenu, mais flagger "à clarifier contractuellement". Conditions de remédiation concrètes à négocier. |
| **No-go d'apparence** | Lecture initiale superficielle. La contre-vérification révèle des protections (ex: OpenAI API B2B vs consumer). Score remonté à 2-3 selon ce qui est trouvé. |

### Format de présentation à l'utilisateur

Après contre-vérification, présenter:

> **Critère X = 1/5 (suspect no-go)** — Contre-vérifié:
> - Source initiale: [URL + phrase exacte]
> - Contre-source 1: [URL + phrase]
> - Contre-source 2: [URL + phrase]
> - **Catégorie**: [no-go définitif / no-go contractuel / no-go d'apparence]
> - **Verdict révisé**: [score final + justification]
> - **Conditions de remédiation** (si no-go contractuel): [actions précises]

---

## Étape 4 — Check-ins humains sur les dimensions critiques

**Pour les 5 dimensions no-go (4, 5, 7, 10, 14)**, présenter ton score proposé + justification + URL source, et demander confirmation:

> "**Critère 4 — Droit d'utilisation**: Je propose **score X**. Justification: [...]. Source: [URL]. Tu confirmes ou tu ajustes?"

Pour les dimensions à zone d'ambiguïté (score 3 ou 4 incertain), même chose — demander validation.

---

## Étape 5 — Calculer le verdict global

1. **Score total** = somme des dimensions **applicables** (pas les N/A)
2. **Score max** = nb dimensions applicables × 5 (normalement 75, ou 65 si Critère 14 et 15 sont N/A)
3. **Pourcentage** = score total / score max × 100 (utilisé pour comparer les outils entre eux)
4. **Nb no-go auto** = compter les dim 4, 5, 7, 10, 14 où score = 1 (Critère 14 ignorée si N/A)
5. **Verdict** (basé sur le pourcentage):
   - Nb no-go ≥ 1 → **🔴 Rouge (no-go automatique)**, peu importe le total
   - Sinon: 
     - > 80% → **🟢 Vert** (signature avec confiance)
     - 60-80% → **🟡 Jaune** (conditions, renégocier dimensions faibles)
     - 40-60% → **🟠 Orange** (plan correctif obligatoire, revue 90 jours)
     - < 40% → **🔴 Rouge** (ne pas signer)

**Référence grille** (échelle sur /75 fixe): >60/75 = Vert, 45-60 = Jaune, 30-45 = Orange, <30 = Rouge. Les seuils en % préservent cette logique tout en gérant le cas N/A.

Si **Jaune** ou **Orange**, identifier 2-3 **conditions de remédiation** concrètes (dimensions faibles à renégocier avec le fournisseur).

---

## Étape 6 — Sortie chat

**Format avec légende explicite** (un humain qui lit doit comprendre tout de suite):

```
**[outil]** — [catégorie] — [URL]

📊 Échelle: 5/5 = idéal, 1/5 = signal d'arrêt. Plus c'est élevé, mieux c'est.
⚠️ = dimension critique (no-go automatique si score = 1/5).

| # | Dimension | Score | Ce que ça veut dire en vrai |
|---|-----------|-------|----------------------------|
| 1 | Infrastructure | 4/5 | Azure dédié documenté ([URL]) |
| 2 | Chiffrement | 5/5 | AES-256 + CMK ([URL]) |
| ... | ... | ... | ... |
| 14 ⚠️ | Posture menaces IA | 1/5 | Aucune doc anti-prompt-injection — NO-GO |
| 15 | Procédure incident IA | 3/5 | Procédure générique, pas spécifique IA |

**Score total**: __/__ ( __% )  |  **No-go automatiques**: __

→ **Verdict: 🔴 Rouge (no-go automatique sur Critère 14)**

**Pourquoi 🔴**: [explication en 1 phrase humaine, ex: "Le fournisseur n'a aucune protection documentée contre les attaques propres à l'IA, alors qu'il utilise activement l'IA."]

**Conditions de remédiation** (si Jaune/Orange):
1. **[Critère X]** — [Action concrète à demander au fournisseur. Ex: "Obtenir une clause contractuelle no-training dans le DPA"]
2. ...
3. ...
```

**Mode comparaison**: tableau side-by-side avec colonnes Critère / outil1 / outil2 / outil3 + ligne verdict final. Garder la légende en haut.

---

## Étape 7 — Push Notion (avec confirmation)

**Confirmation obligatoire avant push** (demander confirmation avant toute action irréversible):

> "Je pousse l'évaluation dans la BD `Régistre des outils (services tiers)`? (oui / non / ajuster d'abord)"

Si oui:
- Utiliser l'outil de création de page Notion disponible dans ton runtime (selon le client: `notion-create-pages`/`create-pages` du connecteur Notion built-in, du MCP Notion installé, ou équivalent)
- Cible: data source `c88611ab-240d-413d-a45e-ae8608a437b6` (BD `Régistre des outils (services tiers)`, https://www.notion.so/d18c7a098fb14b7fa01e948e14699d1d)
- Mapper tous les champs (voir [REFERENCE.md](REFERENCE.md) pour le schema complet et le payload exemple)
- **Important**: champ URL = `userDefined:URL` dans le payload (convention Notion API)

**Mode comparaison**: pousser N rows séparées (1 par outil, pas une row avec arrays).

Confirmer le push avec l'URL de chaque page créée.

---

## Règles

- **Toujours en français**, ton naturel québécois
- **Citations URLs obligatoires** pour chaque score ≥ 3 (le score est documentaire)
- **Investigations en parallèle si possible** — agents secondaires si le runtime les supporte, sinon séquentiel avec output compact
- **Check-ins humains obligatoires** sur les 5 dim no-go (4, 5, 7, 10, 14)
- **Confirmation avant push Notion** — demander confirmation avant toute action irréversible
- **Posture critique** — marketing claim ≠ engagement contractuel
- **Pas d'indulgence par défaut** — l'absence d'info = risque, pas confort
