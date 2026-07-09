# Matrice de la valeur des reviews

Instantané de la matrice de référence de l'équipe. La valeur d'un review humain dépend du
**type de projet** croisé avec la **nature du changement**. Si la matrice source évolue,
synchroniser ce fichier manuellement.

Légende : 🟢 valeur élevée · 🟡 valeur modérée · 🔴 valeur faible.

## Grille par type de projet

### Sites Umbraco
- 🔴 **Fonctionnalités de base** : contenu, formulaires simples, intégration de modules tiers
  (script analytics, bandeau de cookies, etc.).
- 🟡 **Hors de l'ordinaire** : plugins backoffice, modules de synchronisation, règles d'affaires
  complexes, ou nouveaux systèmes qu'on veut réutiliser à l'avenir (ex. neo grid).

### Projets accélérants
- 🟢 Ajouts de fonctionnalités.
- 🔴 Mises à jour.

### Micro Apps (ex. medexpress)
- 🟢 Choix technos et plan de match en début de projet.
- 🟡 Fonctionnalités au fur et à mesure (coûteux proportionnellement à la timeline accélérée de
  ce type de projet).

### Web Apps (ex. qi, clicdon)
- 🟢 Introduction de nouveaux concepts ou systèmes.
- 🟡 Nouvelles fonctionnalités basées sur des concepts existants.
- 🔴 Correctifs simples ou ajustements UX.

### Gros sites web (ex. sommets, barreau)
- 🟢 Fonctionnalités majeures : transactionnel, synchros, changements d'architecture.
- 🔴 Fonctionnalités de contenu ou d'affichage simple, sans règle d'affaires.

### Projets spéciaux (app native, nouvelle stack)
- 🟢🟢 L'analyse pour le choix de la stack (à réviser de près, idéalement présentée de vive voix).
- 🟢 Mise en place du projet, preuves de concept, etc.
- 🟡 Fonctionnalités qui s'appuient sur des concepts et systèmes déjà révisés.
- 🔴 Bugfixes et ajustements.
- 🟡 ... à moins qu'ils soient causés par une mauvaise compréhension de la stack.

## Règles opérationnelles par niveau

- **🔴 Faible** → review agentique suffisant. Merger une fois les commentaires adressés (ou
  explicitement rejetés), puis fermer la tâche / déployer.
- **🟡 Modéré** → review agentique suffisant pour merger, mais un review humain est demandé en
  différé : créer une (sous-)tâche non assignée avec un lien vers la PR. Les commentaires
  éventuels sont adressés dans un commit (petit ajustement) ou une PR 🔴.
- **🟢 Élevé** → review agentique **+** humain nécessaire pour merger.

## Points à prioriser lors d'un review humain

Quand un review humain a lieu (🟡 en différé, 🟢 avant merge), se concentrer sur :
- Architecture, définition des concepts et des systèmes.
- Respect et cohérence des règles d'affaires.
- Logique d'intégration avec les systèmes tiers.
- Performance, sécurité, conformité.

Ne pas s'attarder à la mise en forme ou au style du code (ça relève d'un `REVIEWS.md` de projet
et des reviews agentiques), sauf si ça masque un vrai problème de fond.
