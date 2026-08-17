# Spec 001 — ClashClanEvaluation (Nível 0: Visão Sistêmica)

- **Status**: Draft · **Lane**: full · **Date**: 2026-08-16
- **Origin**: Steward — necessidade de avaliação objetiva do clã no Clash Royale
- **Appetite**: 2 semanas

## What and why

Líderes de clã no Clash Royale precisam decidir sobre permanência, advertências e expulsões de
membros com base na participação nas Guerras de Clãs (River Race). Hoje essa avaliação é manual,
subjetiva e consome tempo. O sistema automatiza a coleta de dados da API oficial, aplica regras
configuráveis de avaliação e produz um painel com o status de cada jogador — cartões recebidos,
histórico e tendências.

**Jornada servida**: o líder/vice-líder avalia a performance do clã entre ciclos de guerra.

### Regras do domínio (Clash Royale River Race)

- A guerra ocorre de **quinta a domingo** (4 dias de batalha).
- Cada jogador tem **4 ataques por dia** (4 decks diferentes).
- O clã compete contra outros clãs para cruzar a **linha de chegada** primeiro.
- Se o clã garantir o **1º lugar antes do fim** (ex: sábado), as regras internas podem ser
  relaxadas no(s) dia(s) restante(s).
- A API oficial expõe: `/clans/{tag}/currentriverrace` (guerra atual) e
  `/players/{tag}/battlelog` (histórico de batalhas).

## Functional requirements

### M1 — Integração com API Clash Royale

- **FR1.1**: O sistema consulta a API oficial do Clash Royale para obter dados da guerra atual
  do clã (`/clans/{tag}/currentriverrace`).
- **FR1.2**: O sistema consulta o battlelog de cada jogador (`/players/{tag}/battlelog`) para
  obter as batalhas do período da guerra.
- **FR1.3**: A autenticação na API é feita via token de desenvolvedor (API key), configurável
  pelo usuário.

### M2 — Motor de Avaliação (Cartões e Regras)

**Sistema de cartões (configurável, defaults):**

| Evento | Cartão | Quantidade |
|---|---|---|
| 1 ataque faltante (de 4/dia) | 🟡 Amarelo | 1 por ataque |
| 4 amarelos acumulados | 🔴 Vermelho | 1 (conversão) |
| 4 vermelhos acumulados | ⚫ Preto | 1 (conversão → candidato a expulsão) |

**Regras de penalidade por desempenho (configuráveis):**

| Condição | Penalidade |
|---|---|
| 1 dia sem jogar (0/4 ataques) | 4 amarelos = 1 vermelho |
| Guerra abaixo de 1600 pontos | +1 amarelo |
| Guerra abaixo do mínimo do clã | +1 vermelho |

- **FR2.1**: O sistema atribui **1 cartão amarelo por ataque faltante** (total de 4 ataques
  por dia). Um dia sem jogar = 4 amarelos = 1 vermelho.
- **FR2.2**: O threshold de conversão **amarelo → vermelho** é configurável (default: 4).
- **FR2.3**: O threshold de conversão **vermelho → preto** (candidato a expulsão) é
  configurável (default: 4).
- **FR2.4**: O mínimo de pontos por guerra é configurável. Duas faixas:
  - Abaixo de 1600 pontos: **+1 cartão amarelo**.
  - Abaixo do mínimo definido pelo clã: **+1 cartão vermelho**.
- **FR2.5**: Se o clã já garantiu o 1º lugar, as regras são relaxadas nos dias restantes
  (cartões não são emitidos).
- **FR2.6**: A avaliação considera **recência**: janela do último ciclo de guerra (4 semanas)
  para a "corrida dos campeões". Histórico completo de **3 meses** disponível para consulta
  expansível por jogador.

### M3 — Painel do Clã

- **FR3.1**: O painel exibe a lista de membros com status atual: cartões acumulados (amarelos,
  vermelhos, pretos), ataques realizados por dia e pontuação na guerra atual.
- **FR3.2**: O painel exibe o **histórico recente** do jogador (últimas N semanas) com
  tendência (melhorando, estável, piorando).
- **FR3.3**: Jogadores com cartão preto são destacados como "candidatos a expulsão".

