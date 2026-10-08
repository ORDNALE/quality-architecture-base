# Resolução de conflitos entre diretrizes

Toda recomendação tem efeitos colaterais. Antes de propor ou aplicar uma correção, verifique se ela
cai em algum conflito abaixo. Achados e planos citam o conflito pelo ID (`CF-NN`).

## Procedimento obrigatório

Para cada alteração proposta, documente:

1. **Problema** e **evidência** (tipo E1–E5).
2. **Alternativas** (no mínimo a escolhida e uma descartada, com motivo).
3. **Escopo** exato.
4. **Diretrizes em conflito** (IDs abaixo).
5. **Riscos** e **verificações** que os cobrem.
6. **Critérios de aceite** mensuráveis.

Se o conflito for **irreconciliável** sem decisão de negócio ou de arquitetura: suspenda **somente** a
alteração afetada, registre em "Decisões pendentes" (`QUALITY_STATE.md`) e peça decisão humana.
As demais alterações seguem.

## Prioridade padrão

Quando nada no perfil diz o contrário, a ordem de prioridade é:

1. Correção funcional e regra de negócio (G-04)
2. Integridade de dados e transações
3. Contratos públicos (API, formatos, paginação existente)
4. Segurança existente (não enfraquecer; encaminhar)
5. Desempenho medido
6. Arquitetura desejada
7. Manutenibilidade e legibilidade
8. Preferências estéticas (nunca justificam mudança sozinhas)

Uma preferência local pode alterar a ordem entre 5–8 com justificativa no perfil. Itens 1–4 não
são rebaixados por preferência local.

## Catálogo

### CF-01 — N+1 × paginação

- **Tensão:** `JOIN FETCH` (ou `EntityGraph`) de **coleção** com `setFirstResult/setMaxResults` faz o
  Hibernate paginar **em memória** (aviso `HHH90003004` no Hibernate 6; `HHH000104` no 5), trazendo
  todas as linhas do banco.
- **Resolução preferida:** (a) projeção DTO paginada no banco; (b) duas etapas: página de IDs com
  ordenação determinística e depois busca das associações por `IN (:ids)`; (c) batch fetching
  (`@BatchSize` ou configuração global); (d) `JOIN FETCH` apenas de associações *to-one*.
- **Proibido:** propor `JOIN FETCH` de coleção como solução universal; remover a paginação para
  resolver N+1.

### CF-02 — DTO/MapStruct × contrato de resposta

- **Tensão:** trocar Entity por DTO pode mudar nomes de campos, campos nulos, formato de data/número,
  ordem de elementos, anotações Jackson/JSON-B, campos calculados e validação.
- **Resolução:** capturar o contrato atual (teste de contrato/snapshot de JSON) **antes**; DTO
  replica exatamente o contrato; diferenças intencionais exigem versão de API ou autorização.

### CF-03 — Otimização SQL × resultado

- **Tensão:** reescrever consultas pode alterar linhas (joins que duplicam, `DISTINCT`, `NULL`
  em `NOT IN`, filtros movidos de `WHERE` para `ON`), ordenação, arredondamentos e agregações.
- **Resolução:** teste de caracterização com dados representativos comparando resultado antes/depois
  (linhas, ordem, totais); conferir tipos numéricos (`numeric` × `double`).

### CF-04 — Lazy loading de frontend × desempenho percebido

- **Tensão:** dividir demais aumenta requisições e atrasa navegação; dividir de menos infla o bundle
  inicial.
- **Resolução:** medir bundle inicial e navegação; lazy por rota/funcionalidade pouco usada;
  preloading seletivo das rotas mais acessadas.

### CF-05 — Cache × consistência

- **Tensão:** cache acelera leitura, mas pode servir dado desatualizado (saldo, estoque, preço) ou
  vazar dados entre usuários/tenants.
- **Resolução:** cache só com estratégia de invalidação definida, chave inclui escopo do usuário/tenant
  quando aplicável, e nunca para dados que exigem leitura forte sem decisão explícita.

### CF-06 — Mover lógica entre camadas × transações e permissões

