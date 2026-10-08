# Perfil de stack — PostgreSQL

## Detecção

| Item | Onde olhar |
|---|---|
| Versão do servidor | imagem em `docker-compose*.yml` (`postgres:16`), `quarkus.datasource.db-version`, documentação de infraestrutura (E5), `SELECT version();` em ambiente adequado |
| Driver | `quarkus-jdbc-postgresql`, `org.postgresql:postgresql` |
| Migrações | Flyway (`db/migration/V*.sql`), Liquibase (`changelog`) |
| Extensões | `CREATE EXTENSION` nas migrations |

## Regras a carregar

- `rules/persistence/query-efficiency.md`
- `rules/persistence/pagination.md`
- `rules/persistence/indexes-and-plans.md`
- `rules/persistence/transactions-and-integrity.md`

## Verificação de consultas (ambiente adequado — G-12)

```sql
-- Estimativa, não executa:
EXPLAIN SELECT ...;

-- Executa a consulta (SELECT):
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- DML: somente dentro de transação descartada
BEGIN;
EXPLAIN (ANALYZE, BUFFERS) UPDATE ...;
ROLLBACK;
```

Registre: versão do PostgreSQL, volume aproximado das tabelas envolvidas, se as estatísticas
estavam atualizadas (`ANALYZE`), parâmetros usados e o plano completo.

## Cuidados

- FKs não ganham índice automaticamente.
- `CREATE INDEX` comum bloqueia escritas; `CREATE INDEX CONCURRENTLY` não roda dentro de transação.
- `numeric` preserva precisão; mapear para `double` no Java altera resultados.
- `OFFSET` grande lê e descarta linhas; keyset exige índice compatível com a ordenação.
- `count(*)` exato em tabelas grandes é caro; estimativas (`pg_class.reltuples`) mudam o contrato.
- Colação e `ILIKE`/`unaccent` afetam filtros de texto — reescritas precisam de teste de resultado.
