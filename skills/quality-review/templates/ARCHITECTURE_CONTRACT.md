# ARCHITECTURE_CONTRACT — <nome do projeto>

> Contrato arquitetural **desejado** para o projeto, decidido por pessoas. Fica em
> `.quality/ARCHITECTURE_CONTRACT.md`. A arquitetura existente pode divergir; a divergência é
> tratada como dívida mapeada, não como autorização para migrar tudo de uma vez.

- **Perfil base:** <`profiles/architecture/layered.md` | `hexagonal.md` | `modular.md` | `custom.md`>
- **Status:** <RASCUNHO | APROVADO>
- **Aprovado por / data:** <nome, AAAA-MM-DD>

## 1. Unidades arquiteturais

| Unidade (camada/módulo/porta) | Responsabilidade | Como identificar no código |
|---|---|---|
| <ex.: Resource> | <contrato HTTP, validação de entrada, delegação> | <pacote `..resource..`, sufixo `Resource`, `@Path`> |
| <ex.: Service> | | |
| <ex.: Repository> | | |
| <ex.: Entity> | | |
| <ex.: DTO> | | |
| <ex.: Mapper> | | |

## 2. Dependências permitidas

> Linhas dependem de colunas. `✔` permitido, `✘` proibido, `≈` permitido com exceção registrada.

| De \ Para | Resource | Service | Repository | Entity | DTO | Mapper |
|---|---|---|---|---|---|---|
| Resource | — | ✔ | ✘ | ✘ | ✔ | ≈ |
| Service | ✘ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Repository | ✘ | ✘ | — | ✔ | ≈ (projeções) | ✘ |
| Entity | ✘ | ✘ | ✘ | ✔ | ✘ | ✘ |
| DTO | ✘ | ✘ | ✘ | ✘ | ✔ | ✘ |
| Mapper | ✘ | ✘ | ✘ | ✔ | ✔ | ✔ |

## 3. Regras habilitadas

| Grupo | Situação | Observação |
|---|---|---|
| `ARC-GEN-*` | habilitado | sempre |
| `ARC-LAY-*` | <habilitado / n.a.> | |
| `ARC-HEX-*` | <habilitado / n.a.> | |
| `ARC-MOD-*` | <habilitado / n.a.> | |

## 4. Mapeamento de pacotes/módulos

```text
<raiz>/
  <pacote ou módulo> → <unidade>
```

## 5. Verificação automatizada

- ArchUnit: <não usado / `src/test/java/.../ArchitectureTest.java`> (modelo: `templates/archunit/LayeredArchitectureTest.java.template`)
- Outras: <ex.: regras ESLint `no-restricted-imports`, dependency-cruiser>

## 6. Divergências conhecidas entre existente e desejado

| Área | Situação atual | Alvo | Estratégia | Prioridade |
|---|---|---|---|---|
| | | | <incremental por funcionalidade tocada / plano dedicado> | |

## 7. Exceções arquiteturais

> Mesma regra do perfil: justificativa, responsável, data, revisão. Ex.: endpoint de health-check
> que consulta o banco diretamente por exigência operacional.

| ID | Regra | Escopo | Justificativa | Aprovado por | Data |
|---|---|---|---|---|---|
