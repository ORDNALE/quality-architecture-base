# Regras de persistência — índices e planos de execução

Achados de índice são hipóteses até haver `EXPLAIN` em ambiente adequado: o índice pode existir só
no banco (criado fora das migrations), e o planejador depende de volume e estatísticas.

### PER-IDX-001 — Índice potencialmente ausente

- **Aplica-se quando:** PostgreSQL (ou relacional) com migrations ou esquema disponível.
- **Verificar:** colunas usadas em filtros frequentes, joins e ordenação de listagens sem índice nas migrations; chaves estrangeiras sem índice (o PostgreSQL **não** cria índice automaticamente para FKs).
- **Evidência mínima:** E3 (migrations + consulta) → NEEDS_VERIFICATION; E1 (`EXPLAIN` mostrando `Seq Scan` custoso em volume representativo) → CONFIRMED.
- **Severidade base:** MEDIUM (HIGH se em listagem principal com volume grande medido)
- **Falsos positivos / cuidados:** tabelas pequenas; índice existente com outra ordem de colunas; índice parcial/expressão que já cobre.
- **Correção preferida:** propor índice específico com consulta-alvo e plano antes/depois; criação via migration do time (CF-15).
- **Conflitos:** CF-15

### PER-IDX-002 — Verificação com EXPLAIN em ambiente adequado

- **Aplica-se quando:** qualquer afirmação sobre plano de execução.
- **Verificar:** uso de `EXPLAIN` (estimativa) × `EXPLAIN (ANALYZE, BUFFERS)` (executa a consulta); volume e estatísticas (`ANALYZE`) representativos; parâmetros reais.
- **Evidência mínima:** plano registrado com ambiente e volume (E1).
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** G-12 — `ANALYZE` executa a consulta; DML só dentro de transação com `ROLLBACK`; nunca produção sem autorização.
- **Correção preferida:** banco local/teste/Dev Services com massa de dados representativa.
- **Conflitos:** nenhum conhecido

### PER-IDX-003 — Predicados que impedem uso de índice

- **Aplica-se quando:** PostgreSQL.
- **Verificar:** funções sobre colunas (`lower(col) = ?` sem índice de expressão), `LIKE '%x'`/`ILIKE` sem índice apropriado (ex.: trigram via extensão `pg_trgm`), conversões implícitas de tipo, comparação de `timestamp` com função de data.
- **Evidência mínima:** E3 (NEEDS_VERIFICATION) ou E1.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** instalar extensão é mudança de infraestrutura (G-07).
- **Correção preferida:** reescrita equivalente ou índice de expressão, com teste de resultado (CF-03).
- **Conflitos:** CF-03, CF-15

### PER-IDX-004 — Migrations de índice seguras

- **Aplica-se quando:** proposta de criação de índice em tabela com escrita contínua.
- **Verificar:** `CREATE INDEX` sem `CONCURRENTLY` em tabela grande em produção (bloqueia escritas); `CONCURRENTLY` não pode rodar dentro de transação — verificar como a ferramenta de migração (Flyway/Liquibase) executa essa instrução na versão em uso.
- **Evidência mínima:** E3 (migration).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** esta base nunca executa migrations em ambiente compartilhado (G-01).
- **Correção preferida:** migration separada, não transacional quando necessário, executada pelo processo normal do time.
- **Conflitos:** CF-15