- **Tensão:** mover código de Resource para Service (ou entre Services) pode mudar fronteira de
  `@Transactional`, ordem de interceptores, `@RolesAllowed`/checagens, tratamento de exceção →
  status HTTP, e autoinvocação (se uma chamada interna passa ou não pelos interceptores depende
  do container e da versão — ex.: Spring com proxies não intercepta; o ArC do Quarkus documenta
  suporte a *self-interception* — confirme na documentação da versão em uso).
- **Resolução:** mapear transação e permissão antes; manter as mesmas fronteiras; testes de
  integração que exercitam rollback e acesso negado.

### CF-07 — Remoção de código "morto" × referências indiretas

- **Tensão:** classes/métodos sem referência textual podem ser usados por CDI (`@Observes`,
  `@Produces`, beans por nome), JPA (construtor sem argumentos, `@PrePersist`), Jackson/JSON-B
  (getters/setters), reflexão, `ServiceLoader`, configuração, templates (Qute), rotas, testes.
- **Resolução:** busca por nome em todo o repositório (inclusive recursos e configurações),
  verificação das anotações, compilação **e** testes; em dúvida, `NEEDS_VERIFICATION`, não remover.

### CF-08 — Padrão universal × preferência local

- **Tensão:** o projeto pode preferir algo que a base desaconselha.
- **Resolução:** a preferência vale se registrada no perfil com justificativa (seção 13), salvo
  itens 1–4 da prioridade padrão. Sem registro, aponte a divergência sem tratá-la como violação
  silenciosamente aceita.

### CF-09 — Arquitetura existente × desejada

- **Tensão:** corrigir toda a divergência de uma vez gera mudança grande e arriscada.
- **Resolução:** migração incremental por funcionalidade tocada ou plano dedicado; nunca big-bang
  dentro de um FIX; nunca impor alvo não aprovado no contrato.

### CF-10 — DRY × acoplamento

- **Tensão:** extrair código "duplicado" entre módulos/contextos pode criar acoplamento indevido,
  especialmente quando a semelhança é acidental (regras que evoluem separadamente).
- **Resolução:** deduplicar apenas conhecimento realmente único (mesma regra de negócio); manter
  duplicação acidental documentada.

### CF-11 — Paginação nova × contrato existente

- **Tensão:** adicionar paginação muda o formato da resposta e o comportamento de clientes.
- **Resolução:** preservar o contrato: parâmetros opcionais com padrão compatível, novo endpoint ou
  nova versão; limite máximo acordado; decisão humana se clientes dependem da lista completa.

### CF-12 — Ferramentas de geração × código existente

- **Tensão:** introduzir Lombok ou MapStruct indiscriminadamente muda estilo, build e depuração.
- **Resolução:** não introduzir Lombok automaticamente; MapStruct apenas onde o perfil prevê e
  onde reduz mapeamento manual real; não substituir getters/setters com semântica.

### CF-13 — Tecnologia nova/reativa × estabilidade

- **Tensão:** migrar para reativo, nova versão ou nova biblioteca nem sempre traz ganho e muda
  semântica de threads, transações e erros.
- **Resolução:** recomendar somente com ganho demonstrado e compatível com a versão em uso; nunca
  como parte de um FIX não relacionado.

### CF-14 — Abstração/memoização × simplicidade

- **Tensão:** interfaces com uma implementação, camadas de delegação pura, `useMemo` em tudo,
  padrões de projeto sem variação real.
- **Resolução:** KISS/YAGNI — abstração só com segunda implementação real, fronteira de teste
  necessária ou contrato arquitetural; memoização só com evidência de custo.

### CF-15 — Índice × custo de escrita e bloqueio

- **Tensão:** índices aceleram leitura, mas custam escrita e espaço; `CREATE INDEX` sem
  `CONCURRENTLY` bloqueia escritas na tabela no PostgreSQL.
- **Resolução:** propor índice com consulta-alvo e `EXPLAIN` antes/depois; migration criada pelo
  time e executada pelo processo normal (esta base nunca executa migration em ambiente compartilhado).

### CF-16 — Teste de caracterização × comportamento possivelmente incorreto

- **Tensão:** o teste de caracterização captura o comportamento atual, inclusive um possível bug.
- **Resolução:** preservar o comportamento no FIX; registrar a suspeita como `INFO` com decisão
  humana. Corrigir o bug é outra tarefa, autorizada à parte.