### M4 — Gerenciamento de Regras

- **FR4.1**: O usuário pode configurar: mínimo de ataques por dia, mínimo de pontos por guerra,
  thresholds de cartões (amarelo→vermelho, vermelho→preto), janela de recência (semanas).
- **FR4.2**: O usuário pode ativar/desativar o relaxamento de regras por vitória antecipada.

### M5 — Histórico e Banco de Dados

- **FR5.1**: O sistema persiste os dados de cada guerra (participação, cartões, pontuação) para
  consulta histórica.
- **FR5.2**: O sistema permite consultar o histórico de um jogador específico (quais guerras
  participou, cartões recebidos, pontuação) com visão expansível — resumo do último ciclo
  (4 semanas) com opção de expandir para 3 meses.

## Out of scope

- Substituição de membros (kick/convite) dentro do jogo — o sistema apenas **informa** a
  decisão, não a executa.
- Cálculo de fama ou recompensas do clã.
- Comunicação com membros (notificações, mensagens).
- Suporte a múltiplos clãs simultaneamente (v1: um clã por instância).
- Aplicativo mobile nativo (v1: web responsivo).

## Mapa Módulo → Épicos → Features

```
ClashClanEvaluation (Nível 0 — este spec)
│
├── M1: Integração API CR       ← Épico: Coleta de Dados
│   ├── F1.1: Autenticação na API
│   ├── F1.2: Coleta de guerra atual
│   └── F1.3: Coleta de battlelog por jogador
│
├── M2: Motor de Avaliação       ← Épico: Regras de Avaliação
│   ├── F2.1: Atribuição de cartões por ataque
│   ├── F2.2: Conversão amarelo → vermelho → preto
│   ├── F2.3: Cálculo de recência
│   └── F2.4: Relaxamento por vitória antecipada
│
├── M3: Painel do Clã            ← Épico: Visualização
│   ├── F3.1: Tabela de status do clã
│   ├── F3.2: Detalhe do jogador com histórico
│   └── F3.3: Destaque de candidatos a expulsão
│
├── M4: Gerenciamento de Regras  ← Épico: Configuração
│   ├── F4.1: Tela de parâmetros
│   └── F4.2: Persistência de configuração
│
└── M5: Histórico e Banco        ← Épico: Persistência
    ├── F5.1: Armazenamento de dados de guerra
    └── F5.2: API de consulta histórica
```

Os épicos serão detalhados nos níveis 1 e 2 do ciclo de especificação.

## Acceptance criteria (DoD)

- WHEN a guerra está ativa (quinta a domingo) THE SYSTEM SHALL exibir o status de ataques de
  cada membro.
- WHEN um jogador não realiza o mínimo de ataques em um dia THE SYSTEM SHALL atribuir um cartão
  amarelo.
- WHEN um jogador acumula o threshold configurado de cartões amarelos THE SYSTEM SHALL
  converter em um cartão vermelho.
- WHEN um jogador acumula o threshold configurado de cartões vermelhos THE SYSTEM SHALL
  marcar o jogador como candidato a expulsão (cartão preto).
- WHEN o clã garante o 1º lugar antes do fim da guerra THE SYSTEM SHALL suspender a emissão de
  cartões nos dias restantes.
- WHEN o usuário consulta o painel THE SYSTEM SHALL exibir tendência do jogador baseada na
  janela de recência configurada.
- `scripts/check-conformance.sh` → exit 0 para validação dos artefatos do ciclo.

## Clarify

Todas as questões do Nível 0 foram resolvidas na Rodada 1:

1. [Cartão por ataque]: ✅ **1 amarelo por ataque faltante** (não por dia). 4 amarelos = 1
   vermelho. 4 vermelhos = 1 preto (expulsão).
2. [Pontuação mínima]: ✅ **Por guerra** (semanal). Duas faixas: < 1600 = +1 amarelo, <
   mínimo do clã = +1 vermelho.
3. [Relaxamento]: ✅ Confirmado — API `currentriverrace.status` indica se o clã cruzou a
   linha de chegada em 1º.
4. [Recência]: ✅ Janela do último ciclo (4 semanas) + histórico de 3 meses expansível.
