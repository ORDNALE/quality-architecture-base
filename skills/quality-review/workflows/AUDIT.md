# Workflow AUDIT — auditoria somente leitura

**Objetivo:** auditoria completa ou incremental de arquitetura, DTO/MapStruct, qualidade, SQL,
N+1, paginação, frontend, testes e conflitos, gerando relatório priorizado. **Sem editar fontes.**

**Papel:** Architecture Auditor (`roles/ARCHITECTURE_AUDITOR.md`).

## Pré-condições

- Projeto alvo confirmado; `git status --porcelain` e `git rev-parse HEAD` registrados.
- `.quality/PROJECT_PROFILE.md` lido, ou ausência declarada (arquitetura desejada = `DESCONHECIDO`).
- Escopo definido: completo, ou incremental (módulo, pacote, funcionalidade, área: backend,
  persistência, frontend, testes).

## Proibido

- Editar código-fonte, testes, build, configuração ou dependências (G-02).
- Executar migrations, alterar dados, `EXPLAIN ANALYZE` de DML fora de transação descartada (G-12).
- Instalar ferramentas (G-07). Afirmar desempenho sem medição (G-06).

## Passos

1. **Prova de não alteração (recomendado):**
   `python3 scripts/tree_snapshot.py create <projeto> --output <fora-do-projeto>/audit.snapshot.json`
2. **Carregar regras** conforme a tabela de roteamento do `SKILL.md`, a partir do perfil.
   Releia o código atual: relatórios anteriores e `QUALITY_STATE.md` são contexto (E5).
3. **Sinais automáticos (E4):** `detect_stack.py` (versões ainda batem com o perfil?) e
   `arch_signals.py` (violações candidatas, Active Record, EAGER, filtros em memória, `listAll`).
4. **Verificações determinísticas disponíveis (E2)** — somente as que não alteram fontes e que
   `references/contracts.md` §7 considere proporcionais ao escopo: compilação, testes e
   linters/ArchUnit já configurados. Reutilize resultado válido do mesmo estado (revisão, escopo e
   condições conferidos; classificação original preservada, nunca apresentado como execução nova)
   e execute só o que faltar ou tiver mudado. Registre comando e resultado, discriminando novo ×
   reutilizado. Se forem demoradas ou exigirem serviços (Docker, banco), combine com o usuário ou
   declare "não executado".
5. **Análise por área** (pule as que o perfil desabilita):
   1. Arquitetura (`rules/architecture/`), respeitando o perfil e as exceções registradas.
   2. Backend e contratos: DTO/MapStruct, Quarkus (`rules/backend/`).
   3. Persistência: N+1, carregamento, consultas, paginação, transações, índices (`rules/persistence/`).
      Para cada listagem de coleção potencialmente grande, rastreie Resource → Service →
      Repository → consulta → mapeamento/serialização.
   4. Performance de backend (`rules/performance/`).
   5. Frontend (`rules/frontend/`): rotas e lazy loading, bundle, requisições, busca, paginação,
      estado, vazamentos, acessibilidade, uso móvel.
   6. Qualidade universal e testes (`rules/universal/`, `rules/testing/`).
6. **Medições opcionais (E1)**, somente se houver ambiente adequado e o usuário concordar:
   log SQL/contagem em testes, `EXPLAIN` em banco local/teste, relatório de bundle.
7. **Classificar** cada achado: regra, severidade, estado, evidência (E1–E5), impacto,
   correção recomendada e alternativas, conflitos (`references/conflict-resolution.md`), risco de
   regressão, testes necessários. Aplique exceções do perfil explicitamente (seção 5 do relatório).
8. **Priorizar:** severidade → estado → custo/risco de correção. Agrupe achados com a mesma causa.
9. **Relatório:** `templates/AUDIT_REPORT.md` → `.quality/reports/AUDIT-<data>.md` (ou conversa).
   Atualize `.quality/QUALITY_STATE.md` (achados abertos, decisões pendentes).
10. **Prova de não alteração:**
    `python3 scripts/tree_snapshot.py compare <projeto> --snapshot <arquivo>` — deve reportar
    nenhuma alteração fora de `.quality/`. Registre o resultado no cabeçalho do relatório.

## Critérios de saída

- [ ] Toda regra aplicada é compatível com o perfil selecionado (nenhuma regra de perfil com arquitetura desconhecida).
- [ ] Todo achado tem evidência e estado coerentes com `references/evidence.md`.
- [ ] Achados de desempenho sem E1 não estão como `CONFIRMED`.
- [ ] Verificações executadas e não executadas listadas.
- [ ] Riscos de segurança apenas encaminhados.
- [ ] Nenhuma fonte alterada (snapshot comparado ou limitação declarada).
