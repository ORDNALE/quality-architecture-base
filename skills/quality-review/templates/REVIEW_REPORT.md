# REVIEW_REPORT — <nome do projeto> — <AAAA-MM-DD>

- **Modo:** REVIEW
- **Alvo:** <`git diff main...HEAD` | arquivos: ... | PR #n>
- **Arquivos analisados:** <n> (lista na seção 5)
- **Perfis aplicados:** <arquitetura> · <stacks>
- **Fontes alteradas durante a revisão:** <nenhuma — comprovado por `tree_snapshot.py compare` | não verificado>

> Para alteração pequena, usar seção curta no estado/relatório consolidado existente conforme
> `references/contracts.md` §7: alvo/revisão, parecer, achados (ou nenhum), verificações novas ou
> reutilizadas e limites. Não criar arquivo ou tabela vazia por obrigação de preencher template.
> Usar o formato completo abaixo quando o risco/decisão justificar; campos dos achados (§5)
> continuam obrigatórios quando houver achado.

## 1. Parecer

**<APROVADO | APROVADO COM RESSALVAS | ALTERAÇÕES NECESSÁRIAS | INCONCLUSIVO>**

Justificativa em até 5 linhas. `INCONCLUSIVO` quando faltou contexto/verificação para opinar.

## 2. Achados no diff

> Mesmo formato de achado do relatório de auditoria (ver `references/contracts.md` §5).
> Apenas problemas **introduzidos ou agravados** pelo diff; dívida pré-existente vai na seção 4.

### F-001 — <título>

| Campo | Valor |
|---|---|
| Severidade | |
| Estado | |
| Local | |
| Regra | |
| Descrição | |
| Evidência | |
| Impacto | |
| Correção sugerida | |
| Conflitos | |
| Risco de regressão | |
| Testes necessários | |

## 3. Possíveis regressões de comportamento

| Área | Mudança observada | Regra de negócio afetada? | Teste que cobre | Situação |
|---|---|---|---|---|
| <cálculo, permissão, transação, contrato HTTP, paginação, consulta> | | | | <coberto / não coberto> |

## 4. Dívida pré-existente notada (fora do escopo do diff)

## 5. Arquivos analisados

## 6. Verificações executadas e limitações
