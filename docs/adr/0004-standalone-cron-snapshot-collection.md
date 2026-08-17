# ADR 004 — Coleta de Snapshots via Script Standalone (cron), não Background Task FastAPI

- **Status**: Accepted · **Date**: 2026-08-17
- **Decision**: A coleta diária de snapshots de guerra é um script Python standalone
  (`scripts/snapshot_war.py`) agendado por cron externo (`30 5 * * 4-7`), não uma FastAPI
  background task / worker interno.
- **Supersedes**: —
- **Superseded by**: —

## Context

A Spec 008 exige captura diária de snapshots durante os dias de guerra (quinta a domingo) às
05:30 UTC, com retentativa em falha de API e gatilho manual para backfill. O backend já roda
FastAPI, o que torna tentadora uma `BackgroundTasks` ou um worker async interno.

O processo de coleta é **batch e agendado**, não **request-scoped**: ele lê da API do Clash
Royale (Clash Royale API), faz upsert de N linhas e loga uma execução de auditoria. Misturar
esse ciclo de vida com o do servidor web acopla a disponibilidade da coleta à do servidor,
dificulta o backfill via linha de comando e quebra a simetria entre o gatilho automático (cron)
e o manual (CLI/endpoint).

## Decision

A coleta é uma **caso de uso de aplicação** (`CollectSnapshotsUseCase`) invocada por dois
adaptadores primários que compartilham a mesma orquestração:

1. **CLI standalone** — `scripts/snapshot_war.py` (agendado por cron externo; retentativa
   própria com número limitado de tentativas e intervalo exponencial).
2. **Endpoint HTTP** — `POST /api/v1/snapshots/collect` (gatilho manual / backfill com
   parâmetro de data opcional).

O agendamento (cron expression `30 5 * * 4-7`) é **responsabilidade de ops**, não da aplicação
— o script é idempotente e tolerante a execuções repetidas, então o cron é o único mecanismo
de tempo. Isso mantém a aplicação stateless quanto a agendamento (Principle VII — YAGNI: não
importamos um scheduler interno enquanto o cron do SO resolve).

### Resolução do `war_id`

Snapshots têm FK para `wars.id`. O caso de uso resolve o `war_id` buscando a `War` da semana
corrente via `WarRepository.get_by_clan_and_date(clan_tag, war_start_date)`; se não existir,
cria uma `War` mínima (stub) para que os snapshots tenham onde ancorar. A `War` completa é
enriquecida posteriormente por `EvaluateClanUseCase`. Isso evita ordenação temporal rígida
entre coleta e avaliação.

## Consequences

- **+** Coleta sobrevive a restart do servidor web; backfill via CLI é trivial.
- **+** Simetria: cron e endpoint chamam o mesmo caso de uso — um só caminho testável.
- **+** O domínio permanece puro: `derive_per_day_attacks` e os aggregates não dependem de
  infraestrutura (Principle XI).
- **−** Ops deve configurar o cron (documentado no README do script; fora do scope da spec).
- **−** Retentativa vive em dois lugares (CLI e, indiretamente, o cliente HTTP que já retenta
  429). Aceitável: a retentativa do CLI cobre indisponibilidade total da API; a do cliente
  cobre rate limiting por requisição.

## Alternatives considered

- **FastAPI `BackgroundTasks`**: rejeitada — acopla coleta ao ciclo de vida do servidor e não
  oferece gatilho CLI simétrico sem duplicar lógica.
- **Scheduler interno (APScheduler / Celery)**: rejeitada por YAGNI — introduz dependência e
  estado de scheduler para um job que roda 4×/semana.
