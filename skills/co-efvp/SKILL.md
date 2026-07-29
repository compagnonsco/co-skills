---
name: co-efvp
description: Réaliser une ÉFVP (Évaluation des facteurs relatifs à la vie privée) conforme Loi 25 art. 17 pour un outil/SaaS. Reprend une ÉFVP existante plutôt que d'en créer un doublon, vérifie qu'un audit /co-evaluate-service existe d'abord, collecte les questions contextuelles (~40%), fusionne avec les données de la grille audit (~60%), produit les 9 sections de l'ÉFVP, push dans le registre ÉFVP Notion, et propose la politique d'usage acceptable quand l'outil traite des RP. Termine en orientant vers /co-approve-service, ou en rendant la main quand il est appelé depuis lui. Utiliser quand l'utilisateur dit "/co-efvp", "fais l'ÉFVP pour X", "on a besoin d'un ÉFVP pour X", ou avant d'adopter un SaaS qui traite des données personnelles. Chaînon central entre /co-evaluate-service et /co-approve-service.
---

**LANGUE**: Toujours répondre en français, ton naturel québécois. Aucun mot anglais sauf les noms techniques (SaaS, DPA, Loi 25, ÉFVP, PII, ZDR, SSO, MFA, etc.). L'input fourni par l'utilisateur donne l'outil visé.

## Dépendances

