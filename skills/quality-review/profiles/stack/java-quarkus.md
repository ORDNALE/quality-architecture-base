# Perfil de stack — Java · Quarkus · Maven · Hibernate ORM/Panache · MapStruct

Perfil de tecnologia, independente do perfil arquitetural. Define como detectar versões, quais
regras carregar e cuidados por versão. **Nunca** presuma versões: detecte e registre a fonte.

## Detecção (somente leitura)

| Item | Onde olhar | Comando de confirmação (não altera fontes) |
|---|---|---|
| JDK alvo | `maven.compiler.release`/`source`, `<release>` do `maven-compiler-plugin`, `.sdkmanrc`, `.java-version`, `.tool-versions` | `java -version`, `./mvnw -v` |
| Maven | `.mvn/wrapper/maven-wrapper.properties` (`distributionUrl`) | `./mvnw -v` |
| Quarkus | `quarkus.platform.version` / BOM `io.quarkus.platform:quarkus-bom` | `./mvnw -q help:evaluate -Dexpression=quarkus.platform.version -DforceStdout` |
| Hibernate ORM / Panache | extensões `quarkus-hibernate-orm`, `quarkus-hibernate-orm-panache` (versão gerenciada pelo BOM) | `./mvnw -q dependency:tree -Dincludes=org.hibernate.orm` |
| MapStruct | `org.mapstruct:mapstruct` + `annotationProcessorPaths` | `dependency:tree -Dincludes=org.mapstruct` |
| REST | `quarkus-rest*` (Quarkus REST) × `quarkus-resteasy*` (clássico) | — |
| Lombok | `org.projectlombok:lombok` | — |
| Banco | `quarkus-jdbc-postgresql`, `quarkus.datasource.db-kind` | — |
| Migrações | `quarkus-flyway`, `quarkus-liquibase`, `src/main/resources/db/migration` | — |
| Testes | `quarkus-junit5`, `rest-assured`, `archunit*`, Testcontainers | — |
| Análise estática | plugins `checkstyle`, `pmd`, `spotbugs`, `jacoco`, `sonar` | — |

`scripts/detect_stack.py <projeto>` extrai as versões **declaradas** desses arquivos. Versões
gerenciadas por BOM aparecem como "gerenciada" — resolva com os comandos acima (que podem baixar
dependências do repositório Maven; se não houver rede, registre `NÃO RESOLVIDA`).

## Regras a carregar

- `rules/universal/*` (sempre)
- `rules/backend/java-quarkus.md`
- `rules/backend/dto-mapstruct.md` (se expõe API REST)
- `rules/persistence/*` (se usa Hibernate/JPA)
- `rules/performance/backend-performance.md`
- `rules/testing/*`

## Cuidados por versão (confirme na documentação oficial da versão em uso)

| Tema | Observação |
|---|---|
| Quarkus 2.x × 3.x | Quarkus 3 migrou para Jakarta EE (`jakarta.*`) e Hibernate ORM 6; Quarkus 2 usa `javax.*` e Hibernate ORM 5.6. Não recomende API de uma linha na outra. |
| Nomes de extensões REST | Na linha 3.x as extensões RESTEasy Reactive foram renomeadas para "Quarkus REST" (`quarkus-rest*`). Verifique a versão exata em que o projeto está. |
| Panache paginação | `PanacheQuery` oferece `page(Page)`/`page(int,int)`, `range(int,int)`, `count()`, `pageCount()`, `hasNextPage()` e `project(Class)` para projeções DTO. `count()` sobre consultas com `fetch` pode falhar ou ser caro — use consulta de contagem dedicada. |
| Paginação + fetch de coleção | Hibernate 6: aviso `HHH90003004` e opção de falhar (`hibernate.query.fail_on_pagination_over_collection_fetch`); Hibernate 5: `HHH000104`. |
| Batch fetching | Quarkus expõe configuração de tamanho de batch fetch do Hibernate; o valor padrão e o nome da propriedade variam por versão — confira antes de afirmar que N+1 "já está resolvido". |
| Log SQL em teste | Propriedades de log SQL do Hibernate no Quarkus variam por versão (`quarkus.hibernate-orm.log.sql` em versões 3.x); use somente em perfil `%test`/`%dev`. |
| Transações | `jakarta.transaction.Transactional` faz rollback em `RuntimeException`; exceções verificadas exigem `rollbackOn`. |
| Event loop | Quarkus REST despacha conforme o tipo de retorno e anotações (`@Blocking`, `@NonBlocking`, `@RunOnVirtualThread`). |
| Virtual threads | `@RunOnVirtualThread` exige JDK com virtual threads (21+); cuidado com *pinning* em versões anteriores ao JDK 24 e com bibliotecas que usam `synchronized` em I/O. |
| MapStruct + CDI | Use o `componentModel` compatível com CDI/Jakarta da versão do MapStruct em uso; com Lombok, verifique o binding de processadores. |
| Records | Records exigem Java 16+; confirme suporte do Jackson/JSON-B da versão em uso. |

## Ferramentas de verificação típicas

```bash
./mvnw -q -DskipTests compile          # compilação
./mvnw test                            # testes unitários/@QuarkusTest
./mvnw verify                          # inclui testes de integração, se configurados
```

Use somente comandos que o projeto já suporta (veja `pom.xml`, CI, README do projeto). Dev
Services/Testcontainers exigem Docker; sem Docker, declare a limitação.
