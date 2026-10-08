# Perfil arquitetural — hexagonal (ports & adapters)

## Quando selecionar

Quando o time decidiu explicitamente por portas e adaptadores e registrou no
`ARCHITECTURE_CONTRACT.md` quais pacotes são domínio, aplicação (casos de uso), portas e
adaptadores. Sem esse mapeamento, o perfil não é aplicado (ARC-GEN-001).

## Contrato lógico

```text
Adaptador de entrada (REST, mensageria, CLI) → Caso de uso (aplicação) → Domínio
                                                  ↓ porta de saída (interface no núcleo)
                                     Adaptador de saída (JPA/Panache, HTTP client, fila)
```

| Unidade | Responsabilidade | Não deve |
|---|---|---|
| Domínio | entidades/objetos de valor/regras | depender de framework de infraestrutura (salvo o permitido no contrato) |
| Aplicação | casos de uso, transações, orquestração | depender de adaptadores concretos |
| Porta | interface definida pelo núcleo | ser declarada no adaptador |
| Adaptador de entrada | tradução de protocolo, validação de entrada | conter regra de negócio |
| Adaptador de saída | persistência e integrações; consultas, paginação, carregamento | vazar tipos de infraestrutura para o núcleo |

## Regras ativadas

- `rules/architecture/general.md`
- `rules/architecture/hexagonal.md`
- `rules/backend/dto-mapstruct.md` (DTOs nos adaptadores de entrada)
- Regras de persistência aplicadas aos adaptadores de saída.

## Parâmetros configuráveis

| Parâmetro | Padrão |
|---|---|
| Anotações permitidas no núcleo | `jakarta.inject`, `jakarta.transaction` na aplicação; nada no domínio |
| Separação modelo de domínio × persistência (ARC-HEX-003) | não exigida |
| Uma porta por adaptador de saída | sim |

## Cuidados

- Não criar portas para casos sem variação real ou sem necessidade de teste (CF-14).
- Projeto em camadas que deseja migrar para hexagonal: registrar migração incremental no contrato
  §6 (CF-09). Este perfil não autoriza a migração por si só.