- **Notion** (registres de gouvernance de l'équipe): le skill **lit** la BD `Audits des outils (services tiers)` (audits, data source `c88611ab-240d-413d-a45e-ae8608a437b6`) et **écrit** dans la BD `Registre ÉFVP` (data source `a1f45d7a-b325-4294-89e3-76364e2f439b`), avec optionnellement la BD `Politiques d'usage acceptable` (`11dd28ba-c387-4b0b-ba3b-84b4bbd62ddb`). Nécessite un accès Notion dans le runtime (connecteur built-in, MCP installé, ou équivalent). Sans Notion, le skill ne peut pas fonctionner.
- **Chaînage**: suppose qu'un audit existe déjà (via `/co-evaluate-service`) et redirige vers `/co-approve-service` à la fin.

## Objectif

Produire une **ÉFVP complète (9 sections)** pour un outil SaaS, conforme à l'article 17 de la Loi 25 (Québec). L'ÉFVP est obligatoire avant tout transfert de renseignements personnels hors Québec — ce qui couvre la grande majorité des SaaS hébergés aux États-Unis.

L'ÉFVP s'appuie sur deux sources:
- **~60% de la grille audit** déjà faite via `/co-evaluate-service` (dimensions 1-15, score, caveats, conditions de remédiation)
- **~40% de questions contextuelles** propres à ce déploiement précis (scope, type de données, mesures en place, etc.)

**Flow de gouvernance**: `/co-evaluate-service` → **`/co-efvp`** → `/co-approve-service`

Voir [REFERENCE.md](REFERENCE.md) pour les schemas Notion, la grille de risques, et le template 9 sections.

---

## Étape 1 — Parser l'input

- **0 nom**: interactif → "Pour quel outil tu veux faire l'ÉFVP?"
- **1 nom**: cet outil.

**Si l'appel est orchestré** (lancé depuis `/co-approve-service` plutôt que par l'utilisateur), noter ce qui a été transmis: le nom de l'outil, la réponse déjà donnée sur les données qui transitent (elle remplace le bloc B de l'étape 3, ne pas la reposer), et l'URL d'une ÉFVP existante à finir le cas échéant. Un appel orchestré change la fin du skill: voir l'étape 8.

---

## Étape 1.5 — Vérifier si une ÉFVP existe déjà (idempotence)

Avant de collecter quoi que ce soit, chercher l'outil dans la BD `Registre ÉFVP` (data source `a1f45d7a-b325-4294-89e3-76364e2f439b`), match case-insensitive sur `Outil / Système`. Sans ce contrôle, chaque relance crée une row de plus et le gate de `/co-approve-service` se retrouve devant plusieurs pages sans savoir laquelle fait foi.

- **Aucune ÉFVP** → continuer à l'étape 2.
- **ÉFVP trouvée** → présenter son `Verdict`, son `Statut` et sa `Date ÉFVP`, puis demander quoi faire:
  - **La compléter ou la corriger** (le cas normal quand son `Verdict` est `🔄 En évaluation`, ou quand des conditions ont été remplies depuis): reprendre son contenu comme point de départ et, à l'étape 6, **mettre à jour la page existante** au lieu d'en créer une.
  - **En refaire une neuve** (le contexte a changé: nouveau scope, nouvelle politique du fournisseur, réévaluation périodique): créer une nouvelle page à l'étape 6. L'ancienne reste au registre comme historique.
  - **Juste consulter**: afficher le résumé et arrêter là.
- **Plusieurs ÉFVP** → présenter la liste (date + verdict + statut) et attendre la sélection avant d'appliquer le choix ci-dessus.

---

## Étape 2 — Vérifier l'audit existant (gate obligatoire)

Chercher l'outil dans la data source `c88611ab-240d-413d-a45e-ae8608a437b6` (BD `Audits des outils (services tiers)`, URL https://www.notion.so/d18c7a098fb14b7fa01e948e14699d1d). Match case-insensitive, ignorer accents/ponctuation.

**Résultats possibles:**

- **Pas d'audit trouvé:**
  > "Pas d'audit existant pour [Outil]. L'ÉFVP se base sur les données d'audit — il faut faire `/co-evaluate-service [Outil]` d'abord. Je lance ça?"
  Si oui, enchaîner sur le skill `co-evaluate-service` **en appel orchestré**: lui indiquer qu'il est lancé depuis `/co-efvp` et qu'il doit rendre la main avec l'URL de la row d'audit et le flag `ÉFVP requise` retenu, au lieu de proposer une prochaine étape (sans ça, il redirige vers `/co-efvp` et on repart de zéro). Puis reprendre ici. Si l'audit n'aboutit pas (push refusé, abandon), arrêter: pas d'ÉFVP sans audit. Sinon, arrêter.

- **Un audit trouvé:** Le prendre. Lire: `Verdict global`, `Score total`, scores par dimension (si disponibles dans le row), `Notes / Caveats`, `Conditions remédiation`, `ÉFVP requise`, `userDefined:URL`, `Date évaluation`, URL de la page d'audit.

  Le flag `ÉFVP requise` (🔴 Oui / 🟡 Selon usage / 🟢 Non) sert à l'étape 7 (politique d'usage). S'il est **vide**, c'est un audit antérieur à l'ajout du champ: le traiter comme 🟡 Selon usage et proposer de le remplir sur la row d'audit à la fin.

- **Plusieurs audits (ré-évaluations):** Présenter la liste (date + verdict) et attendre la sélection de l'utilisateur.

Confirmer à l'utilisateur: "J'ai trouvé l'audit pour [Outil] — verdict [🟢/🟡/🟠/🔴], score [X]/75, daté du [date]. Je pars de ça pour l'ÉFVP."

---

## Étape 3 — Questions contextuelles (~40%) — INTERACTIF, un bloc à la fois

Poser les questions suivantes par blocs. **Attendre la réponse entre chaque bloc.** Pas de mur de texte.

### Bloc A — Scope et usage
> "L'outil sera utilisé comment exactement?
> - Usage **interne** (l'équipe l'utilise pour son propre travail)
> - Usage sur **projet client** (des données de client ou de ses utilisateurs pourraient transiter)
> - Les deux?
>
> Et quel département / qui l'utilise? (tous, une équipe, dev seulement, etc.)"

**Attendre.**

### Bloc B — Type de données

**Si la réponse a été transmise dans un appel orchestré** (voir étape 1), ne pas reposer la question: reprendre la réponse, la reformuler pour confirmation en une ligne, et passer au bloc C.

> "Quelles données vont transiter par cet outil? Pense aux cas réalistes, pas juste théoriques.
> (ex: prompts de travail interne, noms d'employés, emails de contacts, données de clients, données sensibles, code source, BDs de test, etc.)"

**Attendre.** Sur sa réponse, classifier mentalement chaque catégorie:
- **Publique** (aucun enjeu Loi 25)
- **Interne** (non publique mais pas de données personnelles identifiables)
- **PII pro** (nom + courriel pro — normal pour du travail, risque faible)
- **PII perso** (infos privées d'individus)
- **Sensible** (médical, financier, judiciaire, données de mineurs, ethnie/religion, etc.)

### Bloc C — Cycle de vie organisationnel
> "Côté organisation (pas le fournisseur, ça on l'a de l'audit), comment vous gérez les données dans cet outil?
> - Qui a accès? (tout le monde, admins seulement, sous-ensemble?)
> - Y a-t-il un compte org ou des comptes individuels?
> - Si quelqu'un part, le compte et les données sont supprimés comment / par qui?"

**Attendre.**

### Bloc D — Mesures organisationnelles déjà en place
> "Quelles mesures avez-vous déjà en place pour cet outil?
> - SSO / MFA activé?
> - Brèche et notification configurée (canal d'alerte admin)?
> - Politique d'usage envoyée ou prévue?
> - Formation des utilisateurs planifiée?"

**Attendre.** Prendre note de ce qui est en place vs ce qui manque.

---

## Étape 4 — Construire l'ÉFVP

Fusionner les données de l'audit (grille 15 dim.) avec les réponses contextuelles pour remplir les 9 sections. Voir [REFERENCE.md](REFERENCE.md) pour le template complet et la grille de mapping audit → risque.

### Mapping audit → sections ÉFVP clés

| Dimensions audit | Section ÉFVP |
|-----------------|-------------|
| Critères 1-2 (infrastructure, chiffrement) | § 5 Mesures techniques |
| Critère 3 (conservation) | § 5 Cycle de vie |
| Critère 4 (droit d'utilisation) | § 4 Transfert + § 7 Risques |
| Critère 5 (emplacement) | § 4 Flux et transferts |
| Critère 7 (entraînement) | § 4 + § 7 Risques IA |
| Critère 8 (partage 3rd) | § 4 Flux et transferts (sous-traitants) |
| Critère 9 (cryptage technique) | § 5 Mesures techniques |
| Critère 10 (conformité documentée: SOC2, ISO, DPA) | § 5 Mesures contractuelles |
| Conditions remédiation audit | § 8 Conditions à remplir |

Les numéros doivent correspondre à la grille réelle de `/co-evaluate-service`. Les certifications et le
DPA sont au **critère 10**, pas 8-9. Le § 6 Droits des personnes ne se dérive d'aucun critère d'audit:
il s'appuie sur le bloc C de l'étape 3 et sur la documentation de suppression du fournisseur.

### Grille de risques ÉFVP (§ 7)

Pour chaque risque identifié, évaluer: **Probabilité** (Faible/Modérée/Élevée) × **Impact** (Faible/Modéré/Élevé) → **Niveau** (Faible/Modéré/Élevé/Critique).

Risques standard à évaluer selon les données de l'audit et du contexte:

| Risque | Déclencheur |
|--------|-------------|
| Transfert hors QC sans encadrement | Critère 5 ≤ 2 |
| Usage des données au-delà de la prestation | Critère 4 ≤ 2 |
| Entraînement LLM sur les données | Critère 7 ≤ 2 |
| Rétention excessive | Critère 3 ≤ 2 |
| Communication à des tiers non maîtrisée | Critère 8 ≤ 2 |
| Absence d'encadrement contractuel (pas de DPA, pas de certification) | Critère 10 ≤ 2 |
| Fuite via prompt injection | PII/sensible dans les prompts + outil IA |
| Accès non autorisé | Pas de SSO/MFA + PII présents |
| Droits des individus non respectés | Aucun mécanisme de suppression ou d'accès documenté (bloc C + doc fournisseur), **pas un score d'audit** |
| Données client exposées | Scope "projet client" + PII présents |

### Verdict ÉFVP

Utiliser **exactement** les libellés du champ `Verdict` de la BD, sinon le push plante:

| Verdict | Condition |
|---------|-----------|
| ✅ Acceptable | Aucun risque Critique/Élevé résiduel après mesures |
| ⚠️ Conditions | Risques Modérés présents avec mesures en cours / conditions à remplir |
| 🔴 Non acceptable | Risque Critique résiduel sans mitigation viable |
| 🔄 En évaluation | Analyse commencée mais incomplète (infos manquantes du fournisseur) |

Le verdict ÉFVP est indépendant du verdict audit (🟢/🟡/🟠/🔴) — un outil peut avoir un audit 🟡 mais une ÉFVP ✅ si les mesures en place couvrent les risques résiduels.

---

## Étape 5 — Présenter le résumé de l'ÉFVP

Avant de push, présenter à l'utilisateur le récap de l'ÉFVP:

```
**ÉFVP — [Outil]** (basée sur audit du [date])

**Verdict**: [✅ Acceptable / ⚠️ Conditions / 🔴 Non acceptable]

**Fournisseur**: [entité légale + siège]
**Scope**: [Interne Compagnons / Projet client]
**Données qui transitent**: [liste classifiée]
**Transfert hors QC**: [Oui — [juridiction] / Non]
**Risques résiduels**:
- [Risque 1] — [Niveau] — Mitigation: [mesure]
- [Risque 2] — [Niveau] — Mitigation: [mesure]

**Conditions à remplir** (si ⚠️):
1. [Condition 1]
2. [Condition 2]

**RPRP**: l'utilisateur courant  
**Date ÉFVP**: [aujourd'hui]  
**Révision prévue**: [+3 mois si ⚠️, +12 mois si ✅]
```

Puis: "Je push l'ÉFVP complète (9 sections) dans le registre Notion? (oui / non / ajuster d'abord)"

---

## Étape 6 — Push Notion (avec confirmation)

**Confirmation obligatoire avant push** (demander confirmation avant toute action irréversible).

**Créer ou mettre à jour**, selon le choix fait à l'étape 1.5: s'il s'agit de compléter ou corriger une ÉFVP existante, mettre à jour cette page (mêmes champs, même body) plutôt que d'en créer une seconde. Ne créer une nouvelle page que si aucune ÉFVP n'existait ou si le choix était explicitement d'en refaire une neuve.

Si l'utilisateur refuse le push, le dire clairement: sans page au registre, l'ÉFVP n'existe pas pour `/co-approve-service` et l'approbation restera bloquée.

Si oui, créer (ou mettre à jour) la page dans la data source `a1f45d7a-b325-4294-89e3-76364e2f439b` (BD `Registre ÉFVP`, URL https://www.notion.so/c1b99a14fa1e42e895db35d08d9eb1a5):

Champs de la BD (voir [REFERENCE.md](REFERENCE.md) pour le payload complet et les types exacts):
- `Outil / Système` (title) = nom de l'outil
- `Fournisseur` (rich_text) = entité légale + siège
- `Verdict` (select) = `✅ Acceptable` / `⚠️ Conditions` / `🔴 Non acceptable` / `🔄 En évaluation`
- `Date ÉFVP` (date) = aujourd'hui
- `RPRP` (person) = l'utilisateur courant (chercher son ID via get-users, par nom ou courriel)
- `Lié à l'audit` (relation) = URL de la page d'audit dans Audits des outils
- `Scope` (select) = `Interne Compagnons` / `Projet client` (réponse du bloc A)
- `Priorité` (select) = `🔴 Haute` si PII sensible ou scope client, `🟡 Moyenne` si PII pro, `🟢 Basse` sinon
- `Statut` (**status**) = `In progress` si conditions à remplir, `Done` sinon
- `Révision prévue` (date) = +3 mois si ⚠️ Conditions, +12 mois si ✅ Acceptable
- `Notes` (rich_text) = contexte (verdict audit + score + date) puis la liste numérotée des conditions

Les noms de champs et les libellés de select doivent matcher **exactement** ceux de la BD. Un libellé
inventé fait planter le push ou crée une option parasite dans le select.

Le **contenu de la page** (body) doit contenir les 9 sections complètes de l'ÉFVP (voir template dans [REFERENCE.md](REFERENCE.md)). Utiliser des blocks Notion structurés (heading_2, paragraph, table).

Confirmer avec l'URL de la page créée.

---

## Étape 7 — Politique d'usage acceptable

D'abord vérifier si une politique existe déjà pour l'outil dans la data source `11dd28ba-c387-4b0b-ba3b-84b4bbd62ddb` (BD `Politiques d'usage acceptable`). Si oui, le mentionner et sauter l'étape.

Sinon, le comportement dépend du flag `ÉFVP requise` lu sur la row d'audit à l'étape 2:

- **Flag 🔴 Oui** — la politique est **proposée par défaut**, pas en option secondaire:
  > "L'outil traite des RP hors Québec. Je te génère la politique d'usage acceptable pour aller avec l'ÉFVP? (oui / non)"
- **Flag 🟡 ou 🟢** — proposition simple:
  > "Veux-tu qu'on crée aussi la politique d'usage acceptable pour [Outil]?"

Si oui, générer la politique (qui peut l'utiliser, quoi éviter, données interdites, responsabilité) et la push dans la BD politiques. Champs (voir [REFERENCE.md](REFERENCE.md) pour le schema complet):
- `Outil / Système` (title), `Version` = "1.0", `Statut` (**status**) = `Done`
- `Responsable` (person) = même personne que le RPRP de l'ÉFVP
- `Date de publication` = aujourd'hui, `Révision prévue` = même date que celle de l'ÉFVP
- `ÉFVP associée` = **url** de la page ÉFVP créée à l'étape 6 (c'est une url, pas une relation)

Après le push, rappeler le partage (le skill ne poste rien lui-même):
> "Politique créée: [URL]. Pense à la partager à l'équipe (Slack, ou en pièce jointe au message d'annonce de l'outil)."

---

## Étape 8 — Sortie

Deux cas, dans cet ordre de priorité.

**1. Appel orchestré** (le skill a été lancé depuis `/co-approve-service`, voir étape 1). Ne jamais rediriger, quel que soit le verdict: rendre la main avec l'URL de la page ÉFVP, son `Verdict` et ses conditions. C'est l'orchestrateur qui décide de la suite, y compris l'arrêt sur un verdict `🔴 Non acceptable`. Rediriger ici renverrait vers le skill qui vient d'appeler celui-ci.

**2. Appel direct** (l'utilisateur a tapé `/co-efvp`):

- Verdict `✅ Acceptable` ou `⚠️ Conditions`:
  > "L'ÉFVP est complétée et enregistrée. Pour officialiser l'adoption, lance maintenant: `/co-approve-service [Outil]`"
- Verdict `🔴 Non acceptable`:
  > "L'ÉFVP est 🔴 Non acceptable: l'outil ne peut pas être adopté tant que les risques critiques ne sont pas résolus. Il n'y a pas lieu de faire `/co-approve-service` pour l'instant."
- Verdict `🔄 En évaluation` (analyse incomplète, infos manquantes du fournisseur): dire ce qui manque et que l'approbation restera bloquée tant que l'ÉFVP n'est pas conclue.

---

## Règles

- **Toujours en français**, ton naturel québécois.
- **Interactif, un bloc à la fois** — pas de mur de texte, pas de tout envoyer d'un coup.
- **Gate obligatoire**: pas d'ÉFVP sans audit existant.
- **Pas de doublon**: toujours vérifier le registre ÉFVP avant de collecter (étape 1.5). Une ÉFVP existante se complète ou se corrige; on n'en crée une seconde que si le contexte a réellement changé.
- **Appel orchestré = rendre la main**, jamais rediriger. Priorité sur toute autre règle de sortie.
- **Confirmation avant push Notion** — demander confirmation avant toute action irréversible.
- **Noms de champs exacts** — les libellés de propriétés et d'options select doivent matcher la BD au caractère près (voir REFERENCE.md). Ne jamais inventer un nom "logique".
- **Verdict ÉFVP ≠ verdict audit** — ils sont complémentaires, pas redondants.
- **🔴 Non acceptable = pas de /co-approve-service** — pas de contournement.
- **Loi 25 art. 17**: toujours rappeler la base légale dans la section transfert de l'ÉFVP.
