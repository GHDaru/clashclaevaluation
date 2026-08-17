# M2 — Motor de Avaliação (Nível 1: Regras de Cartões e Pontuação)

- **Spec pai**: `specs/001-clash-clan-eval/spec.md` · **Lane**: full · **Date**: 2026-08-16
- **Épico**: Regras de Avaliação — o núcleo do sistema

## What and why

O Motor de Avaliação é o coração do sistema. Ele recebe os dados brutos da API (M1), aplica as
regras configuráveis de cartões e pontuação (M4), e produz o resultado que o painel (M3) exibe.
Toda a lógica de negócio do domínio vive aqui.

---

## Fluxo de avaliação (por guerra, por jogador)

```
Dados da API (ataques, pontos, status do clã)
  │
  ├─→ [Regra 1] Contagem de ataques faltantes por dia
  │     └─→ 1 ataque faltante = 1 🟡 amarelo
  │
  ├─→ [Regra 2] Conversão de cartões acumulados
  │     ├─→ 4 🟡 amarelos = 1 🔴 vermelho  (threshold configurável)
  │     └─→ 4 🔴 vermelhos = 1 ⚫ preto    (threshold configurável)
  │
  ├─→ [Regra 3] Penalidades por pontuação
  │     ├─→ Guerra < 1600 pontos = +1 🟡 amarelo  (faixa de alerta)
  │     └─→ Guerra < mínimo do clã = +1 🔴 vermelho (faixa crítica)
  │
  ├─→ [Regra 4] Relaxamento por vitória antecipada
  │     └─→ Se clã cruzou linha de chegada em 1º → ignora cartões
  │         dos dias restantes
  │
  └─→ [Regra 5] Recência ("corrida dos campeões")
        └─→ Cartões nas últimas 4 semanas têm peso máximo
            Cartões entre 4-12 semanas têm peso reduzido (histórico)
```

---

## Functional requirements

### F2.1 — Contagem de ataques faltantes

- **FR2.1.1**: Para cada dia de guerra (quinta, sexta, sábado, domingo), o sistema conta
  quantos ataques o jogador realizou (fonte: `battlelog` filtrado por data e `type` de batalha
  de guerra).
- **FR2.1.2**: Cada ataque abaixo de 4 gera **1 cartão amarelo por ataque faltante**.
  Exemplos:
  - 4/4 ataques = 0 cartões
  - 2/4 ataques = 2 amarelos
  - 0/4 ataques = 4 amarelos (que viram 1 vermelho pela regra F2.2)
- **FR2.1.3**: O total de ataques por dia (4) é configurável.

### F2.2 — Conversão de cartões

- **FR2.2.1**: O sistema contabiliza cartões acumulados do jogador e aplica conversão:
  - Threshold **amarelo → vermelho**: default 4, configurável.
  - Threshold **vermelho → preto**: default 4, configurável.
- **FR2.2.2**: A conversão é aplicada **após** a contagem de todos os cartões da guerra atual,
  não incrementalmente.
- **FR2.2.3**: Cartão preto = "candidato a expulsão". O sistema apenas **marca**; a decisão
  final é humana (Principle II do Maestro).

### F2.3 — Penalidades por pontuação

- **FR2.3.1**: Duas faixas de pontuação mínima, ambas configuráveis:
  - **Faixa de alerta** (default: 1600 pontos): abaixo → +1 🟡 amarelo.
  - **Faixa crítica** (mínimo do clã): abaixo → +1 🔴 vermelho.
- **FR2.3.2**: A pontuação é total da guerra (soma dos pontos dos 4 dias), por jogador.
- **FR2.3.3**: Se um jogador não jogou nenhum dia (0 pontos), ele já recebeu 16 amarelos
  (4 dias × 4 ataques) = 4 vermelhos; a penalidade de pontuação é **adicional**.

### F2.4 — Relaxamento por vitória antecipada

- **FR2.4.1**: O sistema verifica se o clã **cruzou a linha de chegada em 1º lugar** antes do
  fim da guerra (fonte: `currentriverrace.clan.status` ou campo equivalente da API).
- **FR2.4.2**: Se a condição for verdadeira, os **dias restantes** não geram cartões (nem por
  ataque faltante, nem por pontuação).
- **FR2.4.3**: Cartões já emitidos em dias anteriores à vitória **não** são removidos.
- **FR2.4.4**: O relaxamento é **ativável/desativável** via configuração (M4).

### F2.5 — Recência e janela de avaliação

- **FR2.5.1**: A "corrida dos campeões" considera os cartões das **últimas 4 semanas**
  (último ciclo completo de guerra) com peso máximo.
