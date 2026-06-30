---
name: co-approve-service
description: Approuver un outil/SaaS déjà audité et l'inscrire dans la liste pérenne des outils approuvés (registre d'adoption de l'équipe). Lit le verdict d'audit dans le Régistre des outils, gère l'approbation selon le verdict (vert = direct, jaune/orange = caveats + confirmation, rouge = réévaluer), capture interactivement les infos licence/frais/compte, puis push dans la BD Notion "Régistre des outils approuvés". Utiliser quand l'utilisateur dit "/co-approve-service", "approuve cet outil", "on adopte X", "on signe avec X", ou veut officialiser l'adoption d'un SaaS après son éval. Chaînon après /co-evaluate-service.
---

**LANGUE**: Toujours répondre en français, ton naturel québécois. Aucun mot anglais sauf les noms techniques (SaaS, DPA, Loi 25, etc.). L'input fourni par l'utilisateur donne l'outil à approuver.

## Dépendances

- **Notion** (registres de gouvernance de l'équipe): le skill **lit** la BD `Régistre des outils (services tiers)` (audits, data source `c88611ab-240d-413d-a45e-ae8608a437b6`) et **écrit** dans la BD `Régistre des outils approuvés` (data source `b131ae79-0ef0-407e-b83d-1d5022f854d2`). Nécessite un accès Notion dans le runtime (connecteur built-in, MCP installé, ou équivalent). Sans Notion, le skill ne peut pas fonctionner: il dépend de ces deux registres.
- **Chaînage**: ce skill suppose qu'un audit existe déjà (via `/co-evaluate-service`). S'il n'en trouve pas, il propose de lancer l'audit d'abord.

## Objectif

Officialiser l'adoption d'un outil **déjà audité** via `/co-evaluate-service`. Le skill lit le verdict d'audit, applique la règle d'approbation selon la couleur, capture interactivement le volet commercial/licence, et inscrit l'outil dans la **liste pérenne** `Régistre des outils approuvés` (source de vérité des adoptions). Voir [REFERENCE.md](REFERENCE.md) pour les schemas des deux BD + le payload de push.

---

## Étape 1 — Parser l'input

- **0 nom**: interactif → "Quel outil tu veux approuver?"
- **1 nom**: cet outil.

## Étape 2 — Retrouver l'audit (BD Régistre des outils)

Chercher l'outil dans la data source `c88611ab-240d-413d-a45e-ae8608a437b6` (BD `Régistre des outils (services tiers)`). Match case-insensitive, ignorer accents/ponctuation.

- **Pas trouvé** → "Pas d'audit pour [Outil]. Tu veux que je lance `/co-evaluate-service [Outil]` d'abord?" Si oui, enchaîner sur le skill `co-evaluate-service`, sinon arrêter.
- **Un seul audit** → le prendre.
- **Plusieurs audits** (ré-évaluations) → présenter la liste avec **date d'évaluation + verdict** pour aider l'utilisateur à choisir le bon, attendre sa sélection.

Lire du row d'audit: `Verdict global`, `Score total`, `Notes / Caveats`, `Conditions remédiation`, `userDefined:URL`, `Date évaluation`, l'URL de la page d'audit (pour la relation).

## Étape 3 — Appliquer la règle d'approbation selon le verdict

| Verdict | Action |
|---------|--------|
| 🟢 **Vert** | Approbation directe. Enchaîner à l'étape 4. |
| 🟡 **Jaune** / 🟠 **Orange** | Avant d'accepter: afficher les **caveats** (les `Conditions remédiation` + `Notes / Caveats` de l'audit), rappeler le **niveau d'abonnement requis** et/ou le **cas d'usage approprié** pour que ce soit ok. Puis demander confirmation explicite: "Tu es sûr.e de vouloir l'approuver malgré ça?" Attendre le oui avant l'étape 4. |
| 🔴 **Rouge** | **Pas d'approbation, pas d'override.** Expliquer pourquoi (no-go ou score trop bas). Proposer de **réévaluer avec d'autres critères / un contexte plus précis** (re-lancer `/co-evaluate-service` avec un scope affiné) pour tenter de passer au 🟡. Si ça reste rouge, ça passe pas. Arrêter ici. |

