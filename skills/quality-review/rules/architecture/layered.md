# Regras de arquitetura — camadas (layered)

Aplicam-se **somente** quando o perfil seleciona `profiles/architecture/layered.md`. Contrato lógico:

```text
Resource / Controller → Service → Repository → Persistence / Entity → Database
```

DTOs e Mappers atravessam as fronteiras conforme a matriz do `ARCHITECTURE_CONTRACT.md`. As regras
de DTO/MapStruct ficam em `rules/backend/dto-mapstruct.md`.

### ARC-LAY-001 — Resource não acessa Repository

- **Aplica-se quando:** perfil layered.
- **Verificar:** Resource/Controller injeta ou chama Repository (inclusive `PanacheRepository`) diretamente.
- **Evidência mínima:** E3 (`@Inject` + chamada) ou E2 (ArchUnit).
- **Severidade base:** MEDIUM (HIGH se a chamada contorna regra de negócio, validação ou transação existentes no Service)
- **Falsos positivos / cuidados:** exceção registrada (ex.: health-check); testes.
- **Correção preferida:** delegar ao Service existente do mesmo caso de uso; criar Service só se houver regra/transação/orquestração ou se o perfil exigir consistência (ver ARC-GEN-004).
- **Conflitos:** CF-06, CF-14

### ARC-LAY-002 — Resource não acessa EntityManager, SQL ou API de persistência

- **Aplica-se quando:** perfil layered.
- **Verificar:** `EntityManager`, `Session`, `DataSource`, JDBC, JPQL/SQL, métodos estáticos de `PanacheEntity` (`find`, `list`, `persist`) dentro de Resource.
- **Evidência mínima:** E3 ou E2.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** nenhum comum.
- **Correção preferida:** mover a consulta para o Repository e a orquestração para o Service, preservando transação e permissões.
- **Conflitos:** CF-06

### ARC-LAY-003 — Resource sem regra de negócio

- **Aplica-se quando:** perfil layered.
- **Verificar:** cálculos, decisões de estado, validações de negócio (além de validação de formato/entrada), laços de orquestração em Resource.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** validação de entrada (Bean Validation, formato, obrigatoriedade) e montagem de resposta HTTP pertencem ao Resource.
- **Correção preferida:** mover para o Service com testes de caracterização (UNI-BRP-002).
- **Conflitos:** CF-06, CF-16

### ARC-LAY-004 — Repository Pattern em vez de Active Record

- **Aplica-se quando:** perfil layered **e** o perfil do projeto exige Repository Pattern.
- **Verificar:** entidades que estendem `PanacheEntity`/`PanacheEntityBase` e são consultadas/persistidas por métodos estáticos da própria entidade.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** projetos que adotaram Active Record conscientemente (registrado no perfil) — então não é achado. Migração de Active Record para Repository é mudança ampla: incremental (CF-09).
- **Correção preferida:** `PanacheRepository<T>`/`PanacheRepositoryBase<T, ID>` por agregado; migrar por funcionalidade tocada.
- **Conflitos:** CF-09

### ARC-LAY-005 — Service sem SQL e sem detalhes HTTP

- **Aplica-se quando:** perfil layered.
- **Verificar:** JPQL/SQL/Criteria montados no Service; `EntityManager` no Service; uso de `Response`, `WebApplicationException` com status, `UriInfo`, headers ou `@Context` no Service.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** exceções de domínio mapeadas para HTTP por `ExceptionMapper` são o padrão desejado; chamadas a métodos de consulta do Repository com parâmetros são corretas.
- **Correção preferida:** consultas para o Repository; exceções de domínio + `ExceptionMapper`.
- **Conflitos:** CF-02, CF-06

### ARC-LAY-006 — Repository concentra persistência, sem regra de negócio

- **Aplica-se quando:** perfil layered.
- **Verificar:** filtros, ordenação, paginação e estratégia de carregamento definidos fora do Repository (ex.: Service filtrando lista completa em memória); regras de negócio dentro do Repository.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM (HIGH se envolve coleção grande — ver PER-PAG-002)
- **Falsos positivos / cuidados:** regras de negócio expressas como critério de consulta (ex.: "vendas não canceladas") são aceitáveis no Repository quando nomeadas claramente.
- **Correção preferida:** método de consulta dedicado no Repository.
- **Conflitos:** CF-01, CF-03

### ARC-LAY-007 — Entity restrita a mapeamento e invariantes próprios

- **Aplica-se quando:** perfil layered.
- **Verificar:** Entity com dependências de Service/Repository/HTTP/DTO, anotações de serialização de API (`@JsonIgnore`, `@JsonProperty`) usadas porque a Entity é exposta, lógica que acessa outras partes do sistema.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** métodos que protegem invariantes da própria entidade (ex.: `cancelar()` que valida estado) são compatíveis com o modelo.
- **Correção preferida:** mover serialização para DTOs; manter invariantes na entidade.
- **Conflitos:** CF-02

### ARC-LAY-008 — Fronteira transacional no Service

- **Aplica-se quando:** perfil layered.
- **Verificar:** `@Transactional` em Resource; operações de escrita sem transação; transações abertas em Resource abrangendo chamadas externas; transações que incluem I/O remoto longo.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM (HIGH se escrita sem transação ou com risco de estado parcial)
- **Falsos positivos / cuidados:** mover `@Transactional` muda semântica (CF-06) — exige testes de rollback.
- **Correção preferida:** transação no método de Service do caso de uso.
- **Conflitos:** CF-06

### ARC-LAY-009 — Dependências apenas para baixo

- **Aplica-se quando:** perfil layered.
- **Verificar:** Repository → Service, Service → Resource, Entity → Service/Repository, DTO → Entity (DTO dependendo de Entity no construtor), qualquer camada → Resource.
- **Evidência mínima:** E2 (ArchUnit `layeredArchitecture()`) ou E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** Mapper conhece Entity e DTO por definição; Repository pode retornar projeções DTO se o contrato permitir.
- **Correção preferida:** inverter a dependência movendo o código para a camada certa.
- **Conflitos:** CF-14
