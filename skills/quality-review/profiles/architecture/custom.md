# Perfil arquitetural — personalizado e arquitetura desconhecida

## Arquitetura desejada desconhecida

Quando o `PROJECT_PROFILE.md` registra arquitetura desejada `DESCONHECIDO`:

1. **Não** aplique `rules/architecture/layered.md`, `hexagonal.md` ou `modular.md`.
2. Aplique `rules/architecture/general.md` e as demais áreas (qualidade, persistência, performance,
   frontend, testes), que independem do perfil arquitetural.
3. Descreva a arquitetura **existente** com evidência (E3/E4) no relatório, sem julgá-la contra um
   alvo inexistente.
4. Liste as decisões necessárias, por exemplo:
   - "Resources acessam Repositories diretamente em 12 classes. Isso é aceito (arquitetura
     simplificada) ou o alvo é camadas com Service obrigatório?"
   - "Há `PanacheEntity` (Active Record) e `PanacheRepository` coexistindo. Qual padrão é o alvo?"
5. Registre as perguntas em `QUALITY_STATE.md` §5 (Decisões pendentes).

## Perfil personalizado

Use quando nenhum perfil pronto descreve a arquitetura desejada (ex.: CQRS simples, vertical slices,
camadas com variações). O time descreve o contrato no `ARCHITECTURE_CONTRACT.md`:

1. Unidades, responsabilidades e como identificá-las no código.
2. Matriz de dependências permitidas/proibidas.
3. Quais regras existentes se aplicam (pode reaproveitar IDs `ARC-LAY-*` etc. com escopo ajustado).
4. Regras novas específicas do projeto: escreva-as **no próprio contrato** do projeto, com IDs
   prefixados pelo projeto (ex.: `PRJ-ARC-001`), e não nesta base.

Se uma regra personalizada for útil para vários projetos, proponha-a a esta base seguindo
`docs/EXTENDING.md`.

## Avaliação de um contrato personalizado

O agente verifica apenas o que o contrato define. Lacunas (ex.: matriz incompleta) são registradas
como `INFO` e decisão pendente; não são preenchidas por suposição.
