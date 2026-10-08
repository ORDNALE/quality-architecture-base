# Regras de backend — Java e Quarkus

Sempre confirme a versão real (UNI-VER-001) antes de aplicar uma regra dependente de versão.
Detalhes de versão e comandos de detecção ficam em `profiles/stack/java-quarkus.md`.

### BCK-QRK-001 — Escopo CDI adequado e beans sem estado mutável compartilhado

- **Aplica-se quando:** Quarkus/CDI.
- **Verificar:** campos mutáveis em beans `@ApplicationScoped`/`@Singleton` usados por requisições concorrentes; `@RequestScoped` sem necessidade; `@Dependent` inesperado; injeção de bean de escopo menor em maior sem proxy.
- **Evidência mínima:** E3.
- **Severidade base:** HIGH (estado compartilhado entre requisições); LOW nos demais.
- **Falsos positivos / cuidados:** caches thread-safe intencionais; campos `final` imutáveis.
- **Correção preferida:** remover estado mutável ou usar estrutura thread-safe com justificativa.
- **Conflitos:** CF-05

### BCK-QRK-002 — Semântica de `@Transactional` compreendida

- **Aplica-se quando:** Quarkus com Narayana/JTA (`jakarta.transaction.Transactional`).
- **Verificar:** exceções verificadas (checked) não fazem rollback por padrão sem `rollbackOn`; `@Transactional` em métodos que o container não intercepta (ex.: `private`); `TxType` (`REQUIRES_NEW`, `MANDATORY`) que muda semântica; captura de exceção que impede rollback; autoinvocação (comportamento depende do container/versão — CF-06).
- **Evidência mínima:** E3; teste de integração de rollback (E2) para CONFIRMED.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** alterar a configuração de rollback muda comportamento de negócio (G-04).
- **Correção preferida:** registrar e propor; em FIX, somente com teste que demonstre o comportamento atual e autorização.
- **Conflitos:** CF-06, CF-16

### BCK-QRK-003 — Operações bloqueantes fora do event loop

- **Aplica-se quando:** Quarkus REST (RESTEasy Reactive) ou código reativo (Mutiny, Vert.x).
- **Verificar:** endpoints que retornam `Uni`/`Multi` (executados no event loop por padrão) chamando JDBC, Hibernate ORM clássico, I/O de arquivo ou clientes síncronos; `@NonBlocking` com trabalho bloqueante; avisos "Thread ... has been blocked" nos logs.
- **Evidência mínima:** E3 (PROBABLE) ou E1/E2 com aviso de bloqueio no log (CONFIRMED).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** endpoints com tipo de retorno síncrono rodam em worker thread por padrão no Quarkus REST — confirme as regras de despacho da versão em uso; `@Blocking`/`@RunOnVirtualThread` mudam o despacho.
- **Correção preferida:** retornar tipo síncrono ou anotar `@Blocking`; não migrar para Hibernate Reactive como correção de um achado (CF-13).
- **Conflitos:** CF-13

### BCK-QRK-004 — Pilha REST e clientes coerentes com a versão

- **Aplica-se quando:** Quarkus.
- **Verificar:** mistura de extensões REST clássicas e reativas (`quarkus-resteasy*` × `quarkus-rest*`) ou de clientes incompatíveis com o servidor; nomes de extensões renomeados na versão em uso (ex.: no Quarkus 3.x, `quarkus-resteasy-reactive*` passou a `quarkus-rest*` — confirmar a versão exata); namespace `javax.*` em Quarkus 3 (Jakarta EE).
- **Evidência mínima:** E3 no `pom.xml`/imports ou E2 (aviso/erro de build).
- **Severidade base:** LOW (HIGH se impede build/upgrade)
- **Falsos positivos / cuidados:** extensões relocadas continuam funcionando por um período; troca de extensão é mudança de dependência (G-07).
- **Correção preferida:** recomendar alinhamento como item de planejamento.
- **Conflitos:** CF-13

### BCK-QRK-005 — Configuração por perfil e sem valores perigosos em produção

- **Aplica-se quando:** Quarkus.
- **Verificar:** `quarkus.hibernate-orm.database.generation` (ou nome equivalente da versão) com `drop-and-create`/`update` aplicável ao perfil de produção; log SQL ligado em produção; valores de ambiente fixos no código em vez de `@ConfigProperty`/`@ConfigMapping`; segredos em `application.properties` → seção de segurança.
- **Evidência mínima:** E3 com a chave e o perfil (`%prod`, `%dev`, `%test` ou sem prefixo).
- **Severidade base:** CRITICAL para geração de esquema destrutiva em produção; LOW nos demais.
- **Falsos positivos / cuidados:** propriedade sem prefixo vale para todos os perfis, salvo sobrescrita; verifique variáveis de ambiente e arquivos externos antes de concluir.
- **Correção preferida:** restringir ao perfil `%dev`/`%test`; migrations gerenciadas (Flyway/Liquibase).
- **Conflitos:** nenhum conhecido

### BCK-QRK-006 — Exceções mapeadas centralmente

- **Aplica-se quando:** Quarkus REST/RESTEasy.
- **Verificar:** `try/catch` repetido em Resources para traduzir exceções; ausência de `ExceptionMapper`/`@ServerExceptionMapper` para exceções de domínio.
- **Evidência mínima:** E3.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** centralizar pode mudar status/corpo de erro (CF-02).
- **Correção preferida:** mapper central reproduzindo as respostas atuais.
- **Conflitos:** CF-02
