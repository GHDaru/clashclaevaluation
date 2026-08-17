# UX Design 001 — ClashClanEvaluation

- **Spec**: `spec.md` · **Plan**: `plan.md` · **Date**: 2026-08-16
- **Rule**: Semantic role before component. Define WHAT each element means before HOW it looks.

---

## T1: Painel do Clã (Dashboard)

### Semantic roles

| Element | Role | States |
|---|---|---|
| **War status bar** | Informa o contexto atual da guerra | `active` (dia X de 4), `finished` (posição final), `no_war` (sem guerra) |
| **Early victory badge** 🏁 | Indica que o clã venceu antecipadamente e regras estão relaxadas | `visible` (vitória antecipada ativa), `hidden` |
| **Player row** | Unidade de avaliação — um membro do clã com seu status | `clean` (✅), `warning` (🟡), `danger` (🔴), `critical` (⚫🔥) |
| **Attacks indicator** | Quantos ataques o jogador fez hoje | `4/4` (completo), `2/4` (parcial), `0/4` (faltou) |
| **Cards indicator** | Cartões acumulados na guerra | ícones com contagem (🟡×3, 🔴×1, ⚫×1) |
| **Sort control** | Ordenação da tabela | `cards_desc` (pior primeiro, default), `name_asc`, `points_desc` |
| **Refresh button** | Ação de re-coletar dados da API e reavaliar | `idle`, `loading` (spinner), `error` (se API falhar) |

### Journey served

```
Líder abre o painel → vê o status da guerra → identifica jogadores críticos
→ clica em um jogador para detalhe → decide sobre expulsão (fora do sistema)
```

---

## T2: Detalhe do Jogador (Player Card — modal/expansão)

### Semantic roles

| Element | Role | States |
|---|---|---|
| **Player header** | Identificação do jogador | nome, tag, role, tempo no clã |
| **Status badge** | Status atual de avaliação | `clean`, `warning`, `danger`, `critical` |
| **Current war table** | Ataques dia a dia na guerra atual | 4 linhas (Qui-Sex-Sáb-Dom) com contagem e ícone |
| **Recency summary** | Cartões na janela ativa (4 semanas) | total 🟡, 🔴, ⚫ + tendência (📈➡️📉) |
| **Trend indicator** | Direção do comportamento | `improving` (cartões diminuindo), `stable`, `declining` (aumentando), `new` (1ª guerra) |
| **History table** | Guerras passadas (4 semanas, expansível para 3 meses) | cada linha = 1 guerra com ataques, pontos, cartões |
| **Expand button** | Alterna entre 4 semanas e 3 meses | `collapsed` (4 semanas), `expanded` (3 meses), `loading` |
| **Justification text** | Explica por que o jogador está naquele status | "4 vermelhos = 16 ataques faltantes" |

---

## T3: Configuração (Config Panel)

### Semantic roles

| Element | Role | States |
|---|---|---|
| **Config group card** | Agrupa parâmetros relacionados | Grupos A–E (Cards, Scoring, War, Recency, Relaxation) |
| **Param field** | Um parâmetro configurável | `value` (atual), `default` (original), `range` (min–max) |
| **Range slider or number input** | Controle de valor numérico | `valid` (dentro do range), `invalid` (fora, bloqueado) |
| **Toggle switch** | Parâmetro booleano | `on`, `off` (ex: relax_on_first_place) |
| **Save button** | Persiste configuração | `idle`, `saving`, `saved` (confirmação), `error` |
| **Restore defaults button** | Retorna todos os parâmetros ao default | `idle`, `confirm` (modal de confirmação), `restored` |

---

## Design constraints (not components, rules)

1. **Escaneabilidade**: o painel T1 deve permitir identificar jogadores críticos em < 5
   segundos. Ordenação default pior→melhor. Cores têm papel funcional, não decorativo.
2. **Ação mínima**: o líder não deve precisar de mais de 2 cliques para chegar a qualquer
   informação (1: abrir painel, 2: clicar no jogador).
3. **Confirmação implícita**: o sistema nunca executa ações destrutivas. A informação
   "candidato a expulsão" é uma recomendação — o botão de expulsão não existe (está fora
   do escopo do sistema).
4. **Responsivo**: o painel funciona em desktop (principal) e mobile (consulta rápida).
5. **Tema escuro**: jogadores de Clash Royale frequentemente usam dispositivos à noite.
   Suporte a dark mode é esperado.

---

## Future (YAGNI — not this cycle)

- Gráficos de tendência (sparklines) → texto + ícone é suficiente para v1
- Comparação lado a lado de jogadores
- Exportação de relatório (PDF/CSV)
- Notificações push
