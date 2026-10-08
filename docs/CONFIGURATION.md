# Configuração por projeto

Toda configuração específica de um projeto fica **no próprio projeto**, em `.quality/`. A base não
guarda nada de projetos consumidores.

```text
<projeto>/
└── .quality/
    ├── PROJECT_PROFILE.md          # perfil (stack, arquitetura, políticas, exceções)
    ├── ARCHITECTURE_CONTRACT.md    # contrato arquitetural desejado (matriz de dependências)
    ├── QUALITY_STATE.md            # estado acumulado: achados abertos/resolvidos, decisões pendentes
    ├── reports/                    # AUDIT-*, REVIEW-*, REGRESSION-*
    └── plans/                      # PLAN-* (planos de FIX com bloco de autorização)
```

Versionar `.quality/` é recomendado (histórico de decisões e exceções). Se o time preferir não
versionar relatórios, adicione `.quality/reports/` ao `.gitignore` do projeto manualmente.

## Perfil do projeto (`PROJECT_PROFILE.md`)

Gerado no INIT a partir de `skills/quality-review/templates/PROJECT_PROFILE.md`. Seções:

| Seção | Para que serve |
|---|---|
| 1. Identificação | nome, domínio, criticidade (dados financeiros/estoque elevam severidades) |
| 2. Stack e versões reais | versões **com fonte**; `NÃO RESOLVIDA` quando não for possível resolver |
| 3. Arquitetura | existente (observada) × desejada (decisão humana); perfis selecionados |
| 4. Padrões obrigatórios | regras exigidas (ex.: Repository Pattern, DTOs, MapStruct, paginação) |
| 5. Regras opcionais | grupos habilitados/desabilitados com justificativa |
| 6. DTOs/MapStruct | nomes, records, `componentModel`, Lombok, quando mapear manualmente |
| 7. Persistência | Repository × Active Record, carregamento, projeções, SQL nativo, transações |
| 8. Paginação | parâmetros, tamanho padrão/máximo, ordenação, formato, keyset, coleções isentas |
| 9. Testes e ferramentas | comandos reais de build, testes, lint, ArchUnit, log SQL, banco para EXPLAIN |
| 10. Exceções justificadas | desvios aprovados, com responsável, data e revisão |
| 11. Restrições | áreas congeladas, contratos que não podem mudar |
| 12. Modo de operação | modos permitidos, saída (arquivos ou só conversa) |
| 13. Conflitos | padrão universal × preferência local e a prioridade adotada |

## Selecionar a arquitetura

| Valor em "Arquitetura desejada" | Efeito |
|---|---|
| `layered` | aplica `rules/architecture/layered.md` (Resource → Service → Repository → Entity) |
| `hexagonal` | aplica `rules/architecture/hexagonal.md`; exige mapeamento de pacotes no contrato |
| `modular` | aplica `rules/architecture/modular.md`; exige lista de módulos e APIs públicas |
| `custom` | aplica somente o que o `ARCHITECTURE_CONTRACT.md` define (regras próprias com prefixo `PRJ-`) |
| `DESCONHECIDO` | nenhuma regra específica de arquitetura; o relatório lista as decisões necessárias |

A arquitetura existente pode diferir da desejada: a diferença é tratada como dívida mapeada e
migrada incrementalmente (conflito CF-09), nunca de uma vez.

## Exceções

Exceções sem justificativa, responsável e data são inválidas. O relatório de auditoria tem uma
seção que lista quais achados foram suprimidos/rebaixados por quais exceções — não existem
exceções silenciosas.

## Prioridade entre fontes de instrução

1. Instruções explícitas do usuário na sessão.
2. Guardrails (`references/safety.md`) — não relaxáveis pelo perfil.
3. Contrato e perfil do projeto (inclusive exceções).
4. Perfis de arquitetura e stack.
5. Regras universais e por área.

Quando uma preferência local diverge de um padrão universal, o perfil (seção 13) registra a
prioridade e o motivo. Correção funcional, integridade de dados, contratos públicos e controles de
segurança existentes não são rebaixados por preferência local. Detalhes em
[RULE_CONFLICTS.md](RULE_CONFLICTS.md).
