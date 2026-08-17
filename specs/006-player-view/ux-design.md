# UX Design 006 — Player View

- **Spec**: `spec.md` · **Date**: 2026-08-17
- **Rule**: Semantic role before component. Define WHAT each element means before HOW it looks.

---

## Purpose

Individual clan member sees their own performance across wars. They enter their player tag
(#ABC123) and see their personal history — attacks, points, cards, trend — without seeing
any other member's data. This is a privacy-respecting individual view, distinct from the
clan-wide dashboard.

**Journey served**: A clan member checks their own performance to understand if they are at
risk of receiving cards, how they trend, and what to improve — without seeing everyone else.

---

## Semantic Objects

| Object | Role | Journey | States |
|---|---|---|---|
| **Player lookup input** | Tag entry — visitor identifies themselves | Member identification | `empty`, `typing`, `invalid-format`, `not-found`, `found` |
| **Lookup submit** | Action — resolve tag to player data | Member identification | `idle`, `loading`, `error` |
| **Player header** | Player identification — name, tag, role, avatar | Context for all subsequent data | `found` (rendered), `not-found` (hidden) |
| **Current war summary** | Personal war snapshot — attacks today/total, points, cards, status | Member assesses current war | `active` (war running), `no_war` (no active war), `not_participating` (player not in war) |
| **Attacks today** | Daily attack count for the current war day | Member checks today's participation | `complete` (4/4), `partial` (1-3/4), `zero` (0/4) |
| **Points total** | Fame/points earned in the current war | Member checks contribution | numeric display |
| **Cards summary** | Accumulated cards in the recency window | Member checks card standing | `clean` (0 cards), `warning` (yellows), `danger` (reds), `critical` (blacks) |
| **Trend indicator** | Behavior direction over recent wars | Member understands trajectory | `improving`, `stable`, `declining`, `new` (insufficient data) |
| **War history list** | Past wars with points, cards, attacks per day | Member reviews track record | `loaded` (4 weeks), `expanded` (3 months), `loading`, `empty` (no history) |
| **Personal scope banner** | Context — declares this is an individual view, no clan data shown | Visitor orientation | `visible` |
| **Back to landing** | Navigation — return to entry point | Visitor retreats | `idle`, `hover`, `focus` |

### Roles consumed from catalogue

| Role | Source | Adaptation |
|---|---|---|
| Player header | 001 T2 | Same role, standalone page (not modal) |
| Current war table | 001 T2 | Simplified to summary (personal scope, no clan comparison) |
| Trend indicator | 001 T2 | Unchanged — improving/stable/declining/new |
| History table | 001 T2 | Unchanged — 4 weeks expandable to 3 months |
| Status badge | 001 T2 | Unchanged — clean/warning/danger/critical |
| Cards indicator | 001 T1 | Unchanged — yellow/red/black with counts |

### Roles introduced to catalogue

- `player-lookup-input` — tag entry field for self-identification
- `personal-scope-banner` — context declaration that this view is individual, not clan-wide

---

## Interaction Patterns

1. **Tag entry first**: the page starts with the lookup input. No player data is shown until
   a valid tag is resolved. This is the gate — without it, nothing else renders.
2. **Lookup flow**: visitor types tag → submits → system resolves via API → on success, player
   data renders below; on failure, error message appears inline (no redirect).
3. **Personal scope is explicit**: a banner declares "Esta é sua visão individual — dados do
   clã não são exibidos." This prevents confusion with the clan dashboard.
4. **History expansion**: the war history list shows 4 weeks by default. An expand control
   loads 3 months (consumed from 001 T2 expand button role).
5. **No clan comparison**: unlike the clan dashboard, this view never shows other players'
   data, clan position, or relative ranking. The member sees only their own metrics.

---

## Visual Hierarchy

```
1. Personal scope banner (context, always visible)
2. Player lookup input + submit (gate — dominant until resolved)
   --- gate passed ---
3. Player header (name, tag, role, avatar)
4. Current war summary (attacks today, points, cards, status)
5. Trend indicator (single prominent signal)
6. War history list (scrollable, expandable)
7. Back to landing (footer-level navigation)
```

Before lookup resolution, the input dominates. After resolution, the player header and current
war summary take precedence — the member wants to know "how am I doing right now?" History
supports but sits below the fold.

---

## Accessibility

- Lookup input has an associated `<label>` (visually positioned for screen readers).
- Submit button has text label "Buscar" (not icon-only).
- Invalid tag format shows an inline error with `role="alert"`.
- Not-found result shows an inline message with `role="status"`.
- Trend indicator uses text + icon (not color alone): "Melhorando" + arrow icon.
- War history list is a semantic `<table>` with column headers for screen readers.
- Focus order: lookup input → submit → player header → history → expand → back.
- `prefers-reduced-motion`: trend indicator and list transitions disabled.

---

## States

| State | Description |
|---|---|
| `empty` | No tag entered, lookup input focused |
| `loading` | Tag submitted, API resolving |
| `invalid-format` | Tag does not match expected format (# + alphanumeric) |
| `not-found` | Tag valid format but no player found in clan |
| `found` | Player resolved, all data rendered |
| `no-war` | Player found but no active war (history still shown) |
| `error` | API failure, retry prompt shown |
