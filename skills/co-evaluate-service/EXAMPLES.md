# Exemples — /co-evaluate-service

3 exemples couvrant les principaux scénarios de la grille 15D.

---

## Exemple 1 — Outil avec no-go automatique (Granola)

**Invocation**: `/co-evaluate-service Granola`

**Comportement attendu**:

1. Détecte: Catégorie AI/LLM (note-taker), URL `https://granola.ai`
2. Lance 7 agents secondaires en parallèle:
   - Trust Center → `granola.ai/security`
   - DPA → `granola.ai/dpa`
   - Privacy → `granola.ai/privacy`
   - ToS → `granola.ai/terms`
   - Status → cherche `status.granola.ai`
   - Subprocessors → linked depuis Privacy
   - WebSearch → "Granola SOC2", "Granola security 2025"
3. Agrège les findings + scoring 15 dim
4. Check-in sur les 5 dim critiques → score Critère 14 (posture menaces IA) = 1 → NO-GO auto
5. Tableau:

```
**Granola** — AI/LLM — https://granola.ai

| # | Dimension | Score | Justification |
|---|-----------|-------|---------------|
| 1 | Infrastructure | 3 | Cloud public sans détails isolation |
| 2 | Chiffrement | 4 | TLS 1.3 + AES-256 mentionnés |
| 3 | Conservation | 3 | 90 jours par défaut, configurable |
| 4 ⚠️ | Droit utilisation | 2 | Usage étendu "amélioration produit" sans opt-out clair |
| 5 ⚠️ | Emplacement | 2 | USA sans option Canada |
| 6 | Propriété | 3 | Ma propriété mentionnée ToS |
| 7 ⚠️ | Entraînement | 2 | Opt-in par défaut, opt-out caché |
| 8 | Partage 3rd | 3 | Liste de subprocessors publique |
| 9 | Cryptage technique | 4 | AES-256 + TLS 1.3 |
| 10 ⚠️ | Conformité documentée | 2 | SOC2 "en cours", pas Type II |
| 11 | SLA disponibilité | 2 | Status page sans engagement contractuel |
| 12 | Authentification & IAM | 3 | MFA optionnelle, pas SSO |
| 13 | Sécurité connecteurs/API | 2 | API sans détails OAuth |
| 14 ⚠️ | Posture menaces IA | 1 | Aucune doc sur prompt injection/empoisonnement |
| 15 | Procédure incident IA | 2 | Procédure générique, pas spécifique IA |

**Score total**: 38/75  |  **Nb no-go auto**: 1 (Critère 14)

→ **Verdict: 🔴 Rouge (no-go automatique sur Critère 14)**

**Conditions de remédiation pour repasser à Jaune**:
1. Obtenir documentation posture menaces IA (Critère 14)
2. Activer opt-out training par défaut + clause contractuelle (Critère 7)
3. Confirmer date SOC2 Type II + ajouter option région Canada (Critère 5, 10)
```

6. Push Notion après confirmation.

---

## Exemple 2 — Outil Vert (Anthropic Claude API Team)

**Invocation**: `/co-evaluate-service "Anthropic Claude API"`

**Comportement attendu**:

1. Catégorie AI/LLM, URL `https://anthropic.com`
2. Sub-agents trouvent: trust.anthropic.com, DPA dédié, Privacy Policy détaillée, SOC2 Type II + ISO27001
3. Tableau:

