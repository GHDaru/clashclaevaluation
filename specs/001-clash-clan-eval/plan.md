# Plan 001 — ClashClanEvaluation

- **Spec**: `spec.md` · **Lane**: full · **Date**: 2026-08-16
- **Appetite**: 2 semanas · **Ciclo**: Implementação Completa

## Constitution Check (governance/principles.md)

| Principle | Compliance |
|---|---|
| I. Spec-driven | ✅ Spec 001 aprovado com 5 módulos, 17 features, critérios EARS. Toda decisão de código deriva deste spec. |
| II. Human-governed orchestration | ✅ O Steward (humano) aprova specs, planos e o merge gate. Cartão preto = recomendação, nunca ação automática (expulsão é decisão humana). |
| III. Reversibility / risk gates | ✅ Criação de features em branch (reversível). Configuração com restore defaults. Migrations com rollback. API key armazenada fora do repo. O sistema nunca executa kick/expulsão — apenas informa. |
| IV. Test-first / verifiable DoD | ✅ Cada FR tem critério EARS testável. Verificação: testes unitários no motor (M2), testes de integração na API (M1→M5), testes de componente no painel (M3). |
| V. Context economy / boundary | ✅ 5 módulos cortados por bounded context (API, Motor, Painel, Config, Banco). Paralelismo seguro: M1+M4 podem evoluir independentes de M3. Cada agente recebe apenas seu contexto. |
| VI. Living artifacts | ✅ spec.md, plan.md, data-model.md, contracts/, ux-design.md no mesmo diretório do ciclo. ADR será gerado para decisões arquiteturais. Changelog atualizado no PR. |
| VII. Light governance / YAGNI | ✅ v1: single-clan, single-user, SQLite, sem notificações, sem mobile nativo. Stack definida (uv, pnpm, React, FastAPI) — nada além. |
| VIII. Intelligible communication | ✅ Todas as siglas expandidas na primeira ocorrência: Definition of Done (DoD), Application Programming Interface (API), Architecture Decision Record (ADR), Domain-Driven Design (DDD). Glossário mantido em `docs/governance/glossary.md`. |

**No violations.**

---

## Artifacts of this cycle (declare all five — silence is not a decision)

| Artifact | Declaration | Why |
|---|---|---|
| `research.md` | `ART:research=yes` | A API do Clash Royale tem comportamentos não documentados (formato exato de `currentriverrace.status`, `periodIndex`, rate limits). Precisamos de confirmação antes de codificar. |
| `data-model.md` | `ART:data-model=yes` | Ciclo de código com 5 entidades (Clan, War, Player, PlayerWar, EvaluationLog) e seus relacionamentos. |
| `contracts/` | `ART:contracts=yes` | Backend Python expõe API REST consumida pelo frontend React. Contratos definem as interfaces entre M1↔M2↔M5↔M3. |
| `checklist.md` | `ART:checklist=no` | O DoD do operating model cobre este ciclo. Checklist adicional seria duplicação (Principle VI). |
| `ux-design.md` | `ART:ux-design=yes` | M3 (Painel do Clã) e M4 (Tela de Configuração) tocam telas. Papel semântico antes do componente (Principle VII do método). |

---

## How

### Arquitetura

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React + pnpm)               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Dashboard    │  │  PlayerCard  │  │  ConfigPanel  │  │
│  │  (M3: T1)    │  │  (M3: T2)    │  │  (M4)         │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                 │                   │          │
│         └─────────┬───────┴───────────────────┘          │
│                   │ HTTP REST                            │
└───────────────────┼──────────────────────────────────────┘
                    │
┌───────────────────┼──────────────────────────────────────┐
│                   │  Backend (Python/FastAPI + uv)        │
│  ┌────────────────┴──────────────────────────────────┐   │
│  │              API Router                            │   │
│  │  GET /clan/status    POST /evaluate                │   │
│  │  GET /players/{tag}  PUT /config                   │   │
│  │  GET /wars/{id}      GET /config                   │   │
│  └──┬────────┬─────────┬──────────┬──────────────────┘   │
│     │        │         │          │                       │
│  ┌──▼──┐ ┌──▼───┐ ┌───▼───┐ ┌───▼──────┐                │
│  │ M1  │ │ M2   │ │ M4    │ │ M5       │                │
│  │ API │ │Motor │ │Config │ │Hist/Banco│                │
│  │Client│ │      │ │       │ │          │                │
│  └──┬──┘ └──────┘ └───────┘ └──┬───────┘                │
│     │                          │                         │
└─────┼──────────────────────────┼─────────────────────────┘
      │                          │
      ▼                          ▼
