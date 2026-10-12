# Regras universais — preservação de regra de negócio e refatoração segura

Refatoração não autoriza alteração de regra negocial. Estas regras valem em AUDIT (como critério de
risco), em REVIEW (como detector de regressão) e principalmente em FIX.

### UNI-BRP-001 — Comportamento observável identificado antes da mudança

- **Aplica-se quando:** FIX; REVIEW de refatorações.
- **Verificar:** o plano lista contratos, cálculos, validações, permissões, transações e efeitos colaterais que não podem mudar; existe baseline válido das áreas afetadas (compilação, testes, contagem de consultas quando relevante), executado ou reutilizado e identificado conforme `references/contracts.md` §7.
- **Evidência mínima:** plano preenchido + baseline identificado (revisão, escopo, origem, comandos/resultados, validade). Execução própria nesta sessão: E2/E1; reutilizado ou relatado por outro agente: mantém a classificação original (E5 se anterior e não refeito — `references/evidence.md`), sem promoção a E1/E2.
- **Severidade base:** HIGH (mudança sem baseline em área crítica)
- **Falsos positivos / cuidados:** mudanças puramente mecânicas verificadas pelo compilador (ex.: remover import não usado) dispensam teste de caracterização, não o baseline de compilação.
- **Correção preferida:** completar o plano e identificar baseline válido (reutilizar, ou executar só as lacunas e invalidações) antes de alterar código.
- **Conflitos:** CF-16

### UNI-BRP-002 — Testes de caracterização em código sem cobertura

- **Aplica-se quando:** FIX em código com regra de negócio e cobertura insuficiente.
- **Verificar:** existência de testes que fixam o comportamento atual (entradas e saídas reais, inclusive bordas: zero, negativos, arredondamento, datas de virada, fuso).
- **Evidência mínima:** testes adicionados passando **antes** da refatoração (E2).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** se o comportamento atual parecer errado, o teste o fixa mesmo assim e a suspeita vira decisão humana (CF-16).
- **Correção preferida:** testes de caracterização no menor nível que exercite a regra (unitário de Service; integração se depende de SQL).
- **Conflitos:** CF-16

### UNI-BRP-003 — Precisão numérica, monetária e temporal

- **Aplica-se quando:** sempre que há dinheiro, quantidades, impostos, datas ou horários.
- **Verificar:** `double`/`float` para dinheiro; `BigDecimal` com `equals` em vez de `compareTo`; escala/arredondamento implícitos; `new BigDecimal(double)`; `LocalDateTime` onde o fuso importa; `Date`/`Calendar` legados; JavaScript `Number` para valores monetários; conversões de tipo SQL (`numeric` → `double`).
- **Evidência mínima:** E3.
- **Severidade base:** HIGH (CRITICAL se já produz valor incorreto comprovado)
- **Falsos positivos / cuidados:** a mudança de tipo altera resultados — é alteração de regra de negócio e exige autorização (G-04).
- **Correção preferida:** registrar e propor; em FIX, somente com autorização explícita e testes de caracterização.
- **Conflitos:** CF-03, CF-16

### UNI-BRP-004 — Escopo do FIX respeitado

- **Aplica-se quando:** FIX; REVIEW de diffs produzidos por FIX.
- **Verificar:** arquivos alterados ⊆ arquivos autorizados; nenhuma melhoria "de passagem"; nenhuma formatação em massa; nenhum upgrade de dependência não autorizado.
- **Evidência mínima:** `git status --porcelain` / `git diff --name-only` + `fix_gate.py check` (E2).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** arquivos gerados pelo build não versionados.
- **Correção preferida:** reverter apenas a parte fora de escopo feita pelo próprio agente (nunca alterações do usuário) ou pedir ampliação da autorização.
- **Conflitos:** nenhum conhecido

### UNI-BRP-005 — Integridade dos testes

- **Aplica-se quando:** FIX; REVIEW.
- **Verificar:** testes removidos, desabilitados (`@Disabled`, `@Ignore`, `skip`, `xit`, `.only`), asserções afrouxadas, tolerâncias aumentadas, mocks que substituem a unidade sob teste, expectativas alteradas para coincidir com a nova saída.
- **Evidência mínima:** diff dos testes (E3).
- **Severidade base:** CRITICAL quando feito para "passar" um FIX; HIGH nos demais casos.
- **Falsos positivos / cuidados:** teste comprovadamente errado pode ser corrigido com autorização e justificativa registrada.
- **Correção preferida:** restaurar o teste e investigar a implementação.
- **Conflitos:** nenhum conhecido

### UNI-BRP-006 — Transações, permissões e efeitos colaterais preservados

- **Aplica-se quando:** mudanças que movem código, alteram chamadas entre beans, ou mexem em anotações.
- **Verificar:** fronteiras de `@Transactional` (inclusive autoinvocação), `@RolesAllowed`/checagens manuais, ordem de eventos, envio de mensagens, auditoria, idempotência.
- **Evidência mínima:** E3 antes/depois; testes de integração quando existirem (E2).
- **Severidade base:** CRITICAL
- **Falsos positivos / cuidados:** nenhuma mudança de comportamento ≠ nenhuma mudança de código; comparar efeitos, não texto.
- **Correção preferida:** manter as fronteiras; se impossível, suspender e pedir decisão.
- **Conflitos:** CF-06
