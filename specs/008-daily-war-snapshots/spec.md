# Spec 008 — Coleta Diária de Snapshots de Guerra

- **Status**: Draft · **Lane**: full · **Date**: 2026-08-17
- **Origin**: Steward request — necessidade de saber ataques por dia por jogador; a API do Clash Royale retorna apenas valores cumulativos, sem breakdown diário.

## What and why

O sistema avalia jogadores do clã com base em cartões (amarelo/vermelho/preto) que dependem de quantos ataques cada jogador fez em cada dia de guerra (quinta a domingo). Hoje o sistema só consegue ver o total cumulativo de ataques (decksUsed) no momento da consulta — não consegue dizer quantos ataques foram feitos na quinta vs. sexta vs. sábado. Sem o breakdown diário, a avaliação usa uma heurística aproximada que pode marcar injustamente um jogador que atacou todos os dias mas com distribuição irregular.

A API do Clash Royale não fornece o histórico de ataques por dia. A única forma de obter essa informação é capturar um snapshot dos dados cumulativos a cada dia de guerra e, depois, calcular a diferença entre snapshots consecutivos: o número de ataques no dia X = decksUsed_no_snapshot_do_dia_X − decksUsed_no_snapshot_do_dia_(X−1).

Isso serve a jornada do líder/co-líder que precisa identificar jogadores que não estão atacando em dias específicos — informação que hoje está invisível. A coleta deve ser automática (cron), mas também deve poder ser disparada manualmente para recuperação de dados faltantes (backfill).

## Functional requirements

- **FR1**: O sistema deve capturar um snapshot diário dos dados de guerra de todos os participantes do clã durante os dias de guerra (quinta a domingo), registrando para cada jogador: tag, nome, data do snapshot, decksUsed cumulativo, decksUsedToday, troféus (fame cumulativo), e o identificador da guerra.

- **FR2**: A coleta do mesmo dia executada múltiplas vezes não deve criar registros duplicados — o sistema deve atualizar (upsert) o snapshot existente para a mesma combinação de guerra + jogador + data.

- **FR3**: O sistema deve registrar cada execução da coleta em um log de auditoria (snapshot run), com status de resultado (sucesso, falha, sem guerra ativa) e timestamp, de forma que seja possível detectar dias em que a coleta não ocorreu.

- **FR4**: O sistema deve calcular o número de ataques por dia de cada jogador a partir da diferença de decksUsed cumulativo entre snapshots consecutivos da mesma guerra.

- **FR5**: O sistema deve permitir disparar a coleta manualmente para uma data específica (backfill), com o mesmo comportamento idempotente da coleta automática.

- **FR6**: O sistema deve detectar e reportar quais dias de guerra estão faltando snapshots (completeness check), listando as datas esperadas que não têm snapshot coletado.

- **FR7**: A avaliação do clã deve usar os ataques por dia reais (calculados a partir de snapshots) quando os snapshots existirem para a guerra atual, e deve usar a heurística atual como fallback quando os snapshots não existirem.

- **FR8**: O sistema deve tentar novamente a coleta automaticamente quando a API do Clash Royale estiver indisponível, com um número limitado de tentativas e intervalo entre elas.

## Out of scope

- Coleta de snapshots de guerras passadas anteriores à implementação (não há dados históricos disponíveis na API para reconstruir).
- Coleta fora dos dias de guerra (segunda a quarta) — não há dados de guerra ativa nesses dias.
- Interface de usuário para visualizar o breakdown de ataques por dia (será tratada em ciclo separado).
- Alertas ou notificações proativas sobre snapshots faltantes (apenas detecção via endpoint).
- Configuração do agendamento cron no sistema operacional (o script é standalone; o agendamento é responsabilidade de ops).

## Acceptance criteria (DoD)

- WHEN a coleta é executada em um dia de guerra ativa THEN THE SYSTEM SHALL registrar um snapshot para cada participante presente na resposta da API, com decksUsed e troféus (fame cumulativo) do momento da coleta.
- WHEN a coleta é executada duas vezes para a mesma guerra, jogador e data THEN THE SYSTEM SHALL resultar em exatamente um registro de snapshot para essa combinação, com os valores da execução mais recente.
- WHEN a coleta é executada e a API retorna estado "ended" ou "notInWar" THEN THE SYSTEM SHALL registrar um snapshot run com status "no_war" e não criar snapshots de jogador.
- WHEN a API está indisponível e todas as tentativas falham THEN THE SYSTEM SHALL registrar um snapshot run com status "failure" e um snapshot run com status "success" não deve existir para essa execução.
- WHEN existem snapshots para os dias 1, 2 e 3 de uma guerra THEN THE SYSTEM SHALL calcular ataques_do_dia_2 = decksUsed_snapshot_dia_2 − decksUsed_snapshot_dia_1 para cada jogador.
- WHEN o endpoint de completeness check é chamado para uma guerra com 4 dias esperados e apenas 2 dias têm snapshots THEN THE SYSTEM SHALL retornar uma lista contendo exatamente as 2 datas faltantes.
- WHEN a avaliação do clã é executada e existem snapshots completos para a guerra atual THEN THE SYSTEM SHALL usar os ataques por dia calculados a partir dos snapshots, não a heurística.
- WHEN a avaliação do clã é executada e não existem snapshots para a guerra atual THEN THE SYSTEM SHALL usar a heurística atual de fallback sem erro.
- `python scripts/snapshot_war.py --date 2026-08-14 --clan-tag "#QPUJC0CG"` executado duas vezes → a tabela de snapshots contém exatamente uma linha por participante para essa data (idempotência).
- `grep -r "derive_per_day_attacks" backend/` → resultado não-vazio (a função de cálculo existe e é chamada).

## Clarify

1. A coleta deve rodar em horário fixo (05:30 UTC) ou há tolerância configurável? → Horário fixo 05:30 UTC após o reset diário da guerra (~05:00 UTC), sem tolerância configurável neste ciclo. O backfill manual cobre atrasos.

<!--
  GATE (DoR — not delegable): this spec only becomes a plan after human approval.
  Handoff: spec-agent → (approval) → plan-architect.
-->
