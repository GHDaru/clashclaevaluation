# Research 001 — Clash Royale API e Stack Técnica

- **Spec**: `spec.md` · **Date**: 2026-08-16
- **Questions from**: Technical unknowns in plan.md

---

## R1: Formato exato da resposta `currentriverrace`

**Question**: Quais campos exatos a API `/clans/{tag}/currentriverrace` retorna para
determinar status da guerra, participantes e pontuação?

**Findings** (baseado na documentação oficial developer.clashroyale.com):

A resposta contém:

```json
{
  "state": "active" | "ended",
  "clan": {
    "tag": "#XXXXXXX",
    "name": "Clan Name",
    "participants": [
      {
        "tag": "#PLAYERTAG",
        "name": "Player",
        "fame": 1600,
        "decksUsed": 4,
        "decksUsedToday": 2,
        "boatAttacks": 0,
        "repairPoints": 0
      }
    ],
    "periodPoints": [800, 1200, 600, 400],
    "clanScore": 3000,
    "fame": 0,
    "periodType": "warDay",
    "periodIndex": 2
  },
  "clans": [...]
}
```

**Decision**: Usar `clan.participants[].decksUsedToday` para ataques do dia atual e
`clan.participants[].fame` para pontuação total. `periodIndex` 0-3 mapeia qui-dom.
`clan.clanScore` e posição relativa ao finish line determinam vitória antecipada.

**Sources**: developer.clashroyale.com API docs, comunidade RoyaleAPI.

---

## R2: Rate limits reais da API

**Question**: A API permite 300 req/min. Para 50 jogadores + 1 clan = 51 chamadas por
avaliação. Há risco de rate limit na prática?

**Findings**: 51 chamadas em rajada ocupam ~17% do rate limit. Com espaçamento de 200ms,
51 × 200ms = ~10 segundos. Seguro. Para clãs maiores que 50 ou múltiplos clãs, implementar
token bucket.

**Decision**: Sem preocupação para v1. Espaçar chamadas de battlelog com 200ms. Se a API
retornar 429, retry com backoff exponencial (1s, 2s, 4s).

---

## R3: Stack FastAPI + SQLAlchemy + SQLite

**Question**: FastAPI com SQLAlchemy async + SQLite é suportado?

**Findings**:
- SQLAlchemy 2.0 suporta SQLite com `aiosqlite` para async
- FastAPI + SQLAlchemy é combinação madura, documentação farta
- Alembic gerencia migrations para SQLite sem restrições (exceto ALTER COLUMN, que requer
  batch mode)
- `uv` gerencia dependências e virtualenv, compatível com FastAPI

**Decision**: Usar `aiosqlite` para async SQLite. Configurar Alembic com
`render_as_batch=True` para migrations. Se no futuro migrar para PostgreSQL, trocar
apenas a connection string.

**Sources**: docs.sqlalchemy.org, fastapi.tiangolo.com, alembic.sqlalchemy.org.

---

## R4: Vitória antecipada — como detectar

**Question**: Como o sistema sabe que o clã "garantiu o 1º lugar"?

**Findings**: No River Race, o clã cruza a linha de chegada ao atingir o threshold de fama
do league level. A API retorna `clan.clanScore` e o `periodIndex`. Quando `clan.clanScore`
atinge o valor de finish line + o clã está em 1º lugar entre os `clans[]`, a vitória é
considerada garantida.

**Decision**: Comparar `clan.clanScore` com o maior `clanScore` entre os `clans[]`. Se for
o maior e já cruzou o finish line, ativar relaxamento. Campo exato depende do league level
(Legendary I/II/III têm thresholds diferentes).

**Sources**: community analysis, RoyaleAPI documentation.

---

## R5: React + Vite + TypeScript em 2026

**Question**: Melhor setup para React com pnpm em Agosto/2026?

**Findings**:
- Vite 7 é o bundler padrão (evoluiu do Vite 6)
- React 19 com Server Components está maduro, mas para SPA (single page), React 19 + Vite SPA
  é a escolha certa
- TanStack Query v5 para data fetching (cache, retry, loading states)
- Tailwind CSS v4 ou shadcn/ui para componentes

**Decision**: React 19 + Vite 7 + TypeScript. TanStack Query para chamadas à API backend.
CSS: Tailwind (leve, Steward não definiu preferência de UI). shadcn/ui se quiser componentes
prontos (opcional, decidir no Ciclo 4).

**Sources**: vite.dev, react.dev, tanstack.com/query.