┌──────────┐            ┌──────────────┐
│ Clash    │            │   SQLite /   │
│ Royale   │            │  PostgreSQL  │
│ API      │            │              │
└──────────┘            └──────────────┘
```

### Bounded contexts (corte para paralelismo seguro)

| Contexto | Módulos | Pode evoluir independente de |
|---|---|---|
| **Coleta** | M1 | M2, M3, M4 |
| **Avaliação** | M2 | M3 (desde que contrato mantido) |
| **Apresentação** | M3 | M1, M2, M5 (consome API, não acopla) |
| **Configuração** | M4 | M1, M2, M3 |
| **Persistência** | M5 | M3 (desde que schema mantido) |

### Stack tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Steward definiu; FastAPI traz OpenAPI auto, type safety, async |
| ORM | SQLAlchemy 2.0 + Alembic | Migration suportada, maduro, async |
| Banco v1 | SQLite | Single-user, zero-infra. Migrar para PostgreSQL se multi-usuário |
| Frontend | React 19 + TypeScript + Vite | Steward definiu pnpm; Vite é padrão 2026 |
| HTTP Client | httpx (Python) | Async, suporte a retry, timeouts |
| Gerenciador | uv (Python), pnpm (Frontend) | Steward definiu |
| Testes | pytest + pytest-httpx (back), Vitest (front) | Padrão para cada ecossistema |

### Roadmap de ciclos

```
Ciclo 1 (este):     Planejamento e Constituição  ← ESTAMOS AQUI
                    └─→ spec.md, plan.md, data-model.md,
                        contracts/, ux-design.md, research.md,
                        constitution, ADR 001

Ciclo 2:            Preparação do Ambiente
                    └─→ scaffold do projeto (uv init, pnpm create),
                        CI/CD, migrations iniciais, configuração
                        da API key, Docker/compose se necessário

Ciclo 3:            Desenvolvimento — Núcleo (M1 + M2 + M5)
                    └─→ API client, motor de avaliação com testes,
                        banco e migrações, endpoints de avaliação

Ciclo 4:            Desenvolvimento — Interface (M3 + M4)
                    └─→ Painel React, tela de configuração,
                        integração com API backend, testes E2E

Ciclo 5:            Integração, Testes e Entrega
                    └─→ QA, review independente, documentação,
                        jornada, merge gate
```

### Decisões arquiteturais (ADR)

Este plano gera as seguintes Architecture Decision Records (ADRs):

| ADR | Decisão | Racional |
|---|---|---|
| ADR 001 | FastAPI + SQLAlchemy + SQLite como stack backend | Steward definiu Python. FastAPI é async, gera OpenAPI, type-safe. SQLite para v1 single-user. |
| ADR 002 | Motor de Avaliação como módulo puro (sem I/O) | M2 recebe dados normalizados, não chama API nem banco. Testável com fixtures. |
| ADR 003 | Contratos REST entre frontend e backend | Separação clara. Frontend nunca chama API do Clash Royale diretamente. |
| ADR 004 | Avaliação pós-guerra (não em tempo real) | O sistema avalia após o término da guerra (domingo), não durante. Simplifica o modelo. |

---

## Verification (DoD)

- `pytest specs/001-clash-clan-eval/` → todos os testes do plano passam
- `scripts/check-conformance.sh` → exit 0 (artefatos declarados existem)
- `scripts/check-agents.sh` → agents com tool lists corretas
- `uv run alembic upgrade head` → migrations aplicam sem erro
- `uv run fastapi dev` → servidor sobe e responde em `/docs` (OpenAPI)
- `pnpm run dev` → frontend sobe e renderiza o painel
- `pnpm run build` → build de produção sem erros
- `pnpm run lint` → lint limpo
- `uv run pytest` → todos os testes verdes
- `pnpm run test` → todos os testes do frontend verdes

<!--
  GATE (not delegable): the plan is approved by a human before it becomes tasks.
  Handoff: plan-architect → (approval) → tasks → dev-implementer.
-->
