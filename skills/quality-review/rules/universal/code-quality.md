# Regras universais — qualidade de código

Independentes de stack. SOLID, DRY, KISS e YAGNI são aplicados com pragmatismo: o objetivo é
reduzir custo real de manutenção e risco, não produzir código "mais bonito". Refatoração meramente
estética não gera achado acima de `INFO`.

### UNI-QUA-001 — Responsabilidade única e coesão

- **Aplica-se quando:** sempre.
- **Verificar:** classes/módulos que misturam motivos de mudança independentes (ex.: HTTP + regra de negócio + SQL; componente de UI que também orquestra várias APIs e regras); métodos que fazem várias coisas em níveis de abstração diferentes.
- **Evidência mínima:** E3 apontando as responsabilidades distintas e as linhas de cada uma.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** classes de orquestração legítimas (Service de caso de uso) coordenam várias dependências sem violar SRP; tamanho sozinho não é evidência.
- **Correção preferida:** extrair a responsabilidade para a unidade prevista no contrato arquitetural; não criar classes novas sem destino arquitetural claro.
- **Conflitos:** CF-06, CF-14

### UNI-QUA-002 — Acoplamento excessivo

- **Aplica-se quando:** sempre.
- **Verificar:** dependência de detalhes concretos de outra unidade (campos internos, tipos de infraestrutura atravessando camadas), cadeias longas `a.getB().getC().getD()`, conhecimento de formato de persistência fora da persistência.
- **Evidência mínima:** E3 com os pontos de acoplamento.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** navegação de agregados dentro do mesmo modelo é aceitável; o problema é o acoplamento entre unidades que deveriam evoluir separadamente.
- **Correção preferida:** depender do contrato da unidade (método de serviço, DTO, porta) em vez do detalhe.
- **Conflitos:** CF-10

### UNI-QUA-003 — Dependências cíclicas

- **Aplica-se quando:** sempre (pacotes, módulos, serviços CDI, módulos de frontend).
- **Verificar:** ciclos entre pacotes/módulos/beans; injeções mútuas entre Services.
- **Evidência mínima:** E2 (ArchUnit `slices().should().beFreeOfCycles()`, madge, dependency-cruiser) ou E3 com o ciclo completo listado.
- **Severidade base:** MEDIUM (HIGH se impede inicialização/teste ou cruza fronteira de módulo)
- **Falsos positivos / cuidados:** referências apenas em testes; ciclos entre classes do mesmo pacote coeso são menos graves.
- **Correção preferida:** mover a parte compartilhada para a unidade de menor nível, inverter dependência por evento/porta somente se o contrato prevê.
- **Conflitos:** CF-14

### UNI-QUA-004 — Duplicação de conhecimento

- **Aplica-se quando:** sempre.
- **Verificar:** mesma regra de negócio, cálculo, validação ou consulta implementada em mais de um lugar, com risco de divergência.
- **Evidência mínima:** E3 com os locais duplicados e a demonstração de que representam a mesma regra.
- **Severidade base:** MEDIUM (HIGH se envolve cálculo financeiro/estoque já divergente)
- **Falsos positivos / cuidados:** semelhança textual acidental; código de teste; DTOs parecidos em contratos diferentes.
- **Correção preferida:** centralizar a regra na unidade dona (Service/domínio); nunca unificar comportamentos que hoje diferem sem decisão humana.
- **Conflitos:** CF-10, CF-16

### UNI-QUA-005 — Complexidade desnecessária e abstrações vazias

- **Aplica-se quando:** sempre.
- **Verificar:** interfaces com uma única implementação sem fronteira de teste/contrato; camadas que só delegam; padrões (Strategy, Factory, Builder) sem variação real; generalização especulativa; condicionais profundas.
- **Evidência mínima:** E3.
- **Severidade base:** LOW (MEDIUM se dificulta mudanças frequentes)
- **Falsos positivos / cuidados:** interfaces exigidas pelo framework, por portas hexagonais do contrato ou por mocks necessários; delegação prevista em exceção registrada.
- **Correção preferida:** simplificar; não criar abstração nova para resolver este achado.
- **Conflitos:** CF-14

### UNI-QUA-006 — Legibilidade e intenção

- **Aplica-se quando:** sempre.
- **Verificar:** nomes enganosos, números mágicos de regra de negócio, métodos muito longos com blocos comentados como seções, booleanos de controle em parâmetros, comentários que contradizem o código.
- **Evidência mínima:** E3.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** estilo diferente do preferido não é problema; respeitar convenções existentes do projeto.
- **Correção preferida:** renomear/extrair constante/método apenas quando tocado por outra mudança autorizada ou quando o risco de erro é concreto.
- **Conflitos:** nenhum conhecido

### UNI-QUA-007 — Testabilidade

- **Aplica-se quando:** sempre.
- **Verificar:** dependências instanciadas com `new` em lógica de negócio, acesso estático a relógio/aleatório/ambiente, lógica de negócio presa em camada difícil de testar (Resource, componente visual), efeitos colaterais ocultos.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** objetos de valor e utilitários puros podem ser instanciados diretamente.
- **Correção preferida:** injeção pelo mecanismo existente (CDI, providers Angular, props/hooks), `Clock` injetável para regras com data.
- **Conflitos:** CF-14

### UNI-QUA-008 — Código morto e elementos não utilizados

- **Aplica-se quando:** sempre.
- **Verificar:** classes, métodos, campos, imports, variáveis, parâmetros, rotas, componentes, dependências de build não utilizados.
- **Evidência mínima:** E2 (compilador/IDE/linter apontando não uso) **e** investigação de referências indiretas (CF-07). Imports não usados apontados pelo compilador/linter são `CONFIRMED`; classes e métodos públicos raramente passam de `PROBABLE`.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** CDI (`@Observes`, `@Produces`, `@Named`), JPA (construtor protegido, callbacks), serialização (getters/setters, `@JsonCreator`), reflexão, `ServiceLoader`, Qute/templates, `application.properties`, testes, APIs públicas de biblioteca, endpoints chamados por sistemas externos.
- **Correção preferida:** remover apenas com evidência + testes verdes; em dúvida, registrar e não remover.
- **Conflitos:** CF-07

### UNI-QUA-009 — APIs depreciadas e incompatíveis com a versão

- **Aplica-se quando:** sempre; usar a versão real do perfil.
- **Verificar:** uso de APIs marcadas `@Deprecated`/`forRemoval`, avisos de depreciação do compilador, namespaces antigos (`javax.*` em Quarkus 3), APIs removidas em versões do framework em uso.
- **Evidência mínima:** E2 (aviso do compilador) ou E3 + referência à documentação oficial da versão em uso.
- **Severidade base:** LOW (MEDIUM se `forRemoval` e upgrade planejado; HIGH se já quebra)
- **Falsos positivos / cuidados:** não recomendar API que só existe em versão mais nova que a do projeto.
- **Correção preferida:** substituição equivalente disponível na versão em uso.
- **Conflitos:** CF-13
