# Changelog

All notable changes to ClashClanEvaluation are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), semver.

## [0.2.0] — 2026-08-16

### Added
- **Design system** (Spec 003): Tailwind CSS 4 configured with `@theme` block — 30+ design tokens
  (surface colors, primary/accent, card colors, text hierarchy, fonts, radius, shadows, easing).
- **16 new UI components**: Icon (22 SVG icons), Button (4 variants), Card, StatChip, CardBadge,
  StatusBadge, TrendIndicator, WarProgressBar, Skeleton, Toast (provider + hook), Modal, Logo,
  ToggleSwitch, Layout, PlayerCard, ErrorBoundary.
- **UI redesign** (Spec 004): Dashboard with card grid + war progress bar, PlayerDetail with card
  layout + stat chips, ConfigPanel with styled sections + toggle + modal confirmation.
- **Page transitions** via View Transitions API (`document.startViewTransition`).
- **Skeleton loading** with shimmer animation matching loaded layout.
- **Toast notifications** with `aria-live`, auto-dismiss after 4s.
- **Error Boundary** to catch render crashes and display error + stack trace.
- **Branding footer** (Spec 002): "Desenvolvido por GHDaru Tecnologia" with link to ghdaru.com.br.
- **Accessibility**: `color-scheme: dark`, `focus-visible` rings, `touch-action: manipulation`,
  `tabular-nums`, `prefers-reduced-motion` support, keyboard navigation on player cards.
- **ADRs**: 0002 (design system choice), 0003 (error boundary).

### Changed
- `frontend/src/App.tsx`: Wrapped in ToastProvider + ErrorBoundary, uses Layout shell, View Transitions.
- `frontend/src/pages/Dashboard.tsx`: Table → responsive card grid, added war progress + summary stats.
- `frontend/src/pages/PlayerDetail.tsx`: Plain HTML → card layout with StatChip grid + timeline.
- `frontend/src/pages/ConfigPanel.tsx`: Plain form → card sections + ToggleSwitch + Modal + Toast.
- `frontend/src/main.tsx`: Added `import "./index.css"` + ErrorBoundary wrapper.
- `frontend/index.html`: Added `color-scheme`, `theme-color`, Google Fonts, `class="dark"`.
- `frontend/vite.config.ts`: Added `@tailwindcss/vite` plugin.
- `backend/infrastructure/config.py`: Fixed `.env` path to absolute (was relative to CWD).
- `backend/.env`: Changed `DATABASE_URL` to `postgresql+asyncpg://` with `ssl=require`.
- `backend/infrastructure/adapter/secondary/sql_repositories.py`: Upsert clan + players before war
  (FK constraint fix), persist player_wars with `.count` for cards.

### Removed
- `frontend/src/components/PlayerRow.tsx`: Replaced by `PlayerCard.tsx`.

### Fixed
- Tailwind CSS not generating styles (missing `@tailwindcss/vite` plugin).
- Backend `.env` not loading (relative path → absolute via `Path(__file__)`).
- `ModuleNotFoundError: psycopg2` → installed `asyncpg`, changed driver in `DATABASE_URL`.
- `ForeignKeyViolationError` on wars table → upsert clan + players first via `session.merge()`.
- `AttributeError: 'YellowCard' has no attribute 'value'` → use `.count` for card value objects.

## [0.1.0] — 2026-08-15

### Added
- Initial ClashClanEvaluation system (Spec 001): FastAPI backend with hexagonal architecture,
  Clash Royale API integration, evaluation engine (cards, recency, relaxation), React frontend
  with TanStack React Query, PostgreSQL on Neon.
