# PROJECT_PROFILE — <nome do projeto>

> Perfil individual do projeto consumidor. Fica em `.quality/PROJECT_PROFILE.md` **no próprio
> projeto**, nunca na base de regras. Gerado pelo modo INIT e revisado por uma pessoa responsável.
> Campos marcados com `DESCONHECIDO` bloqueiam as verificações que dependem deles.

- **Versão do perfil:** 1
- **Última revisão humana:** <AAAA-MM-DD, nome>  <!-- vazio = ainda não revisado -->
- **Versão da quality-review usada:** <ex.: 0.1.0>

## 1. Identificação

| Campo | Valor |
|---|---|
| Nome | |
| Repositório | |
| Domínio de negócio | <ex.: ERP de distribuição de bebidas> |
| Responsável técnico | |
| Criticidade | <baixa / média / alta — dados financeiros? estoque? fiscais?> |

## 2. Stack e versões reais

> Versões **efetivamente configuradas**, com a fonte de cada uma. "Gerenciada pelo BOM" não é
> versão; registre a versão resolvida (ex.: via `mvn help:effective-pom`) ou `NÃO RESOLVIDA`.

| Tecnologia | Versão | Fonte (arquivo:linha ou comando) |
|---|---|---|
| Linguagem / JDK | | |
| Build (Maven/Gradle, wrapper) | | |
| Framework (Quarkus/...) | | |
| ORM (Hibernate ORM / Panache) | | |
| Mapper (MapStruct) | | |
| REST (Quarkus REST / RESTEasy Classic / ...) | | |
| Banco (PostgreSQL) | | |
| Migrações (Flyway / Liquibase) | | |
| Frontend (Angular / React) | | |
| TypeScript | | |
| Node.js / gerenciador de pacotes | | |

## 3. Arquitetura

| Campo | Valor |
|---|---|
| Arquitetura **existente** (observada) | <camadas / hexagonal / modular / mista / desconhecida> + evidência |
| Arquitetura **desejada** (decisão humana) | <layered / hexagonal / modular / custom / DESCONHECIDO> |
| Perfil arquitetural selecionado | <`profiles/architecture/layered.md` / ... / nenhum> |
| Perfis de stack selecionados | <`profiles/stack/java-quarkus.md`, `profiles/stack/postgresql.md`, ...> |
| Contrato arquitetural | `.quality/ARCHITECTURE_CONTRACT.md` <existe / pendente> |
| Plano de migração entre existente e desejada | <não há / link> |

> Se a arquitetura desejada for `DESCONHECIDO`, regras `ARC-LAY-*`, `ARC-HEX-*` e `ARC-MOD-*` **não**
> são aplicadas; somente `ARC-GEN-*` e as demais áreas. Ver `profiles/architecture/custom.md`.

## 4. Padrões obrigatórios

<!-- Lista do que este projeto exige. Cada item idealmente referencia uma regra. -->

- [ ] Repository Pattern (sem Active Record) — `ARC-LAY-004`
- [ ] Request/Response DTO separados; nenhuma Entity em contrato HTTP — `BCK-DTO-001`
- [ ] MapStruct para mapeamentos não triviais — `BCK-MAP-001`
- [ ] Paginação no banco para coleções potencialmente grandes — `PER-PAG-001`
- [ ] <outros>

## 5. Regras opcionais habilitadas / desabilitadas

| Regra ou grupo | Situação | Justificativa |
|---|---|---|
| `FE-COM-*` | desabilitado | projeto sem frontend |
| | | |

## 6. Política de DTOs e MapStruct

- DTOs de entrada: <records Java / classes; sufixo `Request`; validação com Bean Validation>
- DTOs de saída: <sufixo `Response`; nunca Entity>
- MapStruct: <versão; `componentModel = "cdi"` ou `"jakarta-cdi"`; `unmappedTargetPolicy`>
- Lombok: <não usado / usado em ... — a base nunca introduz Lombok automaticamente>
- Mapeamento manual permitido quando: <ex.: conversões triviais de 1–3 campos>

## 7. Política de persistência

- Padrão: <Repository (`PanacheRepository<T>`) / EntityManager em repositórios / outro>
- Carregamento: <LAZY por padrão em `@ManyToOne`/`@OneToMany`? batch-size configurado?>
- Projeções: <DTO projections permitidas / preferidas para listagens>
- SQL nativo: <permitido em repositórios com justificativa>
- Transações: <`@Transactional` somente em Service / outro>

## 8. Paginação

- Padrão de API: <`page`/`size` / `offset`/`limit` / cursor>
- Tamanho padrão e máximo: <ex.: 20 / 100>
- Ordenação determinística obrigatória: <sim; desempate por `id`>
- Formato de resposta paginada: <ex.: `{ items, page, size, totalItems }` — não alterar sem autorização>
- Keyset pagination: <onde se aplica / não aplicável>
- Coleções isentas (limite estrutural conhecido): <ex.: UFs, formas de pagamento>

## 9. Testes e ferramentas disponíveis

| Tipo | Existe? | Comando real | Observação |
|---|---|---|---|
| Compilação backend | | <ex.: `./mvnw -q compile`> | |
| Testes unitários | | | |
| Testes de integração (PostgreSQL/Dev Services/Testcontainers) | | | |
| Testes de contrato/API | | | |
| ArchUnit | | | |
| Checkstyle / PMD / SpotBugs / Sonar | | | |
| Compilação frontend / ESLint | | | |
| Testes frontend / E2E | | | |
| Log SQL / contagem de consultas | | <ex.: `quarkus.hibernate-orm.log.sql=true` em perfil de teste> | |
| Banco para EXPLAIN | | <ambiente adequado; nunca produção sem autorização> | |

## 10. Exceções justificadas

> Exceções sem justificativa, responsável e data são inválidas. Não há exceções silenciosas.

| ID | Regra afetada | Escopo (arquivos/pacotes) | Justificativa | Aprovado por | Data | Revisar em |
|---|---|---|---|---|---|---|
| EXC-001 | | | | | | |

## 11. Restrições

- <ex.: não alterar contratos públicos da API v1>
- <ex.: não mudar versão do Quarkus nesta fase>
- <ex.: módulo `fiscal` congelado — somente leitura>
- Questões de segurança: encaminhar ao agente/processo de segurança especializado.

## 12. Modo de operação

| Campo | Valor |
|---|---|
| Modos permitidos | <INIT, AUDIT, REVIEW, FIX> |
| Saída dos relatórios | <arquivos em `.quality/` / somente conversa> |
| Diretório de qualidade | `.quality/` |
| FIX exige | plano com autorização (`fix_gate.py`) + baseline |
| Comandos proibidos adicionais | <ex.: nenhum acesso ao banco de homologação> |

## 13. Conflitos entre padrão universal e preferência local

| Padrão universal | Preferência local | Prioridade adotada | Justificativa |
|---|---|---|---|
| | | | |
