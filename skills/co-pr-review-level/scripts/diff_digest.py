#!/usr/bin/env python3
"""Digère un diff pour orienter la classification du niveau de review.

Entrée (stdin) : la sortie de
`git -c core.quotePath=false diff --name-status -M --find-renames <base>...<head>`
(le format Azure DevOps / GitHub qui liste `A/M/D/R###` + chemin(s) fonctionne aussi).

Sortie (stdout) : un digest compact et déterministe qui range chaque fichier dans un bucket,
puis liste les seuls fichiers qui méritent une lecture humaine/agent (code écrit à la main,
fichiers ajoutés), et lève des signaux (nouveau dossier de code, interface ajoutée, logique à
valeur détectée par chemin/convention, dépendances ou config sensibles modifiées).

Le but est double : économiser des tokens (ne pas dumper le diff complet dans le contexte) et
fiabiliser le tri (la distinction généré / renommé / manuel est mécanique, pas une intuition).

Comme le script ne voit que les NOMS de fichiers (jamais le contenu), le tri combine trois
signaux : l'extension, le chemin (conventions de dossier) et la convention de nom. Pour les
formats à composant monofichier où la logique vit dans le même fichier que l'affichage
(`.vue`, `.svelte`, `.razor`), le défaut sûr est de traiter le fichier comme du code à lire :
un peu de bruit présentationnel vaut mieux qu'un faux négatif sur de la vraie logique.

Ce script ne fait AUCUN appel réseau : calcul local uniquement. Récupérer le diff (git, API
Azure/GitHub, etc.) est délégué à l'agent, qui pipe le résultat ici.
"""

import re
import sys
from collections import defaultdict

# Motifs de code réellement généré, à ignorer.
GENERATED_PATTERNS = [
    r"\.generated\.",           # Umbraco / EF / codegen divers
    r"\.designer\.cs$",
    r"\.g\.cs$",
    r"\.g\.i\.cs$",
    r"\.d\.ts$",                # déclarations TypeScript générées
    r"\.gen\.(ts|js)$",         # TanStack routeTree.gen.ts, etc.
    r"(^|/)__generated__/",     # GraphQL codegen
    r"(^|/)\.nuxt/",
    r"(^|/)\.output/",
    r"(^|/)\.next/",
    r"(^|/)dist/",
    r"(^|/)node_modules/",
    r"(^|/)package-lock\.json$",
    r"(^|/)yarn\.lock$",
    r"(^|/)pnpm-lock\.yaml$",
    r"(^|/)poetry\.lock$",
    r"(^|/)Cargo\.lock$",
    r"(^|/)composer\.lock$",
    r"\.min\.(js|css)$",
    r"\.map$",
]
# NB : les migrations ne sont PAS ici. Elles sont régulièrement éditées à la main (SQL brut,
# backfills, index) et doivent être lues. Seul leur compagnon `.designer.cs` est vraiment généré.

CONTENT_CONFIG_EXT = {
    ".config", ".resx", ".json", ".xml", ".yml", ".yaml", ".md", ".csv", ".txt",
}
# Affichage pur. NB : `.cshtml` (vues Razor/Umbraco) est de l'affichage ; `.vue`/`.svelte`/
# `.razor` sont traités comme du code car leur logique vit dans le même fichier.
VIEW_MARKUP_EXT = {
    ".cshtml", ".html", ".htm", ".aspx", ".css", ".scss", ".less", ".sass",
}
CODE_EXT = {
    ".cs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".go", ".rb",
    ".java", ".php", ".kt", ".swift", ".rs", ".cpp", ".c", ".h",
    ".vue", ".svelte", ".razor",   # logique dans le <script>/@code
    ".prisma", ".sql",             # modèle de données / schéma = haute valeur
}
ASSET_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".zip", ".bin",
}

# Dépendances / config sensibles : on ne les lit pas forcément, mais on signale leur
# modification (nouvelle intégration, secret, flag de prod, changement de schéma).
SENSITIVE_PATTERNS = [
    r"(^|/)package\.json$",
    r"\.csproj$",
    r"\.sln$",
    r"(^|/)appsettings.*\.json$",
    r"\.sql$",
    r"(^|/)schema\.prisma$",
]

# Chemins / conventions qui portent de la logique à valeur (élèvent le niveau).
VALUE_PATH_PATTERNS = [
    r"(^|/)server/api/",
    r"(^|/)server/routes/",
    r"(^|/)server/middleware/",
    r"(^|/)middleware/",
    r"(^|/)stores/",
    r"(^|/)composables/",
]
VALUE_NAME_PATTERNS = [
    r"Handler\.cs$",
    r"Service\.cs$",
    r"Repository\.cs$",
    r"Controller\.cs$",
    r"(^|/)Program\.cs$",
    r"(^|/)Startup\.cs$",
]


def unquote_git_path(path):
    """Dé-quote un chemin quoté par git (core.quotePath=true) : `"caf\\303\\251.py"`.

    Robustesse : le SKILL.md recommande `-c core.quotePath=false`, mais si l'agent oublie le
    flag, on décode quand même les échappements C-style (octal des octets UTF-8 + \\t \\n etc.).
    """
    if len(path) >= 2 and path[0] == '"' and path[-1] == '"':
        inner = path[1:-1]
        out = bytearray()
        simple = {"a": 7, "b": 8, "t": 9, "n": 10, "v": 11, "f": 12, "r": 13, '"': 34, "\\": 92}
        i = 0
        while i < len(inner):
            c = inner[i]
            if c == "\\" and i + 1 < len(inner):
                nxt = inner[i + 1]
                if nxt in simple:
                    out.append(simple[nxt])
                    i += 2
                    continue
                if nxt in "01234567":
                    j = i + 1
                    while j < len(inner) and j < i + 4 and inner[j] in "01234567":
                        j += 1
                    out.append(int(inner[i + 1:j], 8) & 0xFF)
                    i = j
                    continue
                out.append(ord(nxt))
                i += 2
                continue
            out.extend(c.encode("utf-8"))
            i += 1
        return out.decode("utf-8", "replace")
    return path


