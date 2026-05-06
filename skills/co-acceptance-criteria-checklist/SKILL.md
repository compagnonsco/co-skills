---
name: acceptance-criteria-checklist
description: Génère une liste de critères d'acceptation claire et testable pour un testeur QA à partir de changements de code, centrée sur le comportement visible par l'utilisateur (sans détails d'implémentation). Use when the user asks for acceptance criteria, QA checklist, test scenarios, validation list, or tester handoff notes.
---

# Acceptance Criteria Checklist

## Objectif

Produire une liste de critères d'acceptation actionnable que le testeur peut exécuter sans contexte supplémentaire.

### Principe central : fonctionnalité visible, pas l'implémentation

- **Se concentrer sur ce que l'utilisateur voit, entend ou ressent** : écrans, messages, flux, temps de réponse perçu, données affichées, droits visibles, exports téléchargés, etc.
- **Ne pas exposer au testeur** les noms de fichiers, classes, fonctions, endpoints, schémas de base de données, algorithmes internes, choix de librairie ou refactorings purs, sauf si le testeur y a un accès direct explicite (ex. appel API documenté comme livrable produit).
- Les changements techniques peuvent servir **en interne** pour choisir les cas de test et la non-régression ; la **rédaction des critères** doit rester formulée en actions et résultats **du point de vue utilisateur** ou **du produit observable**.

## Entrées à collecter

Avant de rédiger les critères, récupérer ou demander:

- Portée des changements (features corrigées/ajoutées)
- Zone impactée (backend, frontend, api, etc.) — utile pour **raisonner** sur les risques, pas pour **remplir** les critères avec du jargon technique
- Risques connus ou régressions possibles
- Données de test nécessaires

Si une information manque, faire des hypothèses explicites.

## Règles de rédaction

1. Écrire en français simple, orientée vérification.
2. Un critère = un comportement **observable côté utilisateur ou produit** et testable sans lire le code.
3. Favoriser le format `Action -> Résultat attendu`.
4. Inclure les cas limites et cas d'erreur visibles utilisateur.
5. Ajouter une section "Non-régression ciblée" limitée aux éléments potentiellement impactés.
6. **Ne pas** mentionner les détails d'implémentation dans les critères (CA, NEG, NR) : pas de noms de composants internes, routes API brutes, tables SQL, logs techniques, etc. Si une nuance technique est indispensable, la traduire en **symptôme ou preuve observable** (message, état d'écran, fichier généré, code HTTP visible dans l'UI d'admin, etc.).

### Règle stricte pour la non-régression

- Ne jamais demander de retester une fonctionnalité complète "par défaut".
- Pour chaque cas `NR`, expliciter le lien d'impact avec le changement en langage **parcours / fonctionnalité** :
  - dépendance observable (même écran, même flux, même règle métier visible, permission utilisateur),
  - parcours utilisateur qui traverse la zone modifiée,
  - effet de bord plausible côté interface ou données affichées (navigation, calcul montré à l'écran, état incohérent visible).
- La ligne « Impact lié » peut rester courte et orientée **risque utilisateur** ; éviter d'y coller la liste des fichiers ou modules modifiés.
- Si le risque est faible et localisé, limiter la non-régression à 1-2 vérifications ciblées.
- Si aucun impact adjacent crédible n'est identifié, écrire explicitement:
  `Aucun cas de non-régression additionnel requis (impact local confirmé).`

## Format de sortie par défaut

Utiliser ce gabarit:

```markdown
## Contexte
- Changement: (résumé orienté produit / utilisateur, pas liste de fichiers)
- Zone impactée: (écrans, flux ou capacités utilisateur touchés ; éviter le jargon stack seul)
- Risque principal: (impact visible ou métier)

## Critères d'acceptation
- [ ] CA-01 - <action utilisateur> -> <résultat attendu>
- [ ] CA-02 - <action utilisateur> -> <résultat attendu>
- [ ] CA-03 - <action utilisateur> -> <résultat attendu>

## Cas négatifs / limites
- [ ] NEG-01 - <condition invalide> -> <message/comportement attendu>
- [ ] NEG-02 - <condition limite> -> <comportement attendu>

## Non-régression ciblée (uniquement zones potentiellement impactées)
- [ ] NR-01 - <parcours/élément ciblé> reste fonctionnel
  - Impact lié: <pourquoi ce test est nécessaire>
- [ ] NR-02 - <autre parcours/élément ciblé> reste fonctionnel
  - Impact lié: <pourquoi ce test est nécessaire>

## Données de test
- Compte(s):
- Prérequis:
- Jeu de données:
```

## Adaptation selon le type de changement

- **Bugfix**: prioriser reproduction avant/après + absence de régression.
- **Nouvelle fonctionnalité**: couvrir "happy path", permissions, et erreurs utilisateur.
- **Refactor technique**: décrire uniquement les **effets visibles** (aucune régression de parcours, temps perçu, absence de régression d'affichage). Ne pas lister le refactor comme critère ; le traduire en vérifications utilisateur équivalentes.
- **UI/UX**: inclure responsive, états vides, chargement, erreurs, accessibilité de base.

## Méthode rapide de sélection des cas NR (à appliquer systématiquement)

1. Lister en interne les éléments modifiés (écrans, flux, règles métier visibles, permissions) ; les détails code/API servent seulement à ne rien oublier, pas à les recopier dans la checklist.
2. Identifier seulement les parcours utilisateur qui touchent ces éléments.
3. Garder les 1-3 checks NR les plus risqués/probables, rédigés comme des vérifications **utilisateur**.
4. Exclure explicitement les zones non touchées pour éviter le sur-test.

## Checklist de qualité avant envoi au testeur

- [ ] Les critères sont numérotés et sans ambiguïté
- [ ] Chaque critère est vérifiable en 1 scénario **sans accès au code**
- [ ] Aucun critère ne repose sur des détails d'implémentation non observables par l'utilisateur cible du test
- [ ] Les cas négatifs sont présents
- [ ] Les impacts non-régression sont couverts et justifiés
- [ ] Les prérequis de test sont explicites

## Comportement attendu du skill

Quand ce skill est invoqué:

1. Résumer les changements en 2-4 puces maximum, **du point de vue produit / utilisateur** (éviter le résumé « fichier X modifié » sauf demande explicite).
2. Produire la checklist dans le format par défaut.
3. Adapter la profondeur selon le risque (faible/moyen/élevé).
4. Si nécessaire, ajouter une mini section "Questions ouvertes" (max 3).

