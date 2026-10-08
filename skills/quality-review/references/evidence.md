# Critérios de evidência, estado e severidade

Nenhum achado é mais forte que a evidência que o sustenta. Este arquivo define como classificar.

## 1. Tipos de evidência

| Tipo | Nome | Exemplos | Obtida nesta execução? |
|---|---|---|---|
| **E1** | Medição executada | log SQL com contagem de consultas, contador de statements do Hibernate, `EXPLAIN (ANALYZE, BUFFERS)`, profiler, relatório de bundle, Lighthouse | obrigatório |
| **E2** | Ferramenta determinística executada | erro de compilação, teste falhando, ArchUnit, ESLint, Checkstyle/PMD/SpotBugs, `tsc --noEmit` | obrigatório |
| **E3** | Rastreamento estático completo | cadeia de chamadas lida do início ao fim (ex.: laço → getter de associação LAZY sem fetch); `import` proibido presente; assinatura pública retornando `@Entity` | leitura atual do código |
| **E4** | Sinal heurístico | saída de `arch_signals.py`, busca textual, convenção de nome, contagem de arquivos | leitura atual |
| **E5** | Contexto indireto | documentação, comentários, relatórios anteriores, mensagens de commit, `QUALITY_STATE.md` | qualquer época |

Regras:

- E5 **nunca** sustenta sozinho um achado acima de `NEEDS_VERIFICATION`. Documentação antiga é
  contexto, não prova do estado atual.
- Evidência de execuções anteriores conta como E5 até ser refeita.
- Toda evidência E1/E2 registra o comando exato e o ambiente (perfil, volume de dados, versão).
- **Proibido** inventar números, tempos, contagens, planos de execução ou saídas de ferramenta. Se
  não foi executado, escreva "não executado" e o motivo.

## 2. Estado do achado

| Estado | Quando usar |
|---|---|
| `CONFIRMED` | E1 ou E2 reproduziu o problema; **ou** E3 quando o problema é um fato estrutural do código (ex.: `Resource` importa e usa `Repository`; endpoint retorna `@Entity`). |
| `PROBABLE` | E3 de um problema que depende de execução (ex.: N+1 rastreado no código, mas sem log SQL), sem configuração conhecida que o neutralize. |
| `NEEDS_VERIFICATION` | Apenas E4/E5, **ou** E3 em que configuração/ambiente pode mudar o resultado (ex.: `batch-size` global, cache de segundo nível, volume de dados desconhecido, índice que pode existir só no banco). |
| `NOT_REPRODUCED` | Houve tentativa de E1/E2 e o problema não apareceu. Mantém-se registrado com o cenário testado. |

Desempenho: N+1, consultas lentas, índices ausentes e problemas de bundle só são `CONFIRMED` com E1.
Sem medição, são hipóteses (`PROBABLE` ou `NEEDS_VERIFICATION`) e o relatório diz isso.

## 3. Severidade

| Severidade | Critério (impacto real, não estética) |
|---|---|
| `CRITICAL` | Pode corromper/perder dados, produzir cálculo financeiro/fiscal/estoque errado, quebrar integridade transacional, ou derrubar o sistema com volume esperado. |
| `HIGH` | Degradação significativa com crescimento de dados (consulta sem limite em tabela grande, N+1 em listagem principal), violação arquitetural que contorna regra de negócio, transação ou permissão; Entity exposta em API. |
| `MEDIUM` | Custo concreto de manutenção ou desempenho localizado: duplicação de regra de negócio, acoplamento que impede teste, N+1 em coleção pequena, ausência de testes em área crítica. |
| `LOW` | Legibilidade, imports/variáveis não usados confirmados, pequenas inconsistências sem efeito em comportamento. |
| `INFO` | Observação, oportunidade, ponto positivo, ou dívida aceita por exceção. |

A severidade base de uma regra é ajustada pelo contexto: o mesmo N+1 é `HIGH` na listagem de vendas
e `LOW` numa tela administrativa com 5 registros estruturalmente limitados — justifique o ajuste.

## 4. Achados que não são desta base

- **Segurança** (injeção, autenticação, autorização, segredos, criptografia, exposição de dados
  sensíveis): registre na seção "Riscos de segurança encaminhados" sem detalhar exploração e indique
  análise pelo agente/processo de segurança especializado. Não classifique como achado de qualidade,
  não proponha correção de segurança aqui e não enfraqueça controles existentes.
- **Regras de negócio duvidosas** (o cálculo parece errado): registre como `INFO` + decisão humana.
  Corrigir regra de negócio não é refatoração.
