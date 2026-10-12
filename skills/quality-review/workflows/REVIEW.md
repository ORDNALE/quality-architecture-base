# Workflow REVIEW — parecer sobre diff ou arquivos alterados

**Objetivo:** analisar um diff (ou lista de arquivos), detectar violações e regressões possíveis
introduzidas pela mudança e produzir um parecer. **Sem modificar fontes e sem commitar.**

**Papéis:** Architecture Auditor (violações) e Regression/Performance Validator (riscos de regressão).

Aplicar `references/contracts.md` §7: REVIEW permanece obrigatório quando previsto no projeto,
mas não significa nova auditoria global, nova suíte ou novo arquivo de relatório a cada passo.

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
5. Conferir evidências existentes e sua validade para a revisão/escopo atual. Executar verificações
   que não alteram fontes somente para mudanças posteriores, lacunas ou riscos que as anteriores
   não cubram; não repetir testes/build/lint do FIX se continuarem válidos. Discriminar resultados
   novos, reutilizados e não executados, com justificativa.
6. Parecer: `APROVADO`, `APROVADO COM RESSALVAS`, `ALTERAÇÕES NECESSÁRIAS` ou `INCONCLUSIVO`.
7. Parecer conforme `templates/REVIEW_REPORT.md`: seção compacta no estado/relatório consolidado
   existente para alterações pequenas; arquivo completo quando risco/decisão justificar (ou
   conversa se o perfil/pedido assim determinar). Não duplicar planos ou evidências.
8. `tree_snapshot.py compare` — nenhuma alteração fora de `.quality/`.

## Critérios de saída

- [ ] Achados separados entre "introduzidos pelo diff" e "pré-existentes".
- [ ] Cada achado com evidência e estado.
- [ ] Riscos de regressão listados com o teste que cobre (ou "não coberto").
- [ ] Nenhuma fonte alterada; nenhum commit.