```
**Anthropic Claude API (Team)** — AI/LLM — https://www.anthropic.com

| # | Dimension | Score | Justification |
|---|-----------|-------|---------------|
| 1 | Infrastructure | 4 | AWS dédié, isolation logique documentée |
| 2 | Chiffrement | 5 | AES-256 + CMK option (Enterprise) |
| 3 | Conservation | 4 | 30 jours par défaut, configurable |
| 4 ⚠️ | Droit utilisation | 5 | Service-only explicite + DPA |
| 5 ⚠️ | Emplacement | 4 | USA avec choix de région + DPA encadrée |
| 6 | Propriété | 5 | Propriété client explicite |
| 7 ⚠️ | Entraînement | 5 | Opt-out par défaut Team/Enterprise |
| 8 | Partage 3rd | 5 | Liste publique + notification 30j |
| 9 | Cryptage technique | 5 | AES-256 + TLS 1.3 |
| 10 ⚠️ | Conformité documentée | 5 | SOC2 Type II + ISO27001 + GDPR + HIPAA |
| 11 | SLA disponibilité | 4 | 99.9% SLA contractuel |
| 12 | Authentification & IAM | 4 | SSO + MFA + rôles organisation |
| 13 | Sécurité connecteurs/API | 4 | OAuth + API keys + logs |
| 14 ⚠️ | Posture menaces IA | 5 | Red team documenté + tests sécu publiés |
| 15 | Procédure incident IA | 4 | Procédure + notification documentée |

**Score total**: 67/75  |  **Nb no-go auto**: 0

→ **Verdict: 🟢 Vert** — signature avec confiance.

Aucune condition de remédiation requise. À noter pour revue annuelle.
```

---

## Exemple 3 — Comparaison de 3 outils

**Invocation**: `/co-evaluate-service Granola Otter Fireflies`

**Comportement attendu**:

1. Mode comparaison, 3 outils AI/LLM (note-takers)
2. Lance 21 agents secondaires en parallèle (7 sources × 3 outils)
3. Tableau side-by-side:

```
**Comparaison note-takers IA** — AI/LLM

| # | Dimension | Granola | Otter | Fireflies |
|---|-----------|---------|-------|-----------|
| 1 | Infrastructure | 3 | 4 | 3 |
| 2 | Chiffrement | 4 | 4 | 4 |
| 3 | Conservation | 3 | 4 | 3 |
| 4 ⚠️ | Droit utilisation | 2 | 3 | 2 |
| 5 ⚠️ | Emplacement | 2 | 3 | 2 |
| 6 | Propriété | 3 | 4 | 3 |
| 7 ⚠️ | Entraînement | 2 | 4 | 2 |
| 8 | Partage 3rd | 3 | 4 | 3 |
| 9 | Cryptage technique | 4 | 5 | 4 |
| 10 ⚠️ | Conformité documentée | 2 | 4 | 3 |
| 11 | SLA disponibilité | 2 | 4 | 3 |
| 12 | Authentification & IAM | 3 | 4 | 3 |
| 13 | Sécurité connecteurs/API | 2 | 3 | 2 |
| 14 ⚠️ | Posture menaces IA | 1 | 2 | 1 |
| 15 | Procédure incident IA | 2 | 3 | 2 |
| **Total** | | **38/75** | **53/75** | **40/75** |
| **No-go** | | 1 (Critère 14) | 0 | 1 (Critère 14) |
| **Verdict** | | 🔴 Rouge | 🟡 Jaune | 🔴 Rouge |

→ **Reco comparative**:
   - 🟡 **Otter** est le seul candidat viable — signature avec conditions (renégocier opt-out par défaut + ajout DPA Canada)
   - 🔴 Granola et Fireflies = no-go sur posture menaces IA (Critère 14)
   - Si aucun acceptable, considérer alternatives self-hosted (Whisper local + transcription locale)
```

4. Push 3 rows séparées dans Notion (1 par outil).

---

## Notes sur le mode interactif

Si l'utilisateur tape juste `/co-evaluate-service`, démarrer avec:

> "Quel outil tu veux évaluer? Ou tu veux comparer 2-3 outils?"

Puis suivre le flow normal selon la réponse.

---

## Note sur les exemples

Les scores affichés ci-dessus sont **illustratifs** — ils représentent ce que le skill pourrait produire mais ne sont pas issus d'une évaluation réelle au moment de l'écriture. Le skill lui-même fait toujours sa propre recherche au moment de l'exécution.
