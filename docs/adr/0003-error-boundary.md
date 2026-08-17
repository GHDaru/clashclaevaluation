# ADR 0003 — Error Boundary for Render Crash Resilience

- **Status**: Accepted
- **Date**: 2026-08-16
- **Related specs**: 004-ui-redesign

## Context

The frontend exhibited a blank screen after data loaded from the API. Without an Error Boundary,
any runtime error during React render unmounts the entire component tree, leaving a blank white
page with no diagnostic information.

## Decision

Add a class-based `ErrorBoundary` component that wraps the entire app (inside `StrictMode`, outside
`QueryClientProvider`). On error, it displays the error message, component stack, and a reload
button — using inline styles (not Tailwind) to ensure it renders even if CSS fails to load.

## Rationale

1. React requires class components for Error Boundaries (no hook equivalent as of React 19).
2. Inline styles on the fallback UI guarantee visibility regardless of CSS state.
3. Placing it outside `QueryClientProvider` ensures it catches errors from providers too.

## Consequences

- **Positive**: No more blank screens — errors are visible and actionable. Component stack trace
  identifies the exact failing component.
- **Negative**: Class component in a functional-component codebase (minor inconsistency).
