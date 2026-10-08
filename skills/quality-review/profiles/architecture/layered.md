# Perfil arquitetural — camadas (layered)

## Quando selecionar

Somente quando a arquitetura **desejada** (decisão humana registrada no `PROJECT_PROFILE.md`) for
camadas. O fato de o código atual estar organizado em `resource/service/repository` é indício da
arquitetura existente, não decisão.

## Contrato lógico

```text
Resource / Controller → Service → Repository → Persistence / Entity → Database
          ↑ Request/Response DTO        ↑ Mapper (MapStruct ou manual, conforme perfil)
```

| Unidade | Responsabilidade | Não deve |
|---|---|---|
| Resource / Controller | contrato HTTP, DTOs de request, validação de entrada, delegação ao Service, DTOs de response | consultar banco/`EntityManager`; concentrar regra de negócio; expor Entity |
| Service | regras de negócio, orquestração, transações quando necessárias | concentrar SQL/JPQL; lidar com detalhes HTTP |
| Repository | persistência, consultas, filtros, ordenação, paginação, estratégia de carregamento | conter regra de negócio que não seja critério de consulta |
| Entity | mapeamento JPA e invariantes próprios | depender de Service/Repository/HTTP; servir de contrato de API; Active Record quando o perfil exige Repository |
| DTO | formato dos contratos externos | depender de Entity |
| Mapper | conversão Entity ↔ DTO | conter regra de negócio ou disparar carregamentos ocultos (ver BCK-MAP-003) |

## Identificação no código (heurísticas — confirme com o time)

| Unidade | Sinais |
|---|---|
| Resource | `@Path`, `@GET/@POST...`, `@RestController`, sufixo `Resource`/`Controller`, pacote `resource`/`api`/`rest`/`controller` |
| Service | `@ApplicationScoped`/`@Service` com regras, sufixo `Service`, pacote `service` |
| Repository | `implements PanacheRepository*`, `@Repository`, sufixo `Repository`, uso de `EntityManager` |
| Entity | `@Entity`, `@Table`, `extends PanacheEntity*` |
| DTO | sufixos `Request`, `Response`, `DTO`/`Dto`, `record` em pacote `dto` |
| Mapper | `@Mapper` (MapStruct), sufixo `Mapper` |

`scripts/arch_signals.py` produz estes sinais automaticamente (E4).

## Regras ativadas

- `rules/architecture/general.md` (sempre)
- `rules/architecture/layered.md`
- `rules/backend/dto-mapstruct.md`
- Persistência, performance, testes e universais conforme perfis de stack.

## Parâmetros configuráveis (no `PROJECT_PROFILE.md` / contrato)

| Parâmetro | Padrão | Alternativas |
|---|---|---|
| Repository Pattern obrigatório (ARC-LAY-004) | sim | não (Active Record aceito) |
| Service obrigatório mesmo sem regra | não (ARC-GEN-004) | sim, por consistência |
| Resource pode usar Mapper | sim | não (Service devolve DTO) |
| Repository pode devolver projeção DTO | sim | não |
| Fronteira transacional | Service | outra, com justificativa |

## Verificação automatizada

Modelo ArchUnit: `templates/archunit/LayeredArchitectureTest.java.template`. Copiar para o projeto é
uma alteração de testes — só em FIX autorizado ou feita pelo time.

## Fora do escopo deste perfil

- Converter para hexagonal/Clean Architecture (ARC-GEN-002).
- Criar camadas vazias para "completar" o desenho (ARC-GEN-004).
