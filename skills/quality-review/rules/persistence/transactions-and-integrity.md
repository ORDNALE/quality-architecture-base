# Regras de persistência — transações e integridade

### PER-TX-001 — Transações longas

- **Aplica-se quando:** sempre que há transações.
- **Verificar:** chamadas HTTP/remotas, envio de e-mail, processamento pesado ou espera de usuário dentro de transação; laços longos numa única transação.
- **Evidência mínima:** E3; E1 (tempo de transação, bloqueios em `pg_stat_activity` em ambiente adequado) para CONFIRMED.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** dividir a transação muda atomicidade — regra de negócio (G-04).
- **Correção preferida:** mover I/O externo para fora da transação mantendo consistência (ex.: outbox) **somente** com decisão humana; em FIX simples, apenas registrar.
- **Conflitos:** CF-06

### PER-TX-002 — Acesso a associações fora da transação

- **Aplica-se quando:** JPA/Hibernate.
- **Verificar:** `LazyInitializationException` em logs/testes; mapeamento/serialização de associações após o término do método transacional.
- **Evidência mínima:** E2/E1 (exceção) ou E3.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** "corrigir" com EAGER ou abrindo transações maiores costuma piorar desempenho.
- **Correção preferida:** buscar o necessário no Repository (fetch planejado/projeção) dentro da transação.
- **Conflitos:** CF-01, CF-06

### PER-TX-003 — Concorrência em dados críticos

- **Aplica-se quando:** saldo, estoque, numeração sequencial, status de pedidos, reservas.
- **Verificar:** leitura-modificação-escrita sem `@Version` (locking otimista), sem lock pessimista ou sem operação atômica no banco; verificação de unicidade apenas na aplicação.
- **Evidência mínima:** E3 (PROBABLE); teste concorrente reproduzindo perda de atualização (CONFIRMED).
- **Severidade base:** CRITICAL quando envolve dinheiro/estoque.
- **Falsos positivos / cuidados:** a correção altera comportamento sob concorrência (novas exceções/retries) — regra de negócio, exige decisão humana.
- **Correção preferida:** registrar e propor alternativas (versão otimista, `SELECT ... FOR UPDATE`, atualização atômica, constraint única).
- **Conflitos:** CF-06, CF-16

### PER-TX-004 — Escritas em massa eficientes

- **Aplica-se quando:** importações, processamentos em lote.
- **Verificar:** `persist` em laço sem batching JDBC configurado; contexto de persistência crescendo sem `flush()/clear()`; geração de IDs que impede batching (ex.: `IDENTITY` no Hibernate).
- **Evidência mínima:** E3; E1 (número de statements/tempo) para CONFIRMED.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** nomes de propriedades de batch variam por versão (Quarkus/Hibernate) — confirme na documentação da versão; mudar estratégia de ID é mudança de esquema.
- **Correção preferida:** batching configurado + `flush/clear` periódico; operações em massa via JPQL/SQL quando a semântica (callbacks, auditoria) permitir.
- **Conflitos:** CF-03