## Étape 4 — Vérifier les doublons (idempotence)

Chercher l'outil dans la BD `Régistre des outils approuvés` (data source `b131ae79-0ef0-407e-b83d-1d5022f854d2`).
- **Déjà présent** → "Déjà approuvé le [Date d'approbation] (licence [X], statut [Y]). Tu veux mettre à jour cette entrée au lieu d'en créer une nouvelle?" Si update → modifier la row existante. Sinon, arrêter.
- **Absent** → continuer.

## Étape 5 — Capture interactive du volet commercial/licence

**D'abord, brancher**: demander "C'est un **essai gratuit**, ou c'est **déjà payé / on signe**?"
- **Essai gratuit** → sauter Frais / Devise / Récurrence / Nb de sièges (les laisser vides), mettre `Statut` = `En essai`, `Licence choisie` = "Essai gratuit". Demander seulement: raison d'utilisation, données Loi 25, et (optionnel) date de fin d'essai → `Date de renouvellement`, compte courriel.
- **Payé / signature** → demander tous les champs ci-dessous.

Demander un champ à la fois (ou en petit groupe), ton conversationnel. Champs:

- **Licence choisie** (texte, ex: "Team", "Pro annuel")
- **Frais** (nombre) + **Devise** (CAD / USD) + **Récurrence** (mensuel / annuel / usage-based / one-time / gratuit)
- **Nb de sièges** (nombre, si applicable)
- **Date d'abonnement** (date)
- **Date de renouvellement** (date, si applicable)
- **Compte (courriel)** (email du compte)
- **Responsable interne** (qui gère le compte/renouvellement)
- **Raison d'utilisation** (texte court)
- **Données transmises (Loi 25)** (texte): demander explicitement *quelles données vont transiter par l'outil* et les noter (documente le flux pour la conformité)
- **Statut** (défaut: `Actif`, ou `En essai` si période d'essai)

Le `Coût annualisé` est calculé automatiquement par la formule Notion, ne pas le remplir.

## Étape 6 — Confirmation + push Notion

**Confirmation obligatoire avant push** (demander confirmation avant toute action irréversible): présenter le récap (tool + verdict + tous les champs saisis) et demander "Je pousse dans le Régistre des outils approuvés? (oui / non / ajuster)".

Si oui, créer la page dans la data source `b131ae79-0ef0-407e-b83d-1d5022f854d2`:
- Reporter `Tool`, `Verdict`, `URL` (= `userDefined:URL` de l'audit), tous les champs saisis.
- **Relation `Audit`**: lier vers la page d'audit (passer son URL dans un array JSON).
- `Approuvé par` = l'utilisateur courant, `Date d'approbation` = date du jour.

**Champs Personne** (`Approuvé par`, `Responsable interne`): type `person` Notion. Faut l'**ID utilisateur** d'abord (chercher la personne via l'outil get-users, par son nom ou son courriel; demander à l'utilisateur courant qui il est si ce n'est pas déterminable par le runtime), puis passer un array JSON d'IDs. Sinon le push plante.

Voir [REFERENCE.md](REFERENCE.md) pour le mapping complet + payload. Confirmer avec l'URL de la page créée.

---

## Règles

- **Toujours en français**, ton naturel québécois.
- **Jamais approuver un 🔴 Rouge** — réévaluer, pas contourner.
- **Caveats obligatoires + confirmation** sur 🟡/🟠.
- **Confirmation avant push Notion** — demander confirmation avant toute action irréversible.
- **Pas de doublon** — détecter une approbation existante et proposer un update.
- **Loi 25** — toujours capturer les données qui transitent par l'outil.
