# REFACTORING_PLAN — <slug> — <AAAA-MM-DD>

> Plano obrigatório para o modo FIX. Fica em `.quality/plans/`. Nenhuma linha de código é
> alterada antes de a seção **Autorização** estar preenchida e `scripts/fix_gate.py check` passar.

> Formato proporcional: `references/contracts.md` §7. O corpo pode condensar itens aplicáveis em
> problema/escopo, riscos/contratos e verificações/aceite, referenciando evidências existentes.
> Preservar sempre identificador, arquivo formal, bloco de autorização e gates; não criar plano
> por subpasso do mesmo escopo já autorizado. Seções sem pertinência não exigem texto artificial.

- **Projeto:** <nome>
- **Origem:** <relatório `.quality/reports/AUDIT-....md`, achados F-...>
- **Executor:** <ferramenta/agente> — papel: Controlled Refactorer

## 1. Problema

<Para cada achado: o que está errado e por que importa. Referencie o achado, não repita o relatório.>

## 2. Evidência

| Achado | Estado no relatório | Evidência | Precisa medir antes? |
|---|---|---|---|

## 3. Comportamento observável a preservar

> Liste o que **não** pode mudar. Seja específico.

- Contratos HTTP (status, campos, nomes, formatos de data/número, ordenação, paginação):
- Regras de negócio (cálculos, arredondamento, precisão monetária, estados, validações):
- Permissões e autenticação:
- Transações (fronteiras, propagação, rollback):
- Consultas (linhas retornadas, ordenação, filtros):
- Efeitos colaterais (eventos, e-mails, integrações, auditoria):

## 4. Alternativas consideradas

| Alternativa | Prós | Contras | Escolhida? |
|---|---|---|---|

## 5. Escopo

- **Dentro:** <arquivos/classes/métodos>
- **Fora (explicitamente):** <o que não será tocado mesmo que pareça relacionado>
- **Regra de negócio alterada:** NÃO <!-- qualquer "sim" exige autorização separada e explícita -->

## 6. Diretrizes em conflito

| Conflito (`CF-xx`) | Como foi resolvido | Decisão humana? |
|---|---|---|

## 7. Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|

## 8. Baseline e verificações

| Verificação | Comando | Resultado ANTES | Resultado DEPOIS |
|---|---|---|---|
| Compilação | | | |
| Testes unitários | | | |
| Testes de integração | | | |
| Testes de caracterização novos | | | |
| Contagem de consultas SQL (cenário X) | | | |
| EXPLAIN (consulta Y) | | | |
| Snapshot de fontes | `tree_snapshot.py create` | <arquivo> | `compare` |

## 9. Passos incrementais

> Cada passo que afete comportamento/invariantes exige as verificações pertinentes; focais durante
> implementação, globais nos marcos justificados. Não repetir evidência válida nem compilação já
> incluída no comando. Na seção 8, marque cada resultado como `novo` ou `reutilizado (origem,
> revisão)` (contracts §7).

1. <adicionar teste de caracterização para ...>
2. <...>

## 10. Critérios de aceite

- [ ] Testes existentes preservados; verificações pertinentes passam, com seleção, marcos e limites
      registrados conforme contracts §7, sem remover/desabilitar/enfraquecer casos para obter verde.
- [ ] Testes de caracterização, somente se a cobertura existente for insuficiente (UNI-BRP-002),
      passam antes e depois; caso contrário, indicar a cobertura existente que protege o comportamento.
- [ ] Contratos listados na seção 3 inalterados (evidência: ...).
- [ ] Arquivos alterados ⊆ arquivos autorizados (`fix_gate.py check --changed-from-git`).
- [ ] <critério de desempenho medido, se aplicável>

## 11. Autorização

<!-- qab:authorization:start -->
- Status: PENDING
- Autorizado por:
- Data:
- Evidência da autorização:
- Achados autorizados:
- Arquivos autorizados:
- Alteração de regra de negócio autorizada: NÃO
<!-- qab:authorization:end -->

> Formato aceito pelo `fix_gate.py`:
> - `Status:` um de `PENDING`, `AUTHORIZED`, `REJECTED`.
> - `Achados autorizados:` IDs separados por vírgula (ex.: `F-001, F-004`).
> - `Arquivos autorizados:` lista em sub-itens `  - caminho/ou/glob/**` relativos à raiz do projeto.
> - `Evidência da autorização:` citação literal da mensagem do usuário, **posterior** à
>   apresentação deste plano, que contenha o identificador do plano (nome deste arquivo sem `.md`).
>   O pedido inicial de FIX não serve como autorização.
> - O agente só preenche `AUTHORIZED` transcrevendo essa autorização. Nunca por iniciativa própria.
