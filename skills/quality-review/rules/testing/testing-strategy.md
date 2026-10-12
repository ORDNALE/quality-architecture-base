# Regras de testes — estratégia e regressão

Aplicar a política geral de `references/contracts.md` §7: cobertura por comportamento/risco,
testes focais, marcos de validação completa e evidência reutilizável, sem enfraquecer testes.

### TST-STR-001 — Baseline válido identificado antes de qualquer FIX

- **Aplica-se quando:** FIX.
- **Verificar:** baseline das áreas afetadas identificado antes da mudança, executado ou reutilizado conforme contracts §7, com revisão, escopo, origem, comandos/resultados e conferência de validade (inclusive falhas pré-existentes).
- **Evidência mínima:** saída real identificada e conferência da revisão/diffs e condições relevantes; discriminar execução própria de evidência anterior/relatada, sem promovê-la a E2 novo.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** testes que já falham antes da mudança são registrados como pré-existentes, não "consertados" pelo FIX.
- **Correção preferida:** registrar no plano §8 a referência válida ou executar apenas as verificações necessárias para preencher lacunas/invalidações; justificar suítes completas pelo impacto.
- **Conflitos:** nenhum conhecido

### TST-STR-002 — Testes de integração representativos do banco real

- **Aplica-se quando:** regras que dependem de SQL, transações, tipos numéricos, colação, datas.
- **Verificar:** testes de persistência rodando em banco diferente do de produção (ex.: H2 no lugar de PostgreSQL), escondendo diferenças de SQL, tipos e comportamento.
- **Evidência mínima:** E3 (configuração de teste).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** Dev Services/Testcontainers dependem de Docker disponível; se não houver, registre a limitação em vez de trocar o banco.
- **Correção preferida:** PostgreSQL de teste (Dev Services/Testcontainers) para testes sensíveis a SQL, como recomendação.
- **Conflitos:** nenhum conhecido

### TST-STR-003 — Teste de contrato antes de mudar DTOs/serialização

- **Aplica-se quando:** FIX que troca Entity por DTO, introduz Mapper, muda serialização ou paginação.
- **Verificar:** existe cobertura adequada do JSON atual (campos, nulos, formatos, status) dos endpoints afetados; reutilizar testes de contrato existentes, acrescentando somente lacunas reais.
- **Evidência mínima:** cobertura de contrato com resultados antes/depois identificados; discriminar execução nova de baseline reutilizado conforme contracts §7, sem promover evidência anterior a E2 novo.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** valores voláteis (datas de criação, ids) devem ser controlados, não ignorados em massa; DTO interno sem impacto no contrato não exige teste de serialização/getter por si só.
- **Correção preferida:** RestAssured/cliente de teste com asserções de estrutura e valores, ou snapshot aprovado.
- **Conflitos:** CF-02

### TST-STR-004 — Regressão de N+1 detectável por teste

- **Aplica-se quando:** correção de N+1 ou mudança de estratégia de carregamento.
- **Verificar:** existe forma automatizada de detectar o retorno do problema (contagem de statements constante em relação ao número de itens).
- **Evidência mínima:** E2.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** só com mecanismo já disponível ou autorizado (G-07).
- **Correção preferida:** teste com 1 e N itens comparando contagens.
- **Conflitos:** nenhum conhecido

### TST-STR-005 — Testes frontend nos fluxos afetados

- **Aplica-se quando:** mudanças de frontend (lazy loading, paginação, busca, estado).
- **Verificar:** cobertura relevante do fluxo alterado no nível adequado (unitário, componente ou E2E), reutilizando casos existentes; não exigir automaticamente os três níveis para o mesmo cenário.
- **Evidência mínima:** E2.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** ausência de testes vira limitação declarada no relatório de regressão.
- **Correção preferida:** testes de componente para o fluxo alterado; E2E seletivo para jornadas críticas ou riscos específicos de navegador, sem duplicar toda a matriz unitária.
- **Conflitos:** CF-04

### TST-STR-006 — Testes determinísticos

- **Aplica-se quando:** sempre.
- **Verificar:** dependência de relógio real, fuso, aleatoriedade, ordem de execução, dados compartilhados, `sleep`.
- **Evidência mínima:** E3; E2 (falha intermitente reproduzida).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** —
- **Correção preferida:** relógio injetável, dados isolados, espera por condição.
- **Conflitos:** nenhum conhecido
