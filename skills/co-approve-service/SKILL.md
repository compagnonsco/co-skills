---
name: co-approve-service
description: Porte d'entrée du flow de gouvernance des services tiers. Vérifie et orchestre les étapes préalables avant d'inscrire un outil/SaaS dans la liste pérenne des outils approuvés: audit manquant, il lance /co-evaluate-service; ÉFVP requise et manquante, il lance /co-efvp et bloque tant qu'elle n'est pas au registre. Puis gère l'approbation selon le verdict d'audit (vert = direct, jaune/orange = caveats + confirmation, rouge = réévaluer), capture interactivement les infos licence/frais/compte, et push dans la BD Notion "Régistre des outils approuvés" avec les relations Audit et ÉFVP. Utiliser quand l'utilisateur dit "/co-approve-service", "approuve cet outil", "on adopte X", "on signe avec X", ou veut officialiser l'adoption d'un SaaS, que l'audit soit déjà fait ou non.
---

**LANGUE**: Toujours répondre en français, ton naturel québécois. Aucun mot anglais sauf les noms techniques (SaaS, DPA, Loi 25, etc.). L'input fourni par l'utilisateur donne l'outil à approuver.

## Dépendances

- **Notion** (registres de gouvernance de l'équipe): le skill **lit** la BD `Régistre des outils (services tiers)` (audits, data source `c88611ab-240d-413d-a45e-ae8608a437b6`) et la BD `Registre ÉFVP` (data source `a1f45d7a-b325-4294-89e3-76364e2f439b`), et **écrit** dans la BD `Régistre des outils approuvés` (data source `b131ae79-0ef0-407e-b83d-1d5022f854d2`). Nécessite un accès Notion dans le runtime (connecteur built-in, MCP installé, ou équivalent). Sans Notion, le skill ne peut pas fonctionner: il dépend de ces registres.
- **Chaînage**: ce skill est la **porte d'entrée** du flow. Il ne suppose rien: il vérifie l'état de chaque étape préalable et lance `/co-evaluate-service` ou `/co-efvp` au besoin, puis reprend la main.

## Objectif

Officialiser l'adoption d'un outil, en garantissant que les étapes de gouvernance préalables sont faites. Le skill vérifie l'audit (le lance s'il manque), vérifie l'ÉFVP quand elle est requise (la lance et bloque tant qu'elle manque), applique la règle d'approbation selon le verdict d'audit, capture interactivement le volet commercial/licence, et inscrit l'outil dans la **liste pérenne** `Régistre des outils approuvés` (source de vérité des adoptions).

**Flow de gouvernance**: `/co-evaluate-service` → `/co-efvp` (si requise) → **`/co-approve-service`**

Le skill est **ré-entrant**: le relancer sur un outil déjà entamé reprend à la première étape manquante, sans refaire ce qui est déjà au registre. Voir [REFERENCE.md](REFERENCE.md) pour les schemas des BD + le payload de push.

---

## Étape 1 — Parser l'input

- **0 nom**: interactif → "Quel outil tu veux approuver?"
- **1 nom**: cet outil.

## Étape 2 — Retrouver l'audit (BD Régistre des outils)

Chercher l'outil dans la data source `c88611ab-240d-413d-a45e-ae8608a437b6` (BD `Régistre des outils (services tiers)`). Match case-insensitive, ignorer accents/ponctuation.

- **Pas trouvé** → "Pas d'audit pour [Outil]. L'audit est obligatoire avant l'approbation, je le lance? (oui / non)" Si oui, enchaîner sur le skill `co-evaluate-service` en appel orchestré (voir Handoff ci-dessous). Si non, arrêter.
- **Un seul audit** → le prendre.
- **Plusieurs audits** (ré-évaluations) → présenter la liste avec **date d'évaluation + verdict global + `ÉFVP requise`** pour aider l'utilisateur à choisir le bon, attendre sa sélection. Afficher le flag est obligatoire: c'est lui qui décide du gate de l'étape 3.5, et choisir un vieil audit flaggé 🟢 contournerait le gate sans que personne le voie. Si les audits **divergent sur le flag**, le dire explicitement et recommander le plus récent.

