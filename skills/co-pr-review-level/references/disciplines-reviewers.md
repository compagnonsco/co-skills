# Disciplines & reviewers

Instantané de qui couvre quelle discipline dans l'équipe. Sert à deux choses dans
co-pr-review-level : déduire la discipline de l'auteur d'une PR, et savoir qui impliquer quand
une PR déborde. Synchroniser manuellement quand l'équipe change.

## Roster

- **FE (frontend)** : Anne. Review FE nécessaire → demander Anne.
- **BE (backend)** : tout le monde sauf Anne.

Un dev absent de cette liste = discipline inconnue : le skill demande à l'exécution plutôt que
de deviner.

## Ce qui compte comme FE vs BE (pour classer les fichiers « À LIRE » du digest)

- **FE** : `.vue`, `.svelte`, composants `.jsx` / `.tsx`, `stores/`, `composables/`,
  markup/styles (`.cshtml`, `.html`, `.css`, `.scss`). Le markup pur ne compte PAS comme
  débordement : c'est de l'affichage, pas de la logique.
- **BE** : `.cs`, `.prisma`, `.sql`, `server/api`, `server/routes`, `server/middleware`,
  `*Handler.cs` / `*Service.cs` / `*Repository.cs` / `*Controller.cs`, migrations éditées à la
  main.
- **Ambigu** (`.ts` / `.js` hors dossier clair) : trancher en ouvrant le fichier, comme pour
  les monofichiers `.vue` / `.razor`.
