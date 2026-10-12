# REGRESSION_REPORT — <slug> — <AAAA-MM-DD>

- **Plano:** `.quality/plans/PLAN-....md`
- **Executor:** <ferramenta/agente> — papel: Regression/Performance Validator
- **Estado do código:** <hash base> + alterações não commitadas do FIX

> Registro compacto/consolidado permitido por `references/contracts.md` §7: plano/escopo/revisão,
> conclusão, origem e validade das evidências, integridade dos testes e pendências. Referenciar
> resultados já documentados, sem copiar logs ou gerar um relatório por passo.
> Distinguir explicitamente comandos novos, resultados reutilizados e verificações não executadas.

## 1. Conclusão

**<SEM REGRESSÃO DETECTADA | REGRESSÃO DETECTADA | AUSÊNCIA DE REGRESSÃO NÃO COMPROVADA>**

> Use `AUSÊNCIA DE REGRESSÃO NÃO COMPROVADA` sempre que a cobertura de testes ou as medições
> forem insuficientes para a área alterada. "Testes passaram" não implica "sem regressão" se os
> testes não exercitam o comportamento alterado.

## 2. Escopo verificado

- Arquivos alterados (saída real de `git status --porcelain` / `git diff --name-only`):
- Dentro do escopo autorizado? <sim — `fix_gate.py check` exit 0 | não: ...>

## 3. Comparação antes/depois

| Verificação | Comando | Antes | Depois | Situação |
|---|---|---|---|---|
| Compilação | | | | |
| Testes (total/falhas/ignorados) | | | | |
| Testes de caracterização | | | | |
| Contrato HTTP (amostras/snapshots) | | | | |
| Nº de consultas SQL no cenário | | | | |
| Plano de execução / tempo | | | | |
| Bundle inicial (frontend) | | | | |

## 4. Integridade dos testes

- Testes removidos: <nenhum | lista + motivo autorizado>
- Testes desabilitados (`@Disabled`, `skip`, `xit`): <nenhum | lista>
- Asserções enfraquecidas: <nenhuma | lista>

## 5. Regras de negócio preservadas

| Regra/comportamento (do plano §3) | Como foi verificado | Resultado |
|---|---|---|

## 6. Desempenho

> Somente medições reais, com ambiente, volume de dados e número de execuções. Sem medição, escreva
> "não medido" — nunca estime números.

## 7. Pendências e riscos residuais