Lire du row d'audit: `Verdict global`, `Score total`, `Notes / Caveats`, `Conditions remédiation`, `ÉFVP requise`, `userDefined:URL`, `Date évaluation`, l'URL de la page d'audit (pour la relation).

## Étape 3 — Trancher sur le verdict d'audit

Cette étape **décide si le verdict d'audit bloque**, et met de côté les caveats à présenter. Elle ne demande aucune confirmation: la seule confirmation du flow est à l'étape 3.5, une fois l'ÉFVP connue, pour que l'utilisateur confirme les deux d'un coup.

| Verdict | Action |
|---------|--------|
| 🟢 **Vert** | Ne bloque pas. Aucun caveat à retenir. Passer à l'étape 3.5. |
| 🟡 **Jaune** / 🟠 **Orange** | Ne bloque pas, mais **retenir les caveats** pour l'étape 3.5: les `Conditions remédiation` + `Notes / Caveats` de l'audit, plus le **niveau d'abonnement requis** et/ou le **cas d'usage approprié** pour que ce soit ok. Passer à l'étape 3.5. |
| 🔴 **Rouge** | **Pas d'approbation, pas d'override.** Expliquer pourquoi (no-go ou score trop bas). Proposer de **réévaluer avec d'autres critères / un contexte plus précis** (re-lancer `/co-evaluate-service` avec un scope affiné) pour tenter de passer au 🟡. Si ça reste rouge, ça passe pas. Arrêter ici. |
| ⚪ **À évaluer** | L'audit existe mais n'est pas conclu: il n'y a pas de verdict à approuver. Arrêter, et proposer de finir l'audit (`/co-evaluate-service [Outil]`) avant de reprendre l'approbation. Ne jamais reporter `⚪` dans le champ `Verdict` du registre des services approuvés: cette option n'y existe pas. |

## Étape 3.5 — Gate ÉFVP (Loi 25) et confirmation

À faire **avant** la capture du volet commercial: inutile de collecter licence et frais si l'adoption est bloquée.

### 3.5a — Chercher l'ÉFVP (toujours, quel que soit le flag)

Chercher l'outil dans la BD `Registre ÉFVP` (data source `a1f45d7a-b325-4294-89e3-76364e2f439b`), match case-insensitive sur `Outil / Système`. Ce lookup est **inconditionnel**: une ÉFVP défavorable doit bloquer même quand l'audit ne l'exigeait pas, et la relation `ÉFVP` doit être remplie au push dès qu'une page existe.

- **Plusieurs ÉFVP** pour le même outil → présenter la liste (`Date ÉFVP` + `Verdict` + `Statut`) et attendre la sélection. Signaler si les verdicts divergent.
- Noter le `Verdict`, le `Statut`, les conditions (`Notes`) et l'URL de la page.

Deux verdicts tranchent immédiatement, **peu importe le verdict d'audit et le flag**:

- **`🔴 Non acceptable`** → arrêter. Pas d'approbation, pas d'override. Expliquer quel risque critique reste sans mitigation et proposer de refaire l'ÉFVP une fois le risque traité.
- **`🔄 En évaluation`** → l'ÉFVP est commencée mais pas conclue. La traiter comme absente dans la suite de l'étape, en proposant de la **finir** plutôt que d'en créer une nouvelle (voir 3.5b: l'appel à `/co-efvp` doit mentionner la page existante).

Un verdict `⚠️ Conditions` ne bloque pas, mais ses conditions vont dans la confirmation de 3.5c. Une ÉFVP `✅ Acceptable` dont le `Statut` est encore `In progress` a des conditions non remplies: traiter ses `Notes` comme des conditions à afficher, elle aussi.

