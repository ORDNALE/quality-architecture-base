# Regras de testes — estratégia e regressão

### TST-STR-001 — Baseline executado antes de qualquer FIX

- **Aplica-se quando:** FIX.
- **Verificar:** compilação e suíte de testes existentes executadas antes da mudança, com resultado registrado (inclusive falhas pré-existentes).
- **Evidência mínima:** E2 (saída real dos comandos).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** testes que já falham antes da mudança são registrados como pré-existentes, não "consertados" pelo FIX.
- **Correção preferida:** executar e registrar no plano §8.
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
- **Verificar:** existe teste que fixa o JSON atual (campos, nulos, formatos, status) dos endpoints afetados.
- **Evidência mínima:** teste passando antes e depois (E2).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** valores voláteis (datas de criação, ids) devem ser controlados, não ignorados em massa.
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
- **Verificar:** testes unitários/componentes/E2E existentes cobrindo navegação, busca com debounce/cancelamento e paginação.
- **Evidência mínima:** E2.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** ausência de testes vira limitação declarada no relatório de regressão.
- **Correção preferida:** testes de componente para o fluxo alterado.
- **Conflitos:** CF-04

### TST-STR-006 — Testes determinísticos

- **Aplica-se quando:** sempre.
- **Verificar:** dependência de relógio real, fuso, aleatoriedade, ordem de execução, dados compartilhados, `sleep`.
- **Evidência mínima:** E3; E2 (falha intermitente reproduzida).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** —
- **Correção preferida:** relógio injetável, dados isolados, espera por condição.
- **Conflitos:** nenhum conhecido
