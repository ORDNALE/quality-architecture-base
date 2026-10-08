# Regras de backend — DTOs, contratos de API e MapStruct

### BCK-DTO-001 — Entity não exposta em contratos HTTP

- **Aplica-se quando:** projeto expõe API e o perfil exige DTOs (padrão em layered e hexagonal).
- **Verificar:** métodos de Resource que recebem ou retornam `@Entity` (direto, em `List<>`, `Uni<>`, `Response.ok(entity)`, `Page<>`); entidades serializadas por Jackson/JSON-B.
- **Evidência mínima:** E3 (assinatura ou corpo do método) ou E2 (ArchUnit).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** entidade usada apenas internamente; endpoints de administração com exceção registrada. Exposição de campos sensíveis → também seção de segurança encaminhada.
- **Correção preferida:** Response DTO que reproduz **exatamente** o JSON atual (nomes, nulos, formatos, ordem quando relevante), com teste de contrato capturado antes (TST-STR-003).
- **Conflitos:** CF-02

### BCK-DTO-002 — Request e Response separados

- **Aplica-se quando:** perfil exige DTOs.
- **Verificar:** mesmo DTO usado para entrada e saída quando os campos diferem (id, campos calculados, campos somente leitura, auditoria); DTO de entrada aceitando campos que o cliente não deveria definir.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM (aceitação de campos indevidos → seção de segurança encaminhada)
- **Falsos positivos / cuidados:** CRUDs triviais com campos idênticos podem compartilhar se o perfil permitir.
- **Correção preferida:** `XxxRequest` e `XxxResponse` distintos, sem alterar o JSON aceito/retornado.
- **Conflitos:** CF-02

### BCK-DTO-003 — Validação de entrada no Request DTO

- **Aplica-se quando:** projeto usa Bean Validation (Hibernate Validator).
- **Verificar:** ausência de `@Valid` em parâmetros de Resource com DTO anotado; validações manuais duplicadas; validação de formato misturada a regra de negócio.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** mover/adicionar validação muda respostas 400 e mensagens (CF-02); validação de negócio (ex.: saldo suficiente) pertence ao Service.
- **Correção preferida:** anotações no Request DTO + `@Valid`, preservando mensagens/status atuais ou com autorização para mudá-los.
- **Conflitos:** CF-02

### BCK-DTO-004 — DTOs simples e sem regra de negócio

- **Aplica-se quando:** sempre que há DTOs.
- **Verificar:** DTOs com lógica, acesso a repositórios, dependência de Entity (ex.: construtor `XxxResponse(Entity e)`), mutabilidade desnecessária.
- **Evidência mínima:** E3.
- **Severidade base:** LOW (MEDIUM se o DTO dispara carregamento LAZY)
- **Falsos positivos / cuidados:** `record` é uma boa opção quando Java ≥ 16 e a biblioteca de serialização em uso suporta records — confirme a versão.
- **Correção preferida:** conversão no Mapper ou na projeção do Repository.
- **Conflitos:** CF-14

### BCK-MAP-001 — MapStruct conforme o perfil

- **Aplica-se quando:** perfil do projeto adota MapStruct.
- **Verificar:** mapeamentos manuais extensos e repetitivos onde o perfil prevê MapStruct; Mappers configurados com `componentModel` compatível com CDI na versão em uso; processador de anotações configurado no build (`annotationProcessorPaths`).
- **Evidência mínima:** E3 (código + `pom.xml`).
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** se o projeto **não** usa MapStruct, adicioná-lo é mudança de dependência (G-07) e só entra como recomendação. Mapeamentos triviais podem ficar manuais se o perfil permitir.
- **Correção preferida:** introduzir Mapper por agregado/caso de uso tocado, sem migração em massa.
- **Conflitos:** CF-12, CF-14

### BCK-MAP-002 — Campos não mapeados e ignorados são deliberados

- **Aplica-se quando:** projeto usa MapStruct.
- **Verificar:** avisos de compilação "Unmapped target properties"; `unmappedTargetPolicy` (global via `@MapperConfig` ou por Mapper) permissivo sem justificativa; `@Mapping(target = "...", ignore = true)` sem motivo; campos novos de Entity/DTO não refletidos.
- **Evidência mínima:** E2 (saída do compilador) ou E3.
- **Severidade base:** MEDIUM (campo de contrato silenciosamente nulo)
- **Falsos positivos / cuidados:** mudar a política para `ERROR` pode quebrar o build de outros mappers — trate como FIX planejado.
- **Correção preferida:** `ReportingPolicy.ERROR` (ou `WARN` monitorado) definido no projeto; ignores explícitos e justificados.
- **Conflitos:** CF-02

### BCK-MAP-003 — Mapper não dispara N+1 nem acessa associações fora de transação

- **Aplica-se quando:** Mapper converte Entity com associações LAZY.
- **Verificar:** Mapper que navega associações (`source.cliente.nome`, coleções) para cada item de uma lista; mapeamento executado após o fim da transação (`LazyInitializationException`); mapeamento de coleções inteiras quando a resposta só precisa de contagem/resumo.
- **Evidência mínima:** E3 (PROBABLE) ou E1 com log SQL (CONFIRMED).
- **Severidade base:** HIGH em listagens; MEDIUM em detalhe de um único registro.
- **Falsos positivos / cuidados:** associações já carregadas por fetch planejado no Repository; batch fetching configurado (verifique a configuração efetiva).
- **Correção preferida:** decidir o carregamento no Repository (projeção DTO, fetch to-one, batch, duas etapas) — ver PER-N1-001 e CF-01.
- **Conflitos:** CF-01

### BCK-MAP-004 — Mapper sem regra de negócio

- **Aplica-se quando:** projeto usa Mappers.
- **Verificar:** `@Mapping(expression = "java(...)")`, `@AfterMapping` ou métodos default com cálculo de negócio, decisões de estado, chamadas a serviços.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** formatação/conversão de tipo simples é aceitável.
- **Correção preferida:** calcular no Service e mapear o resultado.
- **Conflitos:** CF-06

### BCK-MAP-005 — Sem Lombok automático; acessores com semântica preservados

- **Aplica-se quando:** sempre.
- **Verificar:** propostas/diffs que introduzem Lombok sem decisão do perfil; remoção de getters/setters com lógica, validação, cópia defensiva ou anotações de serialização em nome de "usar MapStruct".
- **Evidência mínima:** diff/proposta (E3).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** projetos que já usam Lombok: a combinação Lombok + MapStruct exige a ordem/binding de processadores correta (ex.: `lombok-mapstruct-binding`) — verificar no build.
- **Correção preferida:** MapStruct gera o mapeamento; acessores continuam como estão.
- **Conflitos:** CF-12
