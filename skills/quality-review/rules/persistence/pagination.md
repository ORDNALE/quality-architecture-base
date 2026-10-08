# Regras de persistência — paginação e grandes volumes

Coleções potencialmente grandes (ex.: clientes, vendas, fornecedores, despesas, estoque, histórico,
relatórios detalhados) devem ser filtradas e paginadas **no banco**. Coleções pequenas com limite
estrutural conhecido (ex.: UFs, status, formas de pagamento) não exigem paginação.

### PER-PAG-001 — Coleção potencialmente grande paginada no banco

- **Aplica-se quando:** endpoints/consultas que listam entidades sem limite estrutural.
- **Verificar:** `listAll()`, `findAll().list()`, `getResultList()` sem `setMaxResults`/`page`/`range`/`LIMIT` em listagens expostas a usuários ou integrações.
- **Evidência mínima:** E3 + justificativa de crescimento (volume atual medido ou natureza do dado).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** coleções com limite estrutural documentado no perfil (§8); endpoints internos com limite garantido por filtro obrigatório.
- **Correção preferida:** paginação no Repository (Panache `page(...)`/`range(...)`, JPQL `setFirstResult/setMaxResults`, SQL `LIMIT/OFFSET` ou keyset) preservando o contrato (CF-11).
- **Conflitos:** CF-11, CF-01

### PER-PAG-002 — Paginação ou filtro aplicados em memória

- **Aplica-se quando:** sempre.
- **Verificar:** `subList`, `stream().skip().limit()`, paginação no frontend sobre lista completa, filtros aplicados após carregar tudo.
- **Evidência mínima:** E3.
- **Severidade base:** HIGH em coleções grandes.
- **Falsos positivos / cuidados:** o mesmo efeito ocorre, sem estar no código, quando o Hibernate pagina em memória por causa de fetch de coleção (PER-PAG-007).
- **Correção preferida:** mover paginação e filtros para a consulta.
- **Conflitos:** CF-01, CF-03

### PER-PAG-003 — Ordenação determinística

- **Aplica-se quando:** qualquer consulta paginada.
- **Verificar:** paginação sem `ORDER BY`, ou ordenada por coluna não única sem desempate (registros repetidos/omitidos entre páginas).
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** acrescentar desempate (ex.: `, id`) pode mudar a ordem visível de empates — normalmente aceitável, mas registre.
- **Correção preferida:** ordenação explícita com chave única como último critério.
- **Conflitos:** CF-03

### PER-PAG-004 — Limites de tamanho de página

- **Aplica-se quando:** API recebe tamanho de página do cliente.
- **Verificar:** ausência de tamanho máximo; tamanho padrão inexistente ou muito alto; parâmetros negativos aceitos.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** impor máximo muda o contrato para clientes que pedem páginas grandes — confirme com o time (CF-11).
- **Correção preferida:** padrão e máximo definidos no perfil; validação de entrada.
- **Conflitos:** CF-11

### PER-PAG-005 — Resposta paginada consistente

- **Aplica-se quando:** API paginada.
- **Verificar:** formatos de resposta paginada diferentes entre endpoints; metadados ausentes ou incoerentes (total × itens); numeração de página inconsistente (0 × 1).
- **Evidência mínima:** E3.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** unificar formatos muda contratos existentes — só para endpoints novos ou com autorização.
- **Correção preferida:** formato padrão no perfil para novos endpoints.
- **Conflitos:** CF-11

### PER-PAG-006 — Keyset pagination quando offsets profundos se justificam

- **Aplica-se quando:** listas com navegação profunda medida ou esperada (rolagem infinita, exportações, integrações que percorrem tudo).
- **Verificar:** `OFFSET` alto em tabelas grandes com custo crescente (`EXPLAIN ANALYZE` em páginas profundas).
- **Evidência mínima:** E1 para recomendar mudança; sem medição, apenas `INFO`.
- **Severidade base:** INFO (MEDIUM com medição)
- **Falsos positivos / cuidados:** keyset impede saltar para página N e muda o contrato; não é padrão universal.
- **Correção preferida:** keyset por `(coluna_ordenação, id)` com índice correspondente, em endpoint/versão nova ou com autorização.
- **Conflitos:** CF-11, CF-15

### PER-PAG-007 — Paginação com fetch de coleção

- **Aplica-se quando:** Hibernate/JPA.
- **Verificar:** `JOIN FETCH`/`EntityGraph` de coleção combinado com paginação; aviso de paginação em memória no log (`HHH90003004` no Hibernate 6, `HHH000104` no Hibernate 5).
- **Evidência mínima:** E3 (PROBABLE) ou aviso no log (CONFIRMED).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** o Hibernate 6 oferece configuração para falhar nesse caso (`hibernate.query.fail_on_pagination_over_collection_fetch`); verifique se está ativa e o nome da propriedade na versão em uso.
- **Correção preferida:** duas etapas (página de IDs + busca das coleções), projeção DTO ou batch fetching (CF-01).
- **Conflitos:** CF-01

### PER-PAG-008 — Exportações e relatórios grandes processados em fluxo

- **Aplica-se quando:** exportações, relatórios detalhados, jobs que percorrem tabelas.
- **Verificar:** carregamento de todo o resultado em memória (lista + montagem de arquivo); transação única gigante.
- **Evidência mínima:** E3; E1 (memória/tempo) para CONFIRMED.
- **Severidade base:** HIGH em volumes grandes.
- **Falsos positivos / cuidados:** streaming mantém conexão/transação abertas — avalie timeout e bloqueios.
- **Correção preferida:** processamento em lotes (keyset), `Stream`/`ScrollableResults` com `clear()` periódico, ou geração assíncrona — conforme a versão e o contrato.
- **Conflitos:** CF-03, CF-11