def ext_of(path):
    m = re.search(r"(\.[A-Za-z0-9]+)$", path)
    return m.group(1).lower() if m else ""


def is_generated(path):
    return any(re.search(p, path) for p in GENERATED_PATTERNS)


def bucket_of(path):
    if is_generated(path):
        return "generated"
    e = ext_of(path)
    if e in CODE_EXT:
        return "code"
    if e in VIEW_MARKUP_EXT:
        return "view"
    if e in CONTENT_CONFIG_EXT:
        return "content"
    if e in ASSET_EXT:
        return "asset"
    return "other"


def parse_line(line):
    """Retourne (status, path, is_pure_rename) ou None.

    status ∈ {A, M, D, R, C}. Pour un rename/copy, path = destination.
    is_pure_rename True si R100/C100 (aucune ligne modifiée).
    """
    line = line.rstrip("\r\n")
    if not line.strip():
        return None
    parts = line.split("\t")
    code = parts[0].strip()
    if not code:
        return None
    letter = code[0].upper()
    if letter in ("R", "C"):
        # Format: R100\told\tnew  (ou C###). La destination est le dernier champ.
        if len(parts) >= 3:
            dest = parts[-1]
        elif len(parts) == 2:
            dest = parts[1]
        else:
            return None
        pct = re.match(r"[RC](\d+)", code)
        pure = bool(pct) and pct.group(1) == "100"
        return (letter, unquote_git_path(dest), pure)
    if letter in ("A", "M", "D", "T", "U"):
        if len(parts) >= 2:
            return (letter, unquote_git_path(parts[-1]), False)
        return None
    return None


def looks_like_numstat(line):
    return bool(re.match(r"^(\d+|-)\t(\d+|-)\t", line))


def main():
    entries = []
    saw_numstat = False
    for raw in sys.stdin:
        if looks_like_numstat(raw):
            saw_numstat = True
        parsed = parse_line(raw)
        if parsed:
            entries.append(parsed)

    if not entries:
        print("DIFF DIGEST : aucune entrée reconnue.")
        if saw_numstat:
            print("On dirait du format --numstat. Utiliser --name-status à la place :")
        print("Attendu : `git -c core.quotePath=false diff --name-status -M --find-renames "
              "<base>...<head>`.")
        return

    counts = defaultdict(int)
    to_read = []          # (status, path) code écrit à la main
    added_code_dirs = defaultdict(list)
    added_interfaces = []
    value_hits = []       # chemins/conventions à valeur
    sensitive_hits = []   # deps / config sensibles

    for status, path, pure in entries:
        if status in ("R", "C") and pure:
            counts["rename"] += 1
            continue
        if status == "D":
            counts["deleted"] += 1
            continue

        if any(re.search(p, path) for p in SENSITIVE_PATTERNS):
            sensitive_hits.append(path)

        b = bucket_of(path)
        counts[b] += 1
        if b == "code":
            to_read.append((status, path))
            if any(re.search(p, path) for p in VALUE_PATH_PATTERNS) or \
               any(re.search(p, path) for p in VALUE_NAME_PATTERNS):
                value_hits.append(path)
            if status == "A":
                d = path.rsplit("/", 1)[0] if "/" in path else "."
                added_code_dirs[d].append(path)
                base = path.rsplit("/", 1)[-1]
                if re.match(r"I[A-Z]", base) or "interface" in base.lower():
                    added_interfaces.append(path)

    total = len(entries)
    print(f"DIFF DIGEST ({total} fichiers)")
    order = [
        ("rename", "Renames / copies purs (mécanique, ignorer)"),
        ("generated", "Code généré (ignorer)"),
        ("content", "Contenu / config (doctype, i18n, settings)"),
        ("view", "Markup / styles (affichage)"),
        ("code", "Code écrit à la main  <-- À LIRE"),
        ("asset", "Assets / binaires"),
        ("deleted", "Supprimés"),
        ("other", "Autre"),
    ]
    for key, label in order:
        if counts.get(key):
            print(f"  - {label}: {counts[key]}")

    print()
    if to_read:
        print("À LIRE pour juger (code écrit à la main) :")
        for status, path in to_read:
            tag = "  [NOUVEAU]" if status == "A" else ""
            print(f"  {status} {path}{tag}")
    else:
        print("À LIRE : aucun code écrit à la main. Changement = contenu / affichage / mécanique.")

    signals = []
    for d, files in added_code_dirs.items():
        if len(files) >= 3:
            signals.append(
                f"Nouveau dossier de code « {d}/ » ({len(files)} fichiers ajoutés) "
                f"-> possible nouveau système réutilisable, vérifier."
            )
    for iface in added_interfaces:
        signals.append(f"Interface ajoutée : {iface} -> abstraction, souvent un système réutilisable.")
    for path in value_hits:
        signals.append(f"Logique à valeur (chemin/convention) : {path} -> endpoint, store, service, contrôleur.")
    if sensitive_hits:
        uniq = sorted(set(sensitive_hits))
        signals.append(
            "Dépendances / config sensibles modifiées : "
            + ", ".join(uniq)
            + " -> vérifier nouvelle intégration, secret ou changement de schéma."
        )

    if signals:
        print()
        print("Signaux :")
        for s in signals:
            print(f"  [!] {s}")


if __name__ == "__main__":
    main()
