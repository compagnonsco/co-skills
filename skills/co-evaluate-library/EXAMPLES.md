# Exemples — /co-evaluate-library

3 exemples de scénarios couverts par le skill.

---

## Exemple 1 — Deep dive sur une lib (npm)

**Invocation**: `/co-evaluate-library zod`

**Comportement attendu**:

1. Détecte écosystème = npm (nom court, scope vide)
2. Lit `package.json` du cwd → détecte Nuxt 4 + TypeScript
3. Lance 3 agents en parallèle:
   - Agent A: `curl https://registry.npmjs.org/zod` → version, license, deps
   - Agent B: `gh api /repos/colinhacks/zod` → stars, last commit, contributors
   - Agent C: `gh api /repos/colinhacks/zod/security-advisories` → CVE
4. Tout vert → pas d'escalade
5. Check-in: "Privacy/Loi 25 — zod traite tout localement, pas de telemetry. Verdict 🟢?"
6. Affiche tableau:

```
**zod** — npm — `3.23.8`

| Critère          | Verdict | Notes |
|------------------|---------|-------|
| Stack fit        | 🟢      | Compatible Nuxt 4, types natifs TS |
| Maintenance      | 🟢      | release toutes 2 sem, 8 mainteneurs |
| Adoption         | 🟢      | 12M dl/sem, 33k stars |
| Sécurité         | 🟢      | 0 CVE 2y |
| Licence          | 🟢      | MIT |
| Privacy/Loi 25   | 🟢      | aucun network call |
| Pérennité        | 🟡      | colinhacks domine (bus factor 2) |
| TCO              | 🟢      | Free, OSS, deps minimales |
| Performance      | 🟡      | +14KB gzip |
| Accessibilité    | —       | N/A (pas UI) |

→ **Reco: 🟢 Go** — caveat: surveiller colinhacks (bus factor).
```

7. Demande: "Push dans Régistre des librairies? (oui/non/projet?)"

---

## Exemple 2 — Comparaison de 3 libs

**Invocation**: `/co-evaluate-library zod yup valibot`

**Comportement attendu**:

1. Mode comparaison, 3 libs npm
2. Lance 9 agents en parallèle (3 sources × 3 libs)
3. Détecte que valibot est moins établie → escalade Bundlephobia + WebSearch pour comparer perfs
4. Tableau côte-à-côte:

```
| Critère          | zod         | yup         | valibot     |
|------------------|-------------|-------------|-------------|
| Stack fit        | 🟢          | 🟢          | 🟢          |
| Maintenance      | 🟢          | 🟡 (slower) | 🟢          |
| Adoption         | 🟢 12M/sem  | 🟢 9M/sem   | 🟡 500k/sem |
| Sécurité         | 🟢          | 🟢          | 🟢          |
| Licence          | 🟢 MIT      | 🟢 MIT      | 🟢 MIT      |
| Privacy/Loi 25   | 🟢          | 🟢          | 🟢          |
| Pérennité        | 🟡          | 🟡          | 🟡          |
| TCO              | 🟢          | 🟢          | 🟢          |
| Performance      | 🟡 14KB     | 🟡 41KB     | 🟢 1KB tree |
| Accessibilité    | —           | —           | —           |

→ **Reco comparative**:
   - 🟢 zod si stabilité/adoption prio
   - 🟢 valibot si bundle critique (mobile, edge)
   - 🟡 yup, dépassé par les 2 autres pour les usages modernes
```

5. Push 3 rows dans Notion (1 par lib) après confirmation.

---

## Exemple 3 — Lib NuGet sans stack détectée

**Invocation**: `/co-evaluate-library MediatR` depuis `~` (pas un projet)

**Comportement attendu**:

1. Détecte écosystème: nom CamelCase typique .NET → tester NuGet d'abord
2. Pas de manifest projet dans cwd → demande "Tu évalues pour quel projet/stack?"
3. L'utilisateur: ".NET 8 + Umbraco 13"
4. Lance agents:
   - Agent A: `curl https://api.nuget.org/v3/registration5-semver1/mediatr/index.json`
   - Agent B: `gh api /repos/jbogard/MediatR`
   - Agent C: `gh api /repos/jbogard/MediatR/security-advisories`
5. ⚠️ Drapeau rouge détecté: MediatR est passé commercial en v12 → escalade WebSearch
6. WebSearch confirme: passage commercial 2024, forks/alternatives émergent
7. Check-in: "Privacy/Loi 25 — pas applicable côté lib elle-même. Verdict ⚪?"
8. Tableau:

```
**MediatR** — NuGet — `13.0.0`

| Critère          | Verdict | Notes |
|------------------|---------|-------|
| Stack fit        | 🟢      | .NET 8 compatible |
| Maintenance      | 🟢      | release/mois |
| Adoption         | 🟢      | 200M+ downloads historique |
| Sécurité         | 🟢      | 0 CVE |
| Licence          | 🔴      | Commercial v12+ (license payante prod) |
| Privacy/Loi 25   | ⚪      | N/A (logique in-process) |
| Pérennité        | 🟢      | jbogard actif |
| TCO              | 🔴      | $400+/an/dev pour usage commercial |
| Performance      | 🟢      | overhead négligeable |
| Accessibilité    | —       | N/A |

→ **Reco: 🔴 No-go** (sauf si budget licence ok) — alternatives gratuites: Wolverine, FastEndpoints, ou rouler son propre mediator (~50 lignes).
```

9. Push dans Notion avec champ Notes/Caveats détaillant le pivot commercial.

---

## Notes sur le mode interactif

Si l'utilisateur tape juste `/co-evaluate-library`, démarrer avec:

> "Quelle lib tu veux évaluer? Ou tu veux comparer 2-3 libs?"

Puis suivre le flow normal selon la réponse.