- **FR2.5.2**: Cartões entre a 5ª e a 12ª semana (histórico de 3 meses) têm peso informativo
  (exibidos, mas não contam para o status de expulsão).
- **FR2.5.3**: A janela de recência (4 semanas) é configurável.

---

## Cenários de exemplo

### Cenário A: Jogador faltoso total

```
Semana X:
  Qui: 0/4 ataques → 4 amarelos = 1 vermelho
  Sex: 0/4 ataques → 4 amarelos = 1 vermelho
  Sáb: 0/4 ataques → 4 amarelos = 1 vermelho
  Dom: 0/4 ataques → 4 amarelos = 1 vermelho
  Pontuação: 0 (< 1600 → +1 amarelo, < mínimo → +1 vermelho)

Total bruto: 16 amarelos, 1 vermelho (pontuação)
Conversão:   16 ÷ 4 = 4 vermelhos + 1 vermelho (pontuação) = 5 vermelhos
             5 ÷ 4 = 1 preto + 1 vermelho restante
Resultado:   ⚫ PRETO — candidato a expulsão
```

### Cenário B: Jogador mediano com alerta

```
Semana X:
  Qui: 4/4 ✅    Sex: 3/4 (1 amarelo)    Sáb: 4/4 ✅    Dom: 2/4 (2 amarelos)
  Pontuação: 1500 (< 1600 → +1 amarelo, ≥ mínimo do clã)

Total bruto: 3 amarelos (ataques) + 1 amarelo (pontuação) = 4 amarelos
Conversão:   4 ÷ 4 = 1 vermelho
Resultado:   🔴 VERMELHO — advertência
```

### Cenário C: Vitória antecipada no sábado

```
Semana X:
  Qui: 4/4 ✅    Sex: 4/4 ✅
  Sáb: clã cruza linha de chegada em 1º lugar
  Sáb: 4/4 ✅ (já jogou antes da vitória)
  Dom: 0/4 — mas vitória antecipada → cartões NÃO emitidos

Total: 0 cartões (relaxamento ativo)
Resultado: ✅ LIMPO
```

---

## Dependências

| Entrada | De onde vem | O que fornece |
|---|---|---|
| Ataques por dia | M1 (API) + battlelog | Número de batalhas de guerra por jogador por dia |
| Pontuação da guerra | M1 (API) + currentriverrace | Total de pontos do jogador na guerra |
| Status do clã | M1 (API) + currentriverrace | Se o clã cruzou a linha de chegada e em qual posição |
| Thresholds e mínimo | M4 (Configuração) | Valores configuráveis (4, 4, 1600, mínimo do clã) |

| Saída | Para onde vai | O que entrega |
|---|---|---|
| Cartões por jogador | M3 (Painel) | Status atual: contagem de amarelos, vermelhos, pretos |
| Status de expulsão | M3 (Painel) | Flag "candidato a expulsão" |
| Histórico de cartões | M5 (Banco) | Dados persistidos para consulta histórica |

---

## Acceptance criteria

- WHEN um jogador faz 3/4 ataques em um dia THE SYSTEM SHALL atribuir 1 cartão amarelo.
- WHEN um jogador faz 0/4 ataques em um dia THE SYSTEM SHALL atribuir 4 cartões amarelos que
  se convertem imediatamente em 1 cartão vermelho.
- WHEN um jogador acumula 4 cartões vermelhos THE SYSTEM SHALL marcar o jogador como ⚫ PRETO
  (candidato a expulsão).
- WHEN a pontuação do jogador na guerra é menor que 1600 THE SYSTEM SHALL adicionar 1 cartão
  amarelo.
- WHEN a pontuação do jogador na guerra é menor que o mínimo do clã THE SYSTEM SHALL
  adicionar 1 cartão vermelho.
- WHEN o clã cruza a linha de chegada em 1º lugar no sábado THE SYSTEM SHALL não emitir
  cartões para o domingo.
- WHEN o líder consulta o status THE SYSTEM SHALL exibir apenas cartões das últimas 4 semanas
  como ativos para o status de expulsão.
- WHEN o líder expande o histórico THE SYSTEM SHALL exibir cartões de até 3 meses.

## Edge cases

- Jogador entra no clã no meio da guerra (quinta já passou): conta apenas dias como membro
  para ataques faltantes. Penalidades de **pontuação são relaxadas** proporcionalmente
  (ex: entrou no sábado → mínimo de pontos é ajustado aos dias jogados).
- Jogador sai e volta: histórico anterior é preservado e exibido.
- API indisponível: sistema reporta "dados indisponíveis" e mantém último estado conhecido.
- Empate na corrida: se o clã cruzou a linha mas há empate, a API define a posição final.
- Guerra cancelada ou sem adversários: não gera cartões.
