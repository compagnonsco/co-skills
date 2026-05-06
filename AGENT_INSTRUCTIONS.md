# Instructions pour les agents (skills d'équipe)

Ce dépôt regroupe des **skills d'agent** partagés par l'équipe (fichiers `SKILL.md` et ressources associées). L'agent doit pouvoir **cloner ou mettre à jour ce dépôt sans demander où le placer**, puis installer les skills dans le dossier global de l'outil qui l'exécute.

## URL du dépôt git

À utiliser pour le premier `git clone` (maintenir cette ligne à jour pour toute l'équipe) :

`https://TODO`

## Emplacement canonique du clone (home de l'utilisateur)

Toujours utiliser **un seul** répertoire local, directement sous le dossier personnel :

| Plateforme | Chemin |
|------------|--------|
| Windows | `%USERPROFILE%\co-skills` |
| macOS / Linux | `$HOME/co-skills` (équivalent : `~/co-skills`) |

**Règles pour l'agent :**

1. Si ce chemin **n'existe pas** : exécuter `git clone` avec l'URL ci-dessus vers ce chemin exact (le dernier segment du chemin doit être `co-skills`).
2. Si le chemin **existe** et contient un dépôt git dont la racine comporte `AGENT_INSTRUCTIONS.md` et le dossier `skills/` : s'y placer pour les commandes `git` (`pull`, etc.).
3. Si le chemin **existe** mais n'est pas ce dépôt (pas de `.git`, autre contenu, ou structure attendue absente) : **ne pas effacer** le dossier sans accord explicite de l'utilisateur ; expliquer le problème et proposer un renommage manuel ou un autre emplacement convenu avec l'humain.

Après un clone ou un pull réussi, toute la suite se fait à partir de la **racine de ce clone**.

## Objectif

Reproduire le contenu du répertoire `skills` du clone canonique dans le **dossier global de skills** de l'outil (éditeur, CLI, plateforme d'agents, etc.).

## Où copier (skills globaux de l'outil)

L'emplacement cible dépend du **produit** :

- Consulter la documentation ou les réglages (chemins « user », « global », « skills », etc.).
- Si le chemin n'est pas déductible, **demander à l'utilisateur** une seule fois s'il faut, ou utiliser une variable d'environnement / option de configuration indiquée par l'utilisateur.

Ne pas confondre : le **clone** est toujours `~/co-skills` (ou équivalent Windows) ; la **copie des skills** va vers le dossier global défini par l'outil.

## Procédure de synchronisation des fichiers

1. S'assurer que le clone canonique est à jour (voir ci-dessus et le skill `co-agent-update` si présent).
2. Pour **chaque sous-dossier** directement dans `skills` du clone (par exemple `co-acceptance-criteria-checklist`), copier ou fusionner ce dossier **dans** le dossier global de skills identifié pour l'outil.
   - Chaque skill est un dossier contenant en général un `SKILL.md` à sa racine.
   - Si un dossier du même nom existe déjà côté global, le mettre à jour avec la version du dépôt.
3. Ne pas supprimer les autres dossiers de skills présents uniquement sur la machine de l'utilisateur : **ajouter ou mettre à jour** uniquement ce qui provient de ce dépôt.

## Vérification rapide

Le dossier global doit contenir les mêmes noms de dossiers que `skills/` dans le clone, chacun avec son `SKILL.md` (et fichiers annexes éventuels).

## Si tu ne peux pas écrire sur le disque

Indiquer les chemins source (`<clone-canonique>/skills/<nom-du-skill>`) et la destination (dossier global de l'outil) pour une copie manuelle ou un script.
