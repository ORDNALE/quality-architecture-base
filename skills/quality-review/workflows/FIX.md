# Workflow FIX — refatoração autorizada e incremental

**Objetivo:** corrigir achados selecionados **somente** dentro de escopo explicitamente autorizado,
preservando regra de negócio, contratos, transações e permissões, com baseline e validação.

**Papéis:** Controlled Refactorer (`roles/CONTROLLED_REFACTORER.md`) para alterar;
Regression/Performance Validator (`roles/REGRESSION_VALIDATOR.md`) para baseline e validação.

Seleção de verificações, evidência reutilizável e registro compacto: `references/contracts.md`
§7. Essa política não dispensa nenhuma pré-condição de autorização abaixo.

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
   - Identificar baseline válido das áreas afetadas (novo ou reutilizado conforme contracts §7);
     registrar revisão, origem, escopo, comandos/resultados, conferência e falhas pré-existentes.
   - Medições do plano (contagem de consultas, `EXPLAIN`, bundle) quando aplicáveis e possíveis.
4. **Testes de caracterização** (Controlled Refactorer)
   - Quando a área não tem cobertura suficiente (UNI-BRP-002, TST-STR-003): adicione testes que
     passam **antes** da refatoração. Esses arquivos de teste precisam estar em "Arquivos autorizados".
5. **Refatorar em passos pequenos**
   - Um passo por vez, conforme o plano §9; validar o comportamento/invariantes afetados com
     testes focais. Compilação incluída nesses comandos não precisa de outra execução idêntica.
     Suítes completas seguem os marcos/impacto de contracts §7, não cada edição mecânica.
   - Se surgir necessidade fora do escopo ou conflito irreconciliável: pare **apenas** essa
     alteração, registre no plano e peça decisão.
6. **Validar** (Regression Validator)
   - `fix_gate.py check <plano> --project <projeto> --changed-from-git` — arquivos alterados dentro do escopo.
   - `tree_snapshot.py compare --snapshot <arquivo> --allow <globs autorizados>`.
   - As duas checagens de escopo são complementares, não redundantes: `git status` vê arquivos
     rastreados em pastas que o snapshot ignora (`build/`, `dist/`, `out/`, `target/`); o snapshot
     vê arquivos ignorados pelo Git que `git status` omite. Mantenha ambas.
   - Comparar verificações equivalentes do escopo afetado antes/depois; reutilizar resultados
     ainda válidos, sem repetir comandos por passagem de papel. Cobrir mudanças posteriores e
     lacunas; testes de caracterização relevantes verdes, globais quando o impacto justificar.
   - Comparação de contratos e consultas quando relevante.
7. **Relatar**
   - Registrar conforme `templates/REGRESSION_REPORT.md`; para mudanças pequenas, seção curta
     no estado/relatório consolidado existente, com referência ao plano e evidências (contracts §7).
   - Conclusão honesta: "sem regressão detectada" somente com cobertura adequada; caso contrário,
     "ausência de regressão não comprovada".
   - Manter `.quality/QUALITY_STATE.md` como índice do resultado, sem duplicar o relatório;
     se o resultado já estiver nele, não criar um segundo registro equivalente.
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
