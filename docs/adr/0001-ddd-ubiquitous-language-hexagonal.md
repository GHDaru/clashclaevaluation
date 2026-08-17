# ADR 001 — Emenda Constitucional: DDD, Linguagem Ubíqua e Arquitetura Hexagonal

- **Status**: Accepted · **Date**: 2026-08-16
- **Decision**: Adicionar Princípios IX (Ubiquitous Language), X (Domain-Driven Design tático)
  e XI (Hexagonal Architecture / Ports & Adapters) à constituição do projeto
  ClashClanEvaluation.
- **Supersedes**: —
- **Superseded by**: —

## Context

O projeto ClashClanEvaluation opera em um domínio rico (avaliação de clã, regras de cartões,
recência, penalidades) que se beneficia de modelagem de domínio profunda. A arquitetura
hexagonal (Ports & Adapters) garante que o núcleo de domínio seja testável e independente de
infraestrutura. A Linguagem Ubíqua (Ubiquitous Language) de Domain-Driven Design (DDD) garante
que o código e a conversa usem os mesmos termos — eliminando a tradução entre negócio e
implementação que é fonte de bugs.

Os princípios I–VIII da constituição Maestro cobrem o método de trabalho (spec-driven,
human-governed, test-first, YAGNI), mas não cobrem princípios de design de código e modelagem
de domínio. O Steward determinou que DDD completo e arquitetura hexagonal são non-negotiable
para este projeto.

## Decision

Adicionar três novos princípios à constituição (`docs/governance/principles.md`), bump de
versão 1.3.0 → 1.4.0 (MINOR: novos princípios).

### IX. Ubiquitous Language (a linguagem do domínio é o código)

Todo termo de domínio usado na conversa entre Steward e agentes DEVE aparecer literalmente no
código — nomes de classes, métodos, variáveis e tabelas. A linguagem do negócio e a linguagem
do código são a mesma. Um termo novo entra primeiro no glossário (`docs/governance/glossary.md`)
e só então aparece no código.

**Termos canônicos do domínio ClashClanEvaluation** (glossário inicial):

| Termo | Definição | Não confundir com |
|---|---|---|
| **Cartão Amarelo** (YellowCard) | Penalidade por 1 ataque faltante | Não é "warning" genérico |
| **Cartão Vermelho** (RedCard) | Conversão de 4 YellowCards | Não é "error" ou "danger" |
| **Cartão Preto** (BlackCard) | Conversão de 4 RedCards — candidato a expulsão | Não é "critical" ou "ban" |
| **Guerra** (War) | Ciclo de batalha de quinta a domingo | Não é "battle" ou "match" |
| **Ataque** (Attack) | Uma batalha de guerra (1 de 4 decks por dia) | Não é "battle" genérico |
| **Dia de Guerra** (WarDay) | Um dos 4 dias (Thursday–Sunday) | Não é "round" ou "period" |
| **Corrida dos Campeões** (ChampionRace) | Janela de recência de 4 semanas | Não é "season" |
| **Vitória Antecipada** (EarlyVictory) | Clã cruzou a finish line em 1º antes do fim | Não é "early finish" |
| **Relaxamento** (Relaxation) | Suspensão de cartões após EarlyVictory | Não é "forgiveness" ou "waiver" |
| **Avaliação** (Evaluation) | Processo de atribuir cartões pós-guerra | Não é "scoring" ou "grading" |

Este glossário de domínio vive em `docs/governance/glossary.md` junto com o glossário de
método. Termos de domínio são prefixados com `[DOMAIN]` para distingui-los dos termos de
método.

### X. Domain-Driven Design tático (o domínio modela o código)

O código segue os padrões táticos de DDD:

- **Entity**: objeto com identidade contínua (ex: `Player` identificado por `tag`)
- **Value Object**: objeto definido por seus atributos, imutável (ex: `WarDay`, `CardCount`)
- **Aggregate**: cluster de entities e value objects com uma raiz que garante consistência
  (ex: `PlayerWar` é raiz do aggregate de participação)
- **Domain Service**: operação que não pertence a uma entity específica (ex:
  `CardConversionService` que converte amarelos em vermelhos)
- **Repository**: abstração de persistência por aggregate (ex: `PlayerWarRepository`)
- **Domain Event**: algo que aconteceu no domínio (ex: `BlackCardIssued`, `EarlyVictoryDetected`)

O domínio NUNCA depende de infraestrutura. A seta de dependência sempre aponta para dentro.

### XI. Arquitetura Hexagonal (Ports & Adapters)

O sistema é organizado em camadas concêntricas:

```
[Infra] → [Application] → [Domain] ← [Application] ← [Infra]
  │            │             │            │            │
  │   ┌────────┴─────────┐   │   ┌────────┴─────────┐   │
  │   │  Primary Ports    │  │   │ Secondary Ports   │   │
  │   │  (entrada)        │  │   │  (saída)          │   │
  │   └────────┬─────────┘   │   └────────┬─────────┘   │
  │            │             │            │             │
  ▼            ▼             │            ▼             ▼
HTTP REST   CLI command       │      DB Repository   CR API Client
(Primary                     │      (Secondary       (Secondary
 Adapter)                    │       Adapter)         Adapter)
```

**Regras**:
- **Domain** (`domain/`): entities, value objects, aggregates, domain services, domain
  events. ZERO dependências externas. Testável com fixtures puras.
- **Application** (`application/`): casos de uso (ports de entrada). Orquestra domain +
  ports de saída. Depende só do domain.
- **Infrastructure** (`infrastructure/`): adaptadores concretos. FastAPI routers,
  SQLAlchemy repositories, CR API HTTP client. Depende de domain + application.
- **Primary ports** (entrada): interfaces que o mundo externo chama (REST endpoints, CLI)
- **Secondary ports** (saída): interfaces que o domínio precisa (repositories, external
  API clients) — definidas no domain/application, implementadas no infrastructure

## Consequences

- Todo código será organizado em `domain/`, `application/`, `infrastructure/`
- O glossário de domínio será mantido junto com o de método em `docs/governance/glossary.md`
- Termos de domínio prefixados `[DOMAIN]` no glossário
- O plano técnico (`plan.md`) já prevê bounded contexts compatíveis com esta arquitetura
- A stack (FastAPI, SQLAlchemy, React) permanece; a organização interna segue Ports & Adapters
