# UX Design 007 — Clan View Improvements

- **Spec**: `spec.md` · **Date**: 2026-08-17
- **Rule**: Semantic role before component. Define WHAT each element means before HOW it looks.

---

## Purpose

Fix the9 unusable dashboard — 92 player cards in a grid with no sorting, no filtering, and
no war context. Replace the card gridA with a sortable, filterable list/table that lets a
leader evaluate 92 members efficiently. Enhance the war status banner with daily point
breakdown and clan race context.

**Journey served**: A leader opens the clan view, sees the war context, filters to active
war participants, sorts by worst-standing first, and identifies critical members in under
10 seconds — even with 92 members.

---

## Semantic Objects

| Object | Role | Journey | States |
|---|---|---|---|
| **War status banner** | War context — clan name, race position, daily points (Thu/Fri/Sat/Sun), total fame, relaxed status | Leader orients before evaluating | `active` (war running, day N of 4), `finished` (war ended, final position), `no_war` (no active war), `relaxed` (early victory, rules suspended) |
| **Daily points breakdown** | Per-day fame earned — Thu/Fri/Sat/Sun columns | Leader tracks race progress | `active` (current day highlighted), `pending` (future days dimmed), `complete` (past days filled) |
| **Sortable member table** | Evaluation surface — one row per member, sortable by any column | Leader evaluates 92 members efficiently | `loaded`, `loading` (skeleton rows), `empty` (no members), `error` (API failure) |
| **Table column — name** | Member identification | Leader locates a member | text, sortable A→Z / Z→A |
| **Table column — status** | Evaluation status badge | Leader identifies critical members | `clean`, `warning`, `danger`, `critical` — sortable worst→best (default) |
| **Table column — attacks today** | Daily attack count | Leader sees who hasn't attacked today | `complete` (4/4), `partial`, `zero` — sortable |
| **Table column — attacks total** | War-total attack count | Leader sees overall participation | numeric, sortable |
| **Table column — points** | Fame/points in current war | Leader sees contribution | numeric, sortable |
| **Table column — cards** | Accumulated yellow/red/black cards | Leader sees card standing | badge counts, sortable by severity |
| **Filter toggle — active war only** | "Somente jogadores da guerra atual" — hides inactive members | Leader focuses on participants | `on` (inactive hidden), `off` (all 92 shown) |
| **Search box** | Name filter — narrows the list by text match | Leader locates a specific member | `empty`, `typing`, `no-match` |
| **View mode toggle** | Switch between table and card grid | Leader on small screen uses cards | `table` (default), `cards` (small screens) |
| **Summary stats row** | Aggregate metrics — total players, critical count, alert count, attack % | Leader gets the big picture at a glance | `loaded`, `loading` |
| **Refresh button** | Re-collect from API and re-evaluate | Leader refreshes after attacks | `idle`, `loading`, `error` |

### Roles consumed from catalogue

| Role | Source | Adaptation |
|---|---|---|
| War status bar | 001 T1 | Enhanced — adds daily points breakdown, clan name, total fame |
| Early victory badge | 001 T1 | Consumed unchanged — shown within banner when relaxed |
| Player row | 001 T1 | Evolved into sortable table row (same evaluation-unit role) |
| Attacks indicator | 001 T1 | Unchanged — reused as table column |
| Cards indicator | 001 T1 | Unchanged — reused as table column |
| Status badge | 001 T2 | Unchanged — reused as table column |
| Sort control | 001 T1 | Enhanced — now sortable by any column, not just 3 fixed options |
| Refresh button | 001 T1 | Unchanged |
| Summary stats row | 004 US2 | Consumed — total players, critical, alerts, attack % |

### Roles introduced to catalogue

- `daily-points-breakdown` — per-day fame columns (Thu/Fri/Sat/Sun) within the war status banner
- `sortable-member-table` — full sortable/filterable table replacing the card grid as default view
- `filter-toggle-active-war` — boolean filter hiding inactive members from the list
- `member-name-search` — text filter narrowing the member list by name
- `view-mode-toggle` — switch between table and card grid presentation

---

## Interaction Patterns

1. **Table is the default**: the sortable table replaces the card grid as the primary view.
   92 cards in a grid is visually overwhelming; a table is scannable and compact.
2. **Sort by any column**: clicking a column header sorts ascending; clicking again sorts
   descending. Default sort: status worst→best (critical first), matching 001 FR3.1.2.
3. **Filter before scan**: the "active war only" toggle is on by default — the leader sees
   war participants first. Toggling off reveals all 92 members including inactive.
4. **Search narrows further**: typing in the search box filters the list by name (case-
   insensitive substring match). Works in combination with the active-war filter.
5. **Card view as fallback**: the view-mode toggle switches to the card grid (from spec 004)
   for small screens where a table is unreadable. This is an accessibility/responsive escape
   hatch, not the primary experience.
6. **War banner is always visible**: sticky at the top, the banner keeps war context present
   while the leader scrolls through 92 rows.
7. **Row click → player detail**: clicking a member row opens the player detail (001 T2 modal).
   This interaction is unchanged from the existing dashboard.

---

## Visual Hierarchy

```
1. War status banner (sticky, always visible)
   ├── Clan name + race position
   ├── Daily points breakdown (Thu/Fri/Sat/Sun)
   ├── Total fame
   └── Relaxed status badge (if early victory)
2. Summary stats row (total, critical, alerts, attack %)
3. Controls row
   ├── Search box (left, grows)
   ├── Filter toggle — active war only
   ├── View mode toggle — table/cards
   └── Refresh button (right)
4. Sortable member table (fills remaining viewport)
   ├── Column headers (sortable, sort indicator on active)
   └── Member rows (one per member, status-colored)
```

The banner anchors context. Stats give the 3-second overview. Controls are grouped in one row.
The table fills the rest — this is where the leader spends their time.

---

## Accessibility

- Table is a semantic `<table>` with `<thead>` and `<tbody>`. Column headers are `<th>` with
  `aria-sort` reflecting current sort direction ("ascending" / "descending" / "none").
- Sortable headers are buttons within `<th>` — keyboard accessible via Enter/Space.
- Filter toggle is a `role="switch"` with `aria-checked` and a visible text label.
- Search box has an associated `<label>` and `aria-placeholder`.
- View mode toggle uses `role="radiogroup"` with two `role="radio"` options.
- Status badges use text + color (not color alone): "Crítico", "Alerta", "Perigo", "Limpo".
- Daily points breakdown: each day column has a header cell with the day abbreviation.
- Refresh button has text label "Atualizar" (not icon-only).
- Table rows are keyboard navigable; Enter on a row opens player detail.
- `prefers-reduced-motion`: sort transitions and row hover effects disabled.

---

## States

| State | Description |
|---|---|
| `loading` | Skeleton rows in table, skeleton in banner, stats show placeholders |
| `loaded` | Full data rendered, table sortable/filterable |
| `empty` | No members found (clan has 0 members or API returned empty) |
| `no-war` | No active war — banner shows "Sem guerra ativa", table shows last-evaluated data |
| `error` | API failure — banner shows error, table shows last cached data with stale indicator |
| `filtered-empty` | Filters/search yield no matches — "Nenhum membro corresponde aos filtros" |
| `relaxed` | Early victory active — banner shows relaxed badge, card issuance suspended note |
