# UX Design 005 — Landing Page

- **Spec**: `spec.md` · **Date**: 2026-08-17
- **Rule**: Semantic role before component. Define WHAT each element means before HOW it looks.

---

## Purpose

Entry point for the ClashClanEvaluation system. A visitor lands here first and must understand
what the system does and choose one of two paths: clan view (for leaders/co-leaders evaluating
the whole clan) or player view (for individual members checking their own performance).

**Journey served**: Any visitor — leader, member, or curious outsider — understands the system's
purpose in under 10 seconds and selects their path without confusion.

---

## Semantic Objects

| Object | Role | Journey | States |
|---|---|---|---|
| **Hero** | System introduction — names the system and states its purpose | Visitor orientation | `default` |
| **Hero subtitle** | Explains the system evaluates clan participation in River Race wars | Visitor orientation | `default` |
| **Feature highlight card** | Capability explanation — one of three system pillars | Visitor understanding | `default`, `hover` (elevated) |
| **Feature: Card system** | Explains the yellow/red/black card evaluation model | Visitor understanding | `default` |
| **Feature: Recency & history** | Explains recency window and historical tracking | Visitor understanding | `default` |
| **Feature: Rule relaxation** | Explains automatic rule relaxation on early victory | Visitor understanding | `default` |
| **Primary CTA — "Ver dados do Clã"** | Path selection — clan-wide evaluation (leader path) | Leader journey start | `idle`, `hover`, `focus`, `active` |
| **Secondary CTA — "Ver minha performance"** | Path selection — individual performance (member path) | Member journey start | `idle`, `hover`, `focus`, `active` |

### Roles consumed from catalogue

None — this is the entry point. All roles are introduced here.

### Roles introduced to catalogue

- `hero` — system introduction block (title + subtitle)
- `feature-highlight-card` — capability explanation card
- `path-cta` — journey selection action (primary/secondary variants)

---

## Interaction Patterns

1. **Single decision point**: the page presents exactly two paths. No nested menus, no
   secondary navigation. The visitor picks one CTA.
2. **Primary vs secondary distinction**: "Ver dados do Clã" is the primary CTA (the system's
   main purpose is clan evaluation). "Ver minha performance" is secondary (a convenience path
   for members). Visual weight communicates this hierarchy.
3. **Feature cards are informational, not interactive**: they explain the system but do not
   link anywhere. Hover elevation is a visual affordance only, not a navigation trigger.
4. **CTA navigation**:
   - Primary CTA → existing dashboard (clan view, spec 001/004)
   - Secondary CTA → player lookup (spec 006-player-view)

---

## Visual Hierarchy

```
1. Hero title (largest, system identity)
2. Hero subtitle (secondary text, purpose statement)
3. Feature highlight cards (3 across, equal weight)
4. Primary CTA (highest visual weight among actions)
5. Secondary CTA (lower visual weight, distinct from primary)
```

The hero dominates the viewport. Feature cards sit below as supporting evidence. CTAs are
grouped below the cards — the visitor reads what the system does, then acts.

---

## Accessibility

- Each CTA has a visible text label (no icon-only controls on this page).
- Focus-visible ring on both CTAs, tab order: primary CTA first, secondary CTA second.
- Feature cards are not focusable (they are not interactive).
- Color is not the sole differentiator between primary and secondary CTA — size/weight differs.
- `prefers-reduced-motion`: hover elevation transitions disabled.

---

## States

| State | Description |
|---|---|
| `default` | Page fully loaded, both CTAs active |
| `navigating` | CTA clicked, transition to destination page |
