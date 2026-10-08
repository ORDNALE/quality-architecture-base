# Workflow FIX — refatoração autorizada e incremental

**Objetivo:** corrigir achados selecionados **somente** dentro de escopo explicitamente autorizado,
preservando regra de negócio, contratos, transações e permissões, com baseline e validação.

**Papéis:** Controlled Refactorer (`roles/CONTROLLED_REFACTORER.md`) para alterar;
Regression/Performance Validator (`roles/REGRESSION_VALIDATOR.md`) para baseline e validação.

## Pré-condições (todas obrigatórias antes de alterar qualquer arquivo de código ou teste)

Os passos 1–2 abaixo produzem o plano e a autorização; só então o código pode ser alterado.

1. Pedido **explícito** de FIX pelo usuário nesta sessão. Esse pedido **não** é a autorização.
2. Achados de origem identificados (relatório de AUDIT/REVIEW ou descrição do usuário convertida em achados).
3. Plano `.quality/plans/PLAN-<data>-<slug>.md` criado a partir de `templates/REFACTORING_PLAN.md`.
4. Seção **Autorização** do plano com `Status: AUTHORIZED`, responsável, evidência literal da
   autorização, achados e arquivos autorizados.
5. `python3 scripts/fix_gate.py check <plano>` com exit code 0.

Se qualquer item faltar: **pare**. Prepare o plano, mostre-o ao usuário e peça autorização. Não
altere nenhum arquivo de código enquanto isso.

## Proibido

- Alterar regra de negócio sem autorização separada (G-04).
- Ampliar escopo silenciosamente (G-03); "melhorias de passagem"; formatação em massa.
- Remover/desabilitar/enfraquecer testes (G-05).
- Commit, push, tag, deploy, migrations em ambiente compartilhado (G-01).
- Sobrescrever alterações não commitadas do usuário (G-11).

## Passos

1. **Planejar** (Controlled Refactorer)
   - Preencha problema, evidência, comportamento observável a preservar, alternativas, escopo,
     conflitos (`references/conflict-resolution.md`), riscos, verificações e critérios de aceite.
2. **Autorizar** (humano)
   - Mostre o plano com `Status: PENDING`, informe a frase de autorização exata
     ("Autorizo <identificador-do-plano>") e **encerre o turno**. Não altere código neste turno.
   - Somente quando uma mensagem **posterior** do usuário aprovar esse plano pelo identificador,
     transcreva-a literalmente em `Evidência da autorização` e marque `AUTHORIZED`.
   - Ajustes pedidos pelo usuário mudam o plano; apresente-o de novo antes de nova autorização.
   - Em execução não interativa, termine aqui com o plano `PENDING`.
   - Rode `fix_gate.py check`.
3. **Baseline** (Regression Validator)
   - `tree_snapshot.py create` (fora do projeto).
   - Compilação e testes existentes; registre resultados, inclusive falhas pré-existentes.
   - Medições do plano (contagem de consultas, `EXPLAIN`, bundle) quando aplicáveis e possíveis.
4. **Testes de caracterização** (Controlled Refactorer)
   - Quando a área não tem cobertura suficiente (UNI-BRP-002, TST-STR-003): adicione testes que
     passam **antes** da refatoração. Esses arquivos de teste precisam estar em "Arquivos autorizados".
5. **Refatorar em passos pequenos**
   - Um passo por vez, conforme o plano §9. Após cada passo: compilar e rodar os testes relevantes.
   - Se surgir necessidade fora do escopo ou conflito irreconciliável: pare **apenas** essa
     alteração, registre no plano e peça decisão.
6. **Validar** (Regression Validator)
   - `fix_gate.py check <plano> --project <projeto> --changed-from-git` — arquivos alterados dentro do escopo.
   - `tree_snapshot.py compare --snapshot <arquivo> --allow <globs autorizados>`.
   - Mesmos comandos do baseline; compare antes/depois; testes de caracterização verdes.
   - Comparação de contratos e consultas quando relevante.
7. **Relatar**
   - `templates/REGRESSION_REPORT.md` → `.quality/reports/REGRESSION-<data>-<slug>.md`.
   - Conclusão honesta: "sem regressão detectada" somente com cobertura adequada; caso contrário,
     "ausência de regressão não comprovada".
   - Atualize `.quality/QUALITY_STATE.md`.
   - Liste os arquivos alterados para o usuário revisar e commitar **ele mesmo**.

## Se um teste falhar após a mudança

1. Não altere o teste. Leia a falha.
2. Se a falha revela mudança de comportamento: ajuste a implementação ou reverta o passo.
3. Se o teste parecer errado: pare e peça decisão humana (CF-16).

## Critérios de saída

- [ ] `fix_gate.py check --changed-from-git` exit 0.
- [ ] Testes pré-existentes não removidos/enfraquecidos; resultados antes/depois registrados.
- [ ] Critérios de aceite do plano atendidos ou explicitamente não atendidos.
- [ ] Nenhum commit/push realizado.
