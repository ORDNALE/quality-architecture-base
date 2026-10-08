# Workflow REVIEW — parecer sobre diff ou arquivos alterados

**Objetivo:** analisar um diff (ou lista de arquivos), detectar violações e regressões possíveis
introduzidas pela mudança e produzir um parecer. **Sem modificar fontes e sem commitar.**

**Papéis:** Architecture Auditor (violações) e Regression/Performance Validator (riscos de regressão).

## Pré-condições

- Alvo definido: `git diff` (não commitado), `git diff --staged`, `git diff <base>...HEAD`, commit,
  ou lista de arquivos. Se não informado, use alterações não commitadas e diga isso.
- Perfil do projeto lido (ou ausência declarada).

## Proibido

- Editar arquivos do projeto (G-02), aplicar sugestões, fazer commit/push (G-01).
- Reportar dívida pré-existente como se fosse introduzida pelo diff.

## Passos

1. `tree_snapshot.py create` (recomendado) e registro do alvo exato (comando de diff usado).
2. Obtenha o diff completo e a lista de arquivos. Leia contexto suficiente ao redor de cada
   mudança (chamadores, testes, consultas, contratos).
3. Carregue somente as regras das áreas tocadas (tabela do `SKILL.md`).
4. Para cada mudança, verifique:
   - Violações de regras/perfil **introduzidas ou agravadas**.
   - Regressões possíveis: contratos HTTP (campos, status, paginação), regra de negócio (cálculos,
     arredondamento, datas, estados), transações/permissões movidas (CF-06), consultas alteradas
     (linhas, ordenação — CF-03), novos N+1 (associação acessada em laço/Mapper), listagens sem
     paginação, lazy loading/bundle no frontend.
   - Integridade de testes: removidos, desabilitados, asserções afrouxadas (UNI-BRP-005).
   - Diffs de FIX: escopo vs. plano autorizado (`fix_gate.py check --changed-from-git`).
5. Execute verificações que não alteram fontes, se disponíveis e rápidas (compilação, testes dos
   módulos tocados, lint). Registre o que não foi executado.
6. Parecer: `APROVADO`, `APROVADO COM RESSALVAS`, `ALTERAÇÕES NECESSÁRIAS` ou `INCONCLUSIVO`.
7. Relatório: `templates/REVIEW_REPORT.md` → `.quality/reports/REVIEW-<data>.md` (ou conversa).
8. `tree_snapshot.py compare` — nenhuma alteração fora de `.quality/`.

## Critérios de saída

- [ ] Achados separados entre "introduzidos pelo diff" e "pré-existentes".
- [ ] Cada achado com evidência e estado.
- [ ] Riscos de regressão listados com o teste que cobre (ou "não coberto").
- [ ] Nenhuma fonte alterada; nenhum commit.
