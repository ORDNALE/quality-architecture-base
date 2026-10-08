# PROJECT_PROFILE — vendas-sample (EXEMPLO)

> Perfil de exemplo, preenchido manualmente para ilustrar o template. Não representa um sistema real.

- **Versão do perfil:** 1
- **Última revisão humana:** 2026-10-08, mantenedores da quality-architecture-base (exemplo)
- **Versão da quality-review usada:** 0.1.0

## 1. Identificação

| Campo | Valor |
|---|---|
| Nome | vendas-sample |
| Repositório | `examples/quarkus-layered-sample` (dentro da base) |
| Domínio de negócio | vendas simplificadas (exemplo) |
| Responsável técnico | — |
| Criticidade | média (valores monetários) |

## 2. Stack e versões reais

| Tecnologia | Versão | Fonte (arquivo:linha ou comando) |
|---|---|---|
| Linguagem / JDK | 21 (release) | `pom.xml:16` |
| Build (Maven/Gradle, wrapper) | Maven 3.9.9 (wrapper) | `.mvn/wrapper/maven-wrapper.properties:1` |
| Framework (Quarkus/...) | Quarkus 3.15.1 | `pom.xml:20` |
| ORM (Hibernate ORM / Panache) | gerenciada pelo BOM — NÃO RESOLVIDA | `pom.xml:43` |
| Mapper (MapStruct) | 1.6.2 | `pom.xml:59` |
| REST (Quarkus REST / RESTEasy Classic / ...) | Quarkus REST + Jackson | `pom.xml:39` |
| Banco (PostgreSQL) | 16 | `docker-compose.yml:3`, `application.properties:2` |
| Migrações (Flyway / Liquibase) | Flyway (versão do BOM) | `pom.xml:55` |
| Frontend (Angular / React) | não há | — |
| TypeScript | não há | — |
| Node.js / gerenciador de pacotes | não há | — |

## 3. Arquitetura

| Campo | Valor |
|---|---|
| Arquitetura **existente** (observada) | camadas (resource/service/repository/entity/dto/mapper), com desvio em `ClienteResource` |
| Arquitetura **desejada** (decisão humana) | layered |
| Perfil arquitetural selecionado | `profiles/architecture/layered.md` |
| Perfis de stack selecionados | `profiles/stack/java-quarkus.md`, `profiles/stack/postgresql.md` |
| Contrato arquitetural | pendente (usar a matriz padrão do template) |
| Plano de migração entre existente e desejada | incremental por funcionalidade tocada |

## 4. Padrões obrigatórios

- [x] Repository Pattern (sem Active Record) — `ARC-LAY-004`
- [x] Request/Response DTO separados; nenhuma Entity em contrato HTTP — `BCK-DTO-001`
- [x] MapStruct para mapeamentos não triviais — `BCK-MAP-001`
- [x] Paginação no banco para coleções potencialmente grandes — `PER-PAG-001`

## 5. Regras opcionais habilitadas / desabilitadas

| Regra ou grupo | Situação | Justificativa |
|---|---|---|
| `FE-COM-*`, `FE-NG-*`, `FE-RX-*`, `FE-TS-*` | desabilitado | projeto sem frontend |

## 6. Política de DTOs e MapStruct

- DTOs de entrada: records com sufixo `Request` e Bean Validation.
- DTOs de saída: records com sufixo `Response`; nunca Entity.
- MapStruct: 1.6.2, `componentModel = "jakarta-cdi"`.
- Lombok: não usado.
- Mapeamento manual permitido quando: conversões de até 3 campos.

## 7. Política de persistência

- Padrão: `PanacheRepository<T>`.
- Carregamento: LAZY em todas as associações; fetch explícito por consulta.
- Projeções: preferidas para listagens.
- SQL nativo: permitido em repositórios com justificativa.
- Transações: `@Transactional` somente em Service.

## 8. Paginação

- Padrão de API: `pagina`/`tamanho` (base 0).
- Tamanho padrão e máximo: 20 / 100.
- Ordenação determinística obrigatória: sim; desempate por `id`.
- Formato de resposta paginada: lista simples (contrato atual; não alterar sem autorização).
- Keyset pagination: não aplicável.
- Coleções isentas (limite estrutural conhecido): nenhuma.

## 9. Testes e ferramentas disponíveis

| Tipo | Existe? | Comando real | Observação |
|---|---|---|---|
| Compilação backend | sim (não executado nesta base) | `./mvnw -q -DskipTests compile` | o wrapper não está incluído no exemplo |
| Testes unitários | não | — | |
| Testes de integração (PostgreSQL/Dev Services/Testcontainers) | não | — | |
| ArchUnit | não | — | modelo disponível na base |
| Log SQL / contagem de consultas | parcial | `%dev.quarkus.hibernate-orm.log.sql=true` | |

## 10. Exceções justificadas

| ID | Regra afetada | Escopo (arquivos/pacotes) | Justificativa | Aprovado por | Data | Revisar em |
|---|---|---|---|---|---|---|
| — | | | | | | |

## 11. Restrições

- Exemplo didático: nenhuma restrição adicional.
- Questões de segurança: encaminhar ao processo de segurança especializado.

## 12. Modo de operação

| Campo | Valor |
|---|---|
| Modos permitidos | INIT, AUDIT, REVIEW, FIX |
| Saída dos relatórios | arquivos em `.quality/` |
| Diretório de qualidade | `.quality/` |
| FIX exige | plano com autorização (`fix_gate.py`) + baseline |
| Comandos proibidos adicionais | nenhum |

## 13. Conflitos entre padrão universal e preferência local

| Padrão universal | Preferência local | Prioridade adotada | Justificativa |
|---|---|---|---|
| — | | | |
