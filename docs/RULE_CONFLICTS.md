# Conflitos entre diretrizes

A fonte canônica é
[`skills/quality-review/references/conflict-resolution.md`](../skills/quality-review/references/conflict-resolution.md).
Este documento explica a abordagem para quem mantém ou usa a base; ele não repete o catálogo.

## Princípio

Toda correção tem efeito colateral. Uma recomendação só é aceitável se declarar quais diretrizes
ela tensiona e como as preserva. Exemplos que motivaram o catálogo:

| Correção ingênua | Efeito colateral | Conflito |
|---|---|---|
| `JOIN FETCH` de coleção para resolver N+1 | paginação passa a ser feita em memória | CF-01 |
| Trocar Entity por DTO | JSON da API muda (nomes, nulos, datas) | CF-02 |
| Reescrever consulta "mais rápida" | linhas, ordem ou totais mudam | CF-03 |
| Lazy loading em todas as rotas | navegação mais lenta, mais requisições | CF-04 |
| Cache em consulta de saldo | dado desatualizado ou vazado entre usuários | CF-05 |
| Mover lógica do Resource para o Service | fronteira de transação ou permissão muda | CF-06 |
| Remover classe "não usada" | quebra uso por CDI/JPA/reflexão | CF-07 |
| Adicionar paginação a endpoint existente | clientes que esperam lista completa quebram | CF-11 |

## Como um conflito aparece nos artefatos

- **Relatório de auditoria:** coluna "Conflitos" em cada achado e seção 4 com conflitos que exigem
  decisão.
- **Plano de refatoração:** seção 6 lista conflitos e como foram resolvidos.
- **Estado da qualidade:** "Decisões pendentes" acumula conflitos irreconciliáveis.

## Conflito irreconciliável

Quando a resolução exige decisão de negócio ou de arquitetura, o agente **suspende apenas a
alteração afetada**, registra a decisão pendente e segue com o restante do escopo autorizado.

## Prioridade padrão

Correção funcional e regra de negócio → integridade de dados/transações → contratos públicos →
segurança existente → desempenho medido → arquitetura desejada → manutenibilidade → estética.
O perfil do projeto pode reordenar apenas os itens de desempenho em diante, com justificativa.

## Propor um novo conflito

Siga [EXTENDING.md](EXTENDING.md#adicionar-um-conflito): use o próximo `CF-NN`, descreva tensão,
resolução preferida e o que é proibido, e cite-o nas regras afetadas.
