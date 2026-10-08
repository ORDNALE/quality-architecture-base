# REFACTORING_PLAN — cliente-resource-dto — 2026-10-08 (EXEMPLO, NÃO AUTORIZADO)

> Plano obrigatório para o modo FIX. Fica em `.quality/plans/`. Nenhuma linha de código é
> alterada antes de a seção **Autorização** estar preenchida e `scripts/fix_gate.py check` passar.

- **Projeto:** vendas-sample
- **Origem:** achados de exemplo F-001 (ARC-LAY-001), F-002 (BCK-DTO-001), F-003 (PER-QRY-001/PER-PAG-001) — ver `examples/README.md`
- **Executor:** <ferramenta/agente> — papel: Controlled Refactorer

## 1. Problema

`ClienteResource` acessa `ClienteRepository` diretamente (F-001), retorna a entidade `Cliente`
(F-002) e filtra a tabela inteira em memória (F-003).

## 2. Evidência

| Achado | Estado no relatório | Evidência | Precisa medir antes? |
|---|---|---|---|
| F-001 | CONFIRMED | E3: `ClienteResource.java:18` injeta `ClienteRepository` | não |
| F-002 | CONFIRMED | E3: `ClienteResource.java:23` retorna `List<Cliente>` | não |
| F-003 | PROBABLE | E3: `listAll().stream().filter(...)`; volume não medido | sim, para priorizar |

## 3. Comportamento observável a preservar

- Contratos HTTP: `GET /clientes?cidade=` retorna array JSON com `id`, `nome`, `cidade`, `ativo`;
  filtro por cidade sem diferenciar maiúsculas/minúsculas; sem paginação no contrato atual (CF-11).
- Regras de negócio: nenhuma alteração.
- Permissões e autenticação: endpoint sem restrição (manter).
- Transações: somente leitura.
- Consultas: mesmas linhas para os mesmos filtros (CF-03: `equalsIgnoreCase` × colação do banco).

## 4. Alternativas consideradas

| Alternativa | Prós | Contras | Escolhida? |
|---|---|---|---|
| `ClienteService` + `ClienteResponse` + consulta filtrada no Repository | resolve F-001/F-002/F-003 | novo Service | sim |
| Somente trocar Entity por DTO no Resource | mudança mínima | mantém F-001 e F-003 | não |
| Adicionar paginação agora | resolve PER-PAG-001 | muda o contrato (CF-11) | não — decisão humana pendente |

## 5. Escopo

- **Dentro:** `ClienteResource`, novo `ClienteService`, novo `ClienteResponse`, método de consulta em `ClienteRepository`, teste de contrato.
- **Fora (explicitamente):** paginação de `/clientes`, demais Resources.
- **Regra de negócio alterada:** NÃO

## 6. Diretrizes em conflito

| Conflito (`CF-xx`) | Como foi resolvido | Decisão humana? |
|---|---|---|
| CF-02 | teste de contrato do JSON antes da troca | não |
| CF-03 | teste comparando filtro em memória × consulta (`lower(cidade) = lower(:cidade)`) | não |
| CF-11 | paginação fora do escopo | sim (pendente) |

## 7. Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Diferença de comparação de texto (acentos/colação) | média | teste de caracterização com acentos |

## 8. Baseline e verificações

| Verificação | Comando | Resultado ANTES | Resultado DEPOIS |
|---|---|---|---|
| Compilação | `./mvnw -q -DskipTests compile` | não executado | — |

## 9. Passos incrementais

1. Teste de contrato de `GET /clientes` (com e sem `cidade`).
2. `ClienteRepository.listarPorCidade(String)`.
3. `ClienteService` + `ClienteResponse` + Mapper.
4. `ClienteResource` delega ao Service.

## 10. Critérios de aceite

- [ ] Teste de contrato passa antes e depois.
- [ ] Arquivos alterados ⊆ arquivos autorizados.

## 11. Autorização

<!-- qab:authorization:start -->
- Status: PENDING
- Autorizado por:
- Data:
- Evidência da autorização:
- Achados autorizados: F-001, F-002, F-003
- Arquivos autorizados:
  - src/main/java/com/example/vendas/resource/ClienteResource.java
  - src/main/java/com/example/vendas/service/ClienteService.java
  - src/main/java/com/example/vendas/dto/ClienteResponse.java
  - src/main/java/com/example/vendas/repository/ClienteRepository.java
  - src/test/java/com/example/vendas/**
- Alteração de regra de negócio autorizada: NÃO
<!-- qab:authorization:end -->
