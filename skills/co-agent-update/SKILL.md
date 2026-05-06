---
name: co-agent-update
description: Assure un clone git du dépôt des skills d'équipe sous le répertoire canonique du home utilisateur (co-skills), exécute pull si le clone existe déjà, puis resynchronise chaque dossier sous skills/ vers le dossier global de skills sans supprimer les autres skills locaux. Use when the user asks to update team skills, sync the skills repo, install or clone co-skills, pull co-skills, refresh shared agent skills, or run a skills repository update.
disable-model-invocation: true
---

# Mise à jour du dépôt skills d'équipe

## Objectif

Maintenir le dépôt des skills partagés **au chemin canonique défini dans `AGENT_INSTRUCTIONS.md`** (racine utilisateur : `co-skills`), puis **réappliquer la synchronisation des fichiers** : copier ou fusionner chaque sous-dossier de `skills/` vers le dossier global de skills (mêmes règles et garde-fous que dans `AGENT_INSTRUCTIONS.md`).

L'agent doit **privilégier ce flux autonome** et ne pas demander « où cloner » si les prérequis sont réunis.

## Chemin canonique du dépôt

Déterminer le répertoire personnel (`HOME` / `%USERPROFILE%`), puis utiliser :

- **Windows** : `%USERPROFILE%\co-skills`
- **macOS / Linux** : `$HOME/co-skills`

Ne pas inventer un autre emplacement pour le clone sans raison documentée (conflit sur le chemin, refus d'écrasement, etc.).

## URL du dépôt

Lire l'URL de `git clone` dans **`AGENT_INSTRUCTIONS.md`** à la racine du dépôt **si le fichier est déjà disponible** (par ex. workspace ou copie locale). Si le dépôt n'est pas encore cloné, utiliser l'URL documentée pour l'équipe dans ce fichier (section « URL du dépôt git ») ; si cette URL est absente, invalide ou non exploitable, **demander l'URL** à l'utilisateur une seule fois ou signaler que la configuration du dépôt est incomplète.

## Étapes

### 1. Obtenir ou mettre à jour le clone

1. Si **`co-skills` n'existe pas** à l'emplacement canonique : `git clone <url> <chemin-canonique>` (le dossier parent doit exister ; créer les parents si l'OS le permet).
2. Si le dossier **existe** :
   - Vérifier que c'est bien ce dépôt : présence de `.git`, de `AGENT_INSTRUCTIONS.md` et du dossier `skills/` à la racine.
   - Si la structure ne correspond pas : ne pas détruire le contenu ; expliquer et demander instruction à l'utilisateur.
3. Si le dépôt est valide : à sa racine, exécuter `git fetch` puis intégrer les changements distants (ex. `git pull` sur la branche qui suit `origin`, ou pratique d'équipe équivalente).
4. Si **modifications locales non commitées** : ne pas écraser aveuglément ; exposer `git status`, proposer stash / commit / revert selon le souhait de l'utilisateur, ou s'arrêter.
5. En cas de **conflit de fusion** : ne pas résoudre seul sans consigne ; lister les fichiers en conflit et demander comment procéder.

### 2. Resynchroniser les skills vers le dossier global

Après clone ou pull sans blocage :

1. Identifier le **dossier global de skills** de l'outil comme dans `AGENT_INSTRUCTIONS.md` (doc, réglages, ou question minimale à l'utilisateur si indispensable).
2. Pour **chaque sous-dossier** directement sous `skills/` du clone canonique, copier ou fusionner vers ce dossier global (même nom de dossier).
3. **Mettre à jour** les dossiers déjà présents (contenu du dépôt fait foi pour les skills d'équipe).
4. **Ne pas supprimer** les autres skills globaux qui ne viennent pas de ce dépôt.

### 3. Vérification

- Côté clone : branche / commit ou résumé court du dernier `pull` (ou message indiquant que le clone vient d'être créé).
- Côté global : chaque `skills/<nom>/` du dépôt a un équivalent avec `SKILL.md` (et annexes si présentes dans le dépôt).

## Si l'agent ne peut pas exécuter git ou écrire les fichiers

Fournir les commandes exactes : `git clone` ou `cd` + `git pull` sur le chemin canonique, puis copie `…/co-skills/skills/<nom>/` vers le dossier global convenu.
