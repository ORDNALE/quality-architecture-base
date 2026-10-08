# AUDIT_REPORT — <nome do projeto> — <AAAA-MM-DD>

- **Modo:** AUDIT (<completo | incremental: escopo>)
- **Commit/estado analisado:** <hash `git rev-parse HEAD` + "há alterações não commitadas" se houver>
- **Perfil do projeto:** `.quality/PROJECT_PROFILE.md` (revisão <n>) — <revisado por humano? sim/não>
- **Perfis aplicados:** <arquitetura> · <stacks>
- **Regras carregadas:** <arquivos de `rules/` usados>
- **Executor:** <ferramenta/agente> — papel: Architecture Auditor
- **Fontes alteradas durante a auditoria:** <nenhuma — comprovado por `tree_snapshot.py compare` | não verificado>

## 1. Resumo executivo

| Severidade | CONFIRMED | PROBABLE | NEEDS_VERIFICATION | NOT_REPRODUCED |
|---|---|---|---|---|
| CRITICAL | | | | |
| HIGH | | | | |
| MEDIUM | | | | |
| LOW | | | | |
| INFO | | | | |

Principais riscos em 3–5 linhas, sem jargão desnecessário.

## 2. Verificações executadas

> Somente o que foi realmente executado. Comandos não executados vão para a seção 7.

| Verificação | Comando | Resultado | Observação |
|---|---|---|---|
| <compilação> | <`./mvnw -q -DskipTests compile`> | <ok / falhou / não executado> | |

## 3. Achados priorizados

> Ordem: severidade, depois estado (CONFIRMED primeiro), depois custo de correção.

### F-001 — <título>

| Campo | Valor |
|---|---|
| Severidade | <CRITICAL/HIGH/MEDIUM/LOW/INFO> |
| Estado | <CONFIRMED/PROBABLE/NEEDS_VERIFICATION/NOT_REPRODUCED> |
| Local | `<arquivo>:<linhas>` |
| Regra | `<ID>` |
| Descrição | |
| Evidência | <tipo: E1–E5 (ver references/evidence.md)> — <trecho/saída/medição> |
| Impacto | |
| Correção sugerida | <recomendada>; alternativas: <...>; descartadas: <... e por quê> |
| Conflitos | <`CF-xx` ou nenhum> |
| Risco de regressão | |
| Testes necessários | |

## 4. Conflitos entre diretrizes identificados

| Conflito | Achados | Recomendação | Decisão humana necessária? |
|---|---|---|---|

## 5. Exceções do perfil aplicadas

| Exceção | Achados suprimidos/rebaixados | Ainda válida? |
|---|---|---|

## 6. Riscos de segurança encaminhados

> Esta base não faz auditoria de segurança. Registre aqui o que foi notado de passagem, para
> análise pelo agente/processo de segurança especializado. Não detalhe exploração.

| Local | Observação | Encaminhado para |
|---|---|---|

## 7. Limitações desta auditoria

- <ex.: sem banco disponível para EXPLAIN; achados de índice são NEEDS_VERIFICATION>
- <ex.: versão do Hibernate gerenciada pelo BOM não resolvida>
- <ex.: frontend fora do escopo>

## 8. Próximos passos sugeridos

1. <ex.: decidir CF-01 para F-003>
2. <ex.: autorizar FIX de F-001 e F-002 via plano>
