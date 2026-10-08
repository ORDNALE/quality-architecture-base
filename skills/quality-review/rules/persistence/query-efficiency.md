# Regras de persistência — N+1, carregamento e eficiência de consultas

Achados desta área sem medição são hipóteses (`PROBABLE`/`NEEDS_VERIFICATION`). Para confirmar, use
log SQL, contador de consultas e/ou `EXPLAIN` em ambiente adequado (G-12, PRF-MEA-001).

### PER-N1-001 — N+1 por associação acessada em laço

- **Aplica-se quando:** ORM (Hibernate/JPA/Panache).
- **Verificar:** laço, `stream().map`, Mapper ou serialização que acessa associação LAZY (to-one ou coleção) para cada elemento de uma lista; Repository chamado dentro de laço.
- **Evidência mínima:** E3 rastreando lista → laço → associação (PROBABLE); E1 com contagem de consultas proporcional ao número de itens (CONFIRMED).
- **Severidade base:** HIGH em listagens/relatórios de coleções grandes; MEDIUM/LOW em coleções pequenas e limitadas.
- **Falsos positivos / cuidados:** associação já buscada (`JOIN FETCH`, `EntityGraph`), batch fetching efetivo (`@BatchSize` ou configuração global — confira o valor efetivo da versão), cache de segundo nível, entidades já no contexto de persistência.
- **Correção preferida:** escolher por caso — projeção DTO; `JOIN FETCH`/`EntityGraph` para to-one; batch fetching; consulta dedicada em duas etapas para coleções. **Não** usar `JOIN FETCH` de coleção com paginação (CF-01).
- **Conflitos:** CF-01, CF-03

### PER-N1-002 — Consultas redundantes

- **Aplica-se quando:** sempre que há acesso a banco.
- **Verificar:** mesma consulta repetida na mesma requisição; `findById` do mesmo registro em várias camadas; carregar entidade inteira apenas para obter o id ou um campo; validação de existência seguida de nova busca.
- **Evidência mínima:** E3 ou E1.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** o contexto de persistência pode evitar a segunda ida ao banco em `find` por id dentro da mesma transação — verificar antes de afirmar custo.
- **Correção preferida:** reutilizar o resultado; consulta específica; `getReference` quando só a referência é necessária (cuidado com `EntityNotFoundException` tardia).
- **Conflitos:** CF-03

### PER-LOAD-001 — EAGER indevido

- **Aplica-se quando:** JPA.
- **Verificar:** `FetchType.EAGER` explícito em coleções; associações to-one sem `fetch = LAZY` (o padrão JPA de `@ManyToOne`/`@OneToOne` é EAGER) em entidades muito usadas em listagens.
- **Evidência mínima:** E3 (mapeamento) + uso em consultas de listagem; E1 para CONFIRMED.
- **Severidade base:** MEDIUM (HIGH se gera cascata de joins/consultas em listagens grandes)
- **Falsos positivos / cuidados:** mudar EAGER → LAZY pode causar `LazyInitializationException` e N+1 em outro ponto. É mudança com plano e testes.
- **Correção preferida:** LAZY + fetch explícito nas consultas que precisam.
- **Conflitos:** CF-01, CF-06

### PER-LOAD-002 — Carregamento excessivo de colunas e linhas

- **Aplica-se quando:** sempre que há acesso a banco.
- **Verificar:** listagens/relatórios carregando entidades completas (inclusive `@Lob`, JSON grandes, coleções) para exibir poucas colunas; `listAll()` para popular combos ou contagens.
- **Evidência mínima:** E3; E1 para quantificar.
- **Severidade base:** MEDIUM (HIGH em tabelas grandes)
- **Falsos positivos / cuidados:** telas de detalhe que realmente usam a entidade completa.
- **Correção preferida:** projeção DTO (JPQL `select new`, Panache `project(...)`, SQL nativo mapeado) no Repository.
- **Conflitos:** CF-02, CF-03

### PER-LOAD-003 — Estratégia de fetch sem produto cartesiano

- **Aplica-se quando:** consultas com múltiplos fetches.
- **Verificar:** dois ou mais `JOIN FETCH` de coleções na mesma consulta (produto cartesiano, `MultipleBagFetchException` com `List`); `DISTINCT` usado para mascarar duplicação.
- **Evidência mínima:** E3; E1 com número de linhas retornadas.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** coleções pequenas e limitadas.
- **Correção preferida:** buscar coleções em consultas separadas/batch; projeções.
- **Conflitos:** CF-01, CF-03

### PER-QRY-001 — Filtros e ordenação em memória

- **Aplica-se quando:** sempre.
- **Verificar:** `listAll()`/`findAll()` seguido de `stream().filter/sorted`, filtros aplicados após carregar tudo; ordenação em Java sobre resultado completo.
- **Evidência mínima:** E3.
- **Severidade base:** HIGH em coleções potencialmente grandes; LOW em coleções estruturalmente pequenas.
- **Falsos positivos / cuidados:** filtros sobre valores calculados que o banco não consegue expressar — documente e avalie alternativa (coluna calculada, view).
- **Correção preferida:** consulta com `WHERE`/`ORDER BY` no Repository, preservando semântica (nulos, case, acentos, colação — CF-03).
- **Conflitos:** CF-03

### PER-QRY-002 — Resultado preservado em reescritas de consulta

- **Aplica-se quando:** FIX/REVIEW que altera consultas.
- **Verificar:** mesmas linhas, ordem, totais e tipos; efeitos de `JOIN` × `LEFT JOIN`, `DISTINCT`, `NOT IN` com `NULL`, colação, arredondamento de agregações.
- **Evidência mínima:** teste de caracterização comparando antes/depois com dados representativos (E2).
- **Severidade base:** CRITICAL quando envolve valores financeiros/estoque; HIGH nos demais.
- **Falsos positivos / cuidados:** —
- **Correção preferida:** teste de caracterização antes; comparação explícita no relatório de regressão.
- **Conflitos:** CF-03, CF-16

### PER-QRY-003 — Contagens caras

- **Aplica-se quando:** paginação com total.
- **Verificar:** `count` executado em toda página sobre tabelas grandes com filtros complexos; `count` derivado de consulta com fetch/joins desnecessários; contagem feita carregando a lista (`list().size()`).
- **Evidência mínima:** E3; E1 (`EXPLAIN ANALYZE` da contagem) para CONFIRMED.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** remover o total muda o contrato de paginação (CF-11).
- **Correção preferida:** consulta de contagem dedicada e enxuta; total opcional/`hasNext` somente com autorização de contrato.
- **Conflitos:** CF-11

### PER-QRY-004 — Joins e predicados custosos

- **Aplica-se quando:** PostgreSQL/SQL relacional.
- **Verificar:** subconsultas correlacionadas em listagens, `OR` entre colunas diferentes, `ILIKE '%termo%'`, funções sobre colunas filtradas, conversões implícitas de tipo, joins sem predicado seletivo.
- **Evidência mínima:** E3 (NEEDS_VERIFICATION); E1 com `EXPLAIN` (CONFIRMED).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** tabelas pequenas; o planejador pode lidar bem — só a medição decide.
- **Correção preferida:** reescrita equivalente com teste de resultado; índice adequado (PER-IDX-001).
- **Conflitos:** CF-03, CF-15
