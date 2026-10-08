# Regras de arquitetura — hexagonal (ports & adapters)

Aplicam-se **somente** quando o perfil seleciona `profiles/architecture/hexagonal.md` e o
`ARCHITECTURE_CONTRACT.md` define os pacotes de domínio, aplicação, portas e adaptadores.

### ARC-HEX-001 — Núcleo independente de frameworks e adaptadores

- **Aplica-se quando:** perfil hexagonal.
- **Verificar:** domínio/aplicação importando JAX-RS, JPA/Hibernate, Panache, clientes HTTP, mensageria, ou pacotes de adaptadores.
- **Evidência mínima:** E2 (ArchUnit) ou E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** o contrato pode permitir anotações neutras (ex.: `jakarta.inject`, `jakarta.transaction` na aplicação). Respeite o que estiver registrado.
- **Correção preferida:** introduzir/usar a porta já definida; não criar portas para casos sem variação (CF-14).
- **Conflitos:** CF-14

### ARC-HEX-002 — Portas definidas pelo núcleo, implementadas por adaptadores

- **Aplica-se quando:** perfil hexagonal.
- **Verificar:** interfaces de porta declaradas no adaptador; núcleo dependendo da implementação concreta; adaptador de saída chamado diretamente por adaptador de entrada.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** —
- **Correção preferida:** mover a interface para o núcleo; adaptador de entrada chama caso de uso.
- **Conflitos:** CF-09

### ARC-HEX-003 — Modelo de domínio separado do modelo de persistência (se o contrato exigir)

- **Aplica-se quando:** perfil hexagonal **e** contrato exige separação domínio/persistência.
- **Verificar:** `@Entity` no pacote de domínio; domínio dependente de lazy loading.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** muitos projetos hexagonais aceitam entidades JPA como domínio por pragmatismo; só é achado se o contrato proibir.
- **Correção preferida:** mapeamento no adaptador de persistência, incremental.
- **Conflitos:** CF-09, CF-14

### ARC-HEX-004 — Adaptadores de entrada sem regra de negócio

- **Aplica-se quando:** perfil hexagonal.
- **Verificar:** regras de negócio em adaptadores REST/mensageria/CLI.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** tradução de protocolo e validação de entrada pertencem ao adaptador.
- **Correção preferida:** mover para o caso de uso com testes de caracterização.
- **Conflitos:** CF-06
