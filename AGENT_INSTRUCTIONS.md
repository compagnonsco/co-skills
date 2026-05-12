# Instructions pour les agents (skills d'équipe)

Ce dépôt regroupe des **skills d'agent** partagés par l'équipe (fichiers `SKILL.md` et ressources associées). L'agent doit pouvoir **cloner ou mettre à jour ce dépôt sans demander où le placer**, puis installer les skills dans le **dossier global de skills** de chaque outil concerné.

## URL du dépôt git

À utiliser pour le premier `git clone` (maintenir cette ligne à jour pour toute l'équipe) :

`https://github.com/compagnonsco/co-skills`

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

## Organisation des dossiers de skills dans le dépôt

| Dossier dans le clone | Rôle |
|----------------------|------|
| **`skills/`** | Skills **génériques** : utilisables quel que soit l'outil (conventions agnostiques, pas de dépendance à une API ou un chemin propre à un éditeur). |
| **`cursor/skills/`** | Réservé à **Cursor** : skills qui s'appuient sur des capacités ou chemins spécifiques à Cursor (ex. Canvas, `~/.cursor/skills-cursor/`, règles ou hooks propres à l'IDE). Ne pas les déployer vers le dossier global d'un autre produit. |
| **`claude/skills/`** *(éventuel, même principe)* | Pourra accueillir plus tard des skills **spécifiques à Claude** (Code, Console, etc.), avec une cible de déploiement documentée quand l'équipe l'adoptera. Tant que ce dossier n'existe pas, l'ignorer. |

Les chemins `cursor/` et `claude/` ne remplacent pas `skills/` : ils **complètent** la bibliothèque commune avec des variantes ou des workflows liés à un outil.

## Objectif

Reproduire le contenu des répertoires de skills du clone canonique dans les **dossiers globaux de skills** appropriés :

- tout sous-dossier de **`skills/`** → dossier global de l'outil pour lequel la synchro est effectuée (voir ci-dessous) ;
- tout sous-dossier de **`cursor/skills/`** → dossier global **Cursor** uniquement ;
- à terme, tout sous-dossier de **`claude/skills/`** → dossier global **Claude** (chemin à préciser dans ce fichier lorsque l'équipe le définira).

## Où copier (skills globaux de l'outil)

L'emplacement cible dépend du **produit** :

- **Cursor (skills sous `cursor/skills/`)** : copier vers le dossier personnel des skills Cursor, en général `~/.cursor/skills` (Windows : `%USERPROFILE%\.cursor\skills`).
- **Skills génériques (`skills/`)** : consulter la documentation ou les réglages de l'outil qui exécute l'agent (chemins « user », « global », « skills », etc.).
- Si le chemin n'est pas déductible pour un outil donné, **demander à l'utilisateur** une seule fois s'il faut, ou utiliser une variable d'environnement / option de configuration indiquée par l'utilisateur.

Ne pas confondre : le **clone** est toujours `~/co-skills` (ou équivalent Windows) ; la **copie des skills** va vers le ou les dossiers globaux définis ci-dessus selon la source (`skills/` vs `cursor/skills/`).

## Procédure de synchronisation des fichiers

1. S'assurer que le clone canonique est à jour (voir ci-dessus et le skill `co-agent-update` si présent).
2. **Arbre `skills/` (générique)** : pour **chaque sous-dossier** directement dans `skills/` du clone (par exemple `co-acceptance-criteria-checklist`), copier ou fusionner ce dossier **dans** le dossier global de skills identifié pour l'outil qui reçoit la synchro générique.
   - Chaque skill est un dossier contenant en général un `SKILL.md` à sa racine.
   - Si un dossier du même nom existe déjà côté global, le mettre à jour avec la version du dépôt.
3. **Arbre `cursor/skills/` (Cursor uniquement)** : si ce dossier existe, pour **chaque sous-dossier** directement sous `cursor/skills/`, copier ou fusionner vers **`~/.cursor/skills`** (même nom de dossier). Ne pas utiliser ce flux pour installer ces skills dans le répertoire global d'un autre IDE ou agent.
4. **Arbre `claude/skills/`** : lorsqu'il existera et qu'une cible aura été documentée ici, appliquer la même logique (copier chaque sous-dossier vers le dossier global Claude convenu).
5. Ne pas supprimer les autres dossiers de skills présents uniquement sur la machine de l'utilisateur : **ajouter ou mettre à jour** uniquement ce qui provient de ce dépôt.

## Vérification rapide

- Chaque `skills/<nom>/` synchronisé vers l'outil générique doit avoir son `SKILL.md` (et annexes éventuelles) côté destination.
- Chaque `cursor/skills/<nom>/` copié vers Cursor doit avoir son équivalent sous `~/.cursor/skills/<nom>/` avec `SKILL.md`.

## Si tu ne peux pas écrire sur le disque

Indiquer les chemins sources et la destination pour une copie manuelle ou un script :

- générique : `<clone-canonique>/skills/<nom-du-skill>` → dossier global de l'outil ;
- Cursor : `<clone-canonique>/cursor/skills/<nom-du-skill>` → `~/.cursor/skills/<nom-du-skill>`.