### 3.5b — Décider si l'absence d'ÉFVP bloque

Partir du champ `ÉFVP requise` lu sur la row d'audit à l'étape 2. **Si le champ est vide** (audit antérieur à l'ajout du champ): le traiter comme 🟡 Selon usage. Ne jamais l'interpréter comme 🟢 Non. Proposer au passage de le remplir sur la row d'audit.

Cette sous-étape ne s'applique que si aucune ÉFVP exploitable n'a été trouvée en 3.5a.

| Flag | Action |
|------|--------|
| 🔴 **Oui** | ÉFVP **obligatoire**. "Cet outil traite des RP hors Québec, l'ÉFVP est obligatoire avant l'approbation (Loi 25 art. 17). Je la fais maintenant? (oui / non)". Si oui, enchaîner sur `/co-efvp` en appel orchestré (voir Handoff ci-dessous). Si non, **arrêter**: pas d'approbation. |
| 🟡 **Selon usage** | Demander d'abord: "Quelles données vont réellement transiter par cet outil? Pense aux cas réalistes, pas juste théoriques." Sur la réponse: des renseignements personnels (noms, courriels, données de clients ou de leurs usagers, contenu qui identifie des individus) → traiter comme 🔴 Oui ci-dessus. Aucun RP → continuer, et **exiger une justification écrite** qui ira dans `Données transmises (Loi 25)` (ex: "Usage dev interne uniquement, code source et diagnostics, aucun RP par définition du cas d'usage"). Réutiliser cette réponse à l'étape 5, ne pas reposer la question. |
| 🟢 **Non** | Non bloquant, continuer. Si l'utilisateur veut quand même une ÉFVP, `/co-efvp` reste disponible. |

### 3.5c — Confirmation unique

C'est le seul point de confirmation du flow avant le push. Présenter d'un coup ce qui a été retenu:

- les **caveats d'audit** mis de côté à l'étape 3 (si verdict 🟡/🟠);
- les **conditions de l'ÉFVP** (si verdict `⚠️ Conditions`, ou `✅` avec `Statut` = `In progress`).

Puis demander une confirmation explicite: "Tu es sûr.e de vouloir l'approuver malgré ça?" Attendre le oui avant l'étape 4.

S'il n'y a **ni caveat ni condition** (audit 🟢 et ÉFVP `✅` sans condition, ou pas d'ÉFVP requise), sauter la confirmation et passer à l'étape 4: il n'y a rien à confirmer.

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
- **Comptes (courriels)** (courriel du ou des comptes)
- **Responsable interne** (qui gère le compte/renouvellement)
- **Raison d'utilisation** (texte court)
- **Données transmises (Loi 25)** (texte): si la question a déjà été posée à l'étape 3.5 (flag 🟡), **réutiliser cette réponse** au lieu de la reposer. Sinon, demander explicitement *quelles données vont transiter par l'outil* et les noter (documente le flux pour la conformité)
- **Statut** (défaut: `Actif`, ou `En essai` si période d'essai)

Le `Coût annualisé` est calculé automatiquement par la formule Notion, ne pas le remplir.

## Étape 6 — Confirmation + push Notion

**Confirmation obligatoire avant push** (demander confirmation avant toute action irréversible): présenter le récap (tool + verdict d'audit + verdict ÉFVP s'il y en a une + tous les champs saisis) et demander "Je pousse dans le Régistre des outils approuvés? (oui / non / ajuster)".

Si oui, créer la page dans la data source `b131ae79-0ef0-407e-b83d-1d5022f854d2`:
- Reporter `Tool`, `Verdict`, `URL` (= `userDefined:URL` de l'audit), tous les champs saisis.
- **Relation `Audit`**: lier vers la page d'audit (passer son URL dans un array JSON).
- **Relation `ÉFVP`**: lier vers la page ÉFVP trouvée ou créée à l'étape 3.5 (array JSON d'URLs). Laisser vide seulement si le flag était 🟢 Non, ou 🟡 avec justification "aucun RP".
- `Approuvé par` = l'utilisateur courant, `Date d'approbation` = date du jour.

**Champs Personne** (`Approuvé par`, `Responsable interne`): type `person` Notion. Faut l'**ID utilisateur** d'abord (chercher la personne via l'outil get-users, par son nom ou son courriel; demander à l'utilisateur courant qui il est si ce n'est pas déterminable par le runtime), puis passer un array JSON d'IDs. Sinon le push plante.

Voir [REFERENCE.md](REFERENCE.md) pour le mapping complet + payload. Confirmer avec l'URL de la page créée.

---

## Handoff — appels orchestrés

Les étapes 2 et 3.5b peuvent lancer `/co-evaluate-service` ou `/co-efvp`. Ces deux skills se terminent normalement en redirigeant vers `/co-approve-service`: sans convention, on repart en boucle. Un **appel orchestré** est un appel où on demande au skill de rendre la main au lieu de rediriger.

**À transmettre à l'aller**, en une phrase au début de l'appel:
- que c'est un appel orchestré depuis `/co-approve-service`, donc qu'il doit rendre la main à la fin plutôt que proposer une prochaine étape;
- le nom de l'outil;
- pour `/co-efvp`: la réponse déjà donnée sur les données qui transitent (elle correspond au bloc B du questionnaire, inutile de la reposer), et l'URL de l'ÉFVP existante s'il s'agit de finir une ÉFVP `🔄 En évaluation` plutôt que d'en créer une.

**À récupérer au retour**:
- de `/co-evaluate-service`: l'URL de la row d'audit et le flag `ÉFVP requise` retenu;
- de `/co-efvp`: l'URL de la page ÉFVP, son `Verdict` et ses conditions.

**Si le skill appelé n'aboutit pas** — l'utilisateur refuse le push Notion, abandonne en cours, ou le push échoue: il n'y a ni row d'audit ni page ÉFVP à lier. Le gate reste **fermé**. Le dire explicitement ("sans la page au registre je ne peux pas approuver") et arrêter, plutôt que de continuer vers l'étape 4 avec une relation qui pointerait dans le vide.

**Si le contexte ne peut pas transiter** (le skill s'exécute dans un contexte isolé qui ne reçoit pas ces informations): ne pas enchaîner. Dire à l'utilisateur de lancer le skill manquant lui-même, puis de relancer `/co-approve-service [Outil]`. Le skill étant ré-entrant, la relance reprend à l'étape manquante sans rien refaire.

---

## Règles

- **Toujours en français**, ton naturel québécois.
- **Vérifier avant de supposer** — l'audit et l'ÉFVP se vérifient dans les registres, jamais sur parole. Étape manquante = on la lance ou on arrête.
- **Le registre ÉFVP se consulte toujours** — même quand le flag dit 🟢 Non. Le flag décide si l'**absence** bloque; il ne dispense pas de regarder ce qui existe.
- **Jamais approuver un 🔴 Rouge ni un ⚪ À évaluer** — réévaluer ou finir l'audit, pas contourner.
- **Jamais approuver sans l'ÉFVP quand elle est requise** — et jamais avec une ÉFVP `🔴 Non acceptable`. Pas d'override sur ces deux-là.
- **Flag `ÉFVP requise` vide = 🟡 Selon usage**, jamais 🟢 Non. Un audit ancien n'est pas une dispense.
- **Une seule confirmation, à l'étape 3.5c** — elle agrège caveats d'audit et conditions d'ÉFVP. Ne pas confirmer à l'étape 3.
- **Confirmation avant push Notion** — demander confirmation avant toute action irréversible.
- **Pas de doublon** — détecter une approbation existante et proposer un update.
- **Loi 25** — toujours capturer les données qui transitent par l'outil, et ne poser la question qu'une fois.
