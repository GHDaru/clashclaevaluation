# M1 — Integração com API Clash Royale (Nível 1: Coleta de Dados)

- **Spec pai**: `specs/001-clash-clan-eval/spec.md` · **Lane**: full · **Date**: 2026-08-16
- **Épico**: Coleta de Dados — a porta de entrada do sistema

## What and why

O sistema depende de dados oficiais do Clash Royale. Este módulo é responsável por autenticar,
coletar e normalizar os dados da API oficial, entregando-os limpos para o Motor de Avaliação
(M2) e para o Banco (M5). É a única porta de entrada de dados externos.

---

## Endpoints da API utilizados

| Endpoint | Dados obtidos | Usado por |
|---|---|---|
| `GET /clans/{clanTag}` | Lista de membros do clã (tag, nome, role, trophies) | M1 → M2, M3 |
| `GET /clans/{clanTag}/currentriverrace` | Guerra atual: status do clã, períodos, participantes, pontuações | M1 → M2 (F2.4, F2.5) |
| `GET /players/{playerTag}/battlelog` | Últimas batalhas do jogador (até 25) | M1 → M2 (F2.1) |

**Autenticação**: API Key via header `Authorization: Bearer {token}`. Token gerado em
developer.clashroyale.com.

**Rate limit**: A API oficial tem limite de ~300 requisições/minuto. Para um clã de 50
jogadores, coletar todos os battlelogs = ~51 chamadas (1 clan + 50 players). Cabe folgado.

---

## Functional requirements

### F1.1 — Autenticação na API

- **FR1.1.1**: O usuário fornece o token da API (API Key) via configuração (M4).
- **FR1.1.2**: O token é armazenado de forma segura (variável de ambiente ou arquivo de
  configuração fora do repositório).
- **FR1.1.3**: O sistema testa a validade do token ao iniciar (chamada leve: `GET /clans/{tag}`
  e verifica HTTP 200).

### F1.2 — Coleta de dados da guerra atual

- **FR1.2.1**: `GET /clans/{clanTag}/currentriverrace` retorna:
  - `state` (active/inactive), `clan.participants[]` com `tag`, `fame`, `decksUsed`,
    `periodPoints[]`
  - `clan.periodPoints` (pontuação diária), `periodIndex` (dia atual: 0=qui, 1=sex, 2=sáb,
    3=dom)
  - `clan.status` (posição: `finished` + colocação)
- **FR1.2.2**: O sistema extrai e normaliza: tag do jogador, fama/pontos, decks usados por
  dia, se o clã terminou e em qual posição.
- **FR1.2.3**: Se `state = null` ou erro 404 (sem guerra ativa), o sistema informa "sem
  guerra ativa" e não avalia.

### F1.3 — Coleta de battlelog por jogador

- **FR1.3.1**: Para cada jogador do clã, `GET /players/{playerTag}/battlelog`.
- **FR1.3.2**: Filtra batalhas pelo `type` de guerra (river race) e pela data dos dias de
  guerra (quinta a domingo). Campos relevantes: `battleDate`, `type`, `gameMode`,
  `team[0].trophyChange`.
- **FR1.3.3**: Agrega por dia: contagem de batalhas de guerra por jogador → quantos ataques
  fez dos 4 possíveis.
- **FR1.3.4**: A coleta é **cacheada**: em uma sessão de avaliação, cada battlelog é buscado
  uma vez. Dados persistem no banco (M5) para consultas futuras sem nova chamada à API.

---

## Edge cases

- **API offline / timeout**: retry 3x com backoff exponencial (1s, 2s, 4s). Se falhar,
  reporta "dados indisponíveis" e mantém último estado persistido.
- **Token inválido/expirado**: erro claro "Token inválido. Gere um novo em
  developer.clashroyale.com".
- **Jogador saiu do clã**: battlelog ainda retorna dados históricos. O sistema marca o
  jogador como "inativo" e coleta o que foi possível.
- **Clã cheio (50 membros)**: 51 chamadas é seguro dentro do rate limit. Se necessário,
  espaçar chamadas com delay de 200ms.
- **Battlelog sem batalhas de guerra**: jogador pode não ter jogado guerra nenhuma → 0
  ataques em todos os dias, tratado normalmente pelo M2.

---

## Dependências

| Entrada | De onde vem | O que fornece |
|---|---|---|
| Clan tag | M4 (Configuração) | Identificador do clã (#XXXXXXX) |
| API key | M4 (Configuração) | Token de autenticação |

| Saída | Para onde vai | O que entrega |
|---|---|---|
| Lista de membros | M2, M3 | Nome, tag, role de cada jogador |
| Dados da guerra atual | M2, M5 | status, periodPoints, participants |
| Ataques por jogador/dia | M2 | Contagem de batalhas de guerra por dia |
