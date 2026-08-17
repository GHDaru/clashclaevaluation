# M3 — Painel do Clã (Nível 1: Visualização)

- **Spec pai**: `specs/001-clash-clan-eval/spec.md` · **Lane**: full · **Date**: 2026-08-16
- **Épico**: Visualização — a interface que o líder usa

## What and why

O painel é a face visível do sistema. O líder abre, vê o status do clã na guerra atual e toma
decisões. A informação deve ser escaneável em segundos: quem está bem, quem está em risco,
quem é candidato a expulsão.

---

## Telas

```
┌─────────────────────────────────┐
│  T1. PAINEL DO CLÃ (principal)  │
│  ┌─────────────────────────────┐│
│  │ Guerra atual: Dia 2 (Sex)   ││
│  │ Clã: 2º lugar | 34500 pts   ││
│  │                             ││
│  │ Jogador      Ataques Cartões││
│  │ 👑 Líder     4/4 ✅  —      ││
│  │ 🟡 JogadorA  2/4    🟡🟡   ││
│  │ 🔴 JogadorB  0/4    🔴 (4🟡)││
│  │ ⚫ JogadorC  0/4    ⚫🔥     ││
│  │ ...                         ││
│  └─────────────────────────────┘│
│                                 │
│  T2. DETALHE DO JOGADOR (modal) │
│  ┌─────────────────────────────┐│
│  │ JogadorC • desde Jan/2025   ││
│  │ ⚫ PRETO — Cand. Expulsão   ││
│  │                             ││
│  │ Guerra Atual: 0 pts • 0/16  ││
│  │ Recência (4sem): 3🔴 1⚫    ││
│  │ Histórico (3m):  [expandir] ││
│  │   Semana 1: 4/4 ✅ 3200pts  ││
│  │   Semana 2: 1/4 🔴 800pts   ││
│  │   Semana 3: 0/4 ⚫ 0pts     ││
│  │   Semana 4: 0/4 ⚫ 0pts     ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

---

## Functional requirements

### F3.1 — Tabela de status do clã (T1)

- **FR3.1.1**: Exibe todos os membros do clã com:
  - Nome e tag
  - Ataques realizados no dia atual (ex: 3/4)
  - Cartões acumulados na guerra (ícones 🟡🔴⚫ com contagem)
  - Pontuação total na guerra
  - Status visual (✅ limpo, 🟡 alerta, 🔴 advertência, ⚫ expulsão)
- **FR3.1.2**: Ordenação default: pior → melhor (pretos primeiro, depois vermelhos, depois
  amarelos, depois limpos).
- **FR3.1.3**: Indicador de guerra: dia atual, posição do clã, se vitória antecipada está
  ativa (🏁 ícone).
- **FR3.1.4**: Atualização manual: botão "Atualizar dados" que re-coleta da API (M1) e
  re-avalia (M2).

### F3.2 — Detalhe do jogador (T2)

- **FR3.2.1**: Ao clicar em um jogador, abre modal/expansão com:
  - Cartões atuais e total acumulado na janela de recência
  - Tabela da guerra atual (dia a dia: ataques, pontos)
  - Histórico resumido da janela de recência (4 semanas)
  - Botão "Expandir histórico" → carrega dados de até 3 meses
- **FR3.2.2**: Indicador de tendência: 📈 melhorando / ➡️ estável / 📉 piorando (baseado nos
  cartões das últimas 3 guerras).

### F3.3 — Destaque de candidatos a expulsão

- **FR3.3.1**: Jogadores ⚫ preto aparecem com destaque visual (fundo vermelho, ícone 🔥).
- **FR3.3.2**: O sistema exibe a justificativa: "4 vermelhos acumulados — 16 ataques
  faltantes na guerra atual" ou "8 vermelhos em 4 semanas".

---

## Edge cases

- **Clã sem guerra ativa**: painel mostra "Sem guerra ativa" + data da última guerra
  avaliada.
- **0 jogadores com cartão**: painel mostra "Todos os jogadores estão em dia ✅".
- **Jogador saiu do clã**: aparece na lista com tag "Inativo" e os dados da última
  participação.
- **Dados ainda não coletados**: primeira execução mostra "Clique em Atualizar para coletar
  dados".

---

## Dependências

| Entrada | De onde vem | O que fornece |
|---|---|---|
| Cartões e status | M2 (Motor) | Status de cada jogador |
| Lista de membros | M1 (API) | Nomes, tags, roles |
| Histórico | M5 (Banco) | Dados de guerras passadas |

| Saída | Para onde vai | O que entrega |
|---|---|---|
| Interface visual | Usuário (líder) | Decisão informada sobre o clã |
