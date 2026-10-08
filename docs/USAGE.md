# Uso — os quatro modos

Invocação (após a instalação):

| Ferramenta | Forma |
|---|---|
| Claude Code, skill por diretório | `/quality-review <MODO> [argumentos]` |
| Claude Code, plugin | `/quality-architecture-base:quality-review <MODO> [argumentos]` |
| Codex CLI (cópia) | `$quality-review <MODO> [argumentos]` ou `/skills` |
| Ambos | linguagem natural: "Use a skill quality-review em modo AUDIT no backend" |

O modo também pode ser deduzido do pedido; em caso de dúvida a skill escolhe um modo **somente
leitura** e avisa. FIX nunca é deduzido.

## INIT — perfilar o projeto

```text
/quality-review INIT
```

O agente:

1. Roda `scripts/detect_stack.py` e `scripts/arch_signals.py` (somente leitura) e confere os arquivos.
2. Descreve a arquitetura **existente** com evidência.
3. Pergunta a arquitetura **desejada** e as políticas que faltam.
4. Propõe `.quality/PROJECT_PROFILE.md`, `.quality/ARCHITECTURE_CONTRACT.md` (se a arquitetura foi
   decidida) e `.quality/QUALITY_STATE.md`.

Não altera código. Revise o perfil e preencha "Última revisão humana".

## AUDIT — auditoria somente leitura

```text
/quality-review AUDIT                       # completa
/quality-review AUDIT persistência          # incremental por área
/quality-review AUDIT pacote com.empresa.vendas
```

Gera `.quality/reports/AUDIT-<data>.md` (template `AUDIT_REPORT.md`) com achados priorizados. Cada
achado traz severidade, estado, evidência, impacto, correção sugerida, conflitos, risco de regressão
e testes necessários. O relatório declara o que foi e o que não foi executado e inclui a prova de
que as fontes não mudaram (`tree_snapshot.py`).

## REVIEW — parecer sobre diff

```text
/quality-review REVIEW                      # alterações não commitadas
/quality-review REVIEW main...HEAD          # branch atual contra main
/quality-review REVIEW src/main/java/com/empresa/vendas/VendaService.java
```

Gera `.quality/reports/REVIEW-<data>.md` com parecer (`APROVADO`, `APROVADO COM RESSALVAS`,
`ALTERAÇÕES NECESSÁRIAS`, `INCONCLUSIVO`), separando problemas introduzidos pelo diff de dívida
pré-existente. Não edita nem commita.

## FIX — refatoração autorizada

```text
/quality-review FIX F-001 F-002 do relatório AUDIT-2026-10-08
```

Fluxo:

1. O agente cria `.quality/plans/PLAN-<data>-<slug>.md` (problema, evidência, comportamento a
   preservar, alternativas, escopo, conflitos, riscos, baseline, passos, critérios de aceite) com
   `Status: PENDING`.
2. **Você** revisa e autoriza explicitamente na conversa (ex.: "Autorizo o plano PLAN-...
   para F-001 e F-002 nos arquivos listados"). O agente transcreve a autorização literal para a
   seção Autorização; ou você mesmo edita o plano.
3. `scripts/fix_gate.py check <plano>` precisa retornar 0.
4. Baseline → testes de caracterização → mudanças pequenas → validação → relatório de regressão.
5. O agente lista os arquivos alterados. **Você** revisa e commita.

Verificar o portão manualmente:

```bash
python3 <dir-da-skill>/scripts/fix_gate.py check .quality/plans/PLAN-2026-10-08-x.md
python3 <dir-da-skill>/scripts/fix_gate.py check .quality/plans/PLAN-2026-10-08-x.md --project . --changed-from-git
```

## Subagentes

Quando instalados (`--with-agents` ou plugin), os papéis podem rodar como subagentes:

| Papel | Claude Code | Codex CLI |
|---|---|---|
| Architecture Auditor | `quality-auditor` | `quality_auditor` (sandbox somente leitura) |
| Controlled Refactorer | `quality-refactorer` | `quality_refactorer` |
| Regression/Performance Validator | `quality-validator` | `quality_validator` |

Exemplo: "Use o subagente quality-auditor para auditar persistência e depois o quality-validator
para avaliar os riscos de regressão do diff".

## Scripts úteis fora dos modos

```bash
S=<dir-da-skill>/scripts
python3 $S/detect_stack.py  /caminho/projeto --format markdown
python3 $S/arch_signals.py  /caminho/projeto --format json
python3 $S/tree_snapshot.py create  /caminho/projeto --output /tmp/antes.json
python3 $S/tree_snapshot.py compare /caminho/projeto --snapshot /tmp/antes.json
```

## Exemplos para treinar

`examples/quarkus-layered-sample/` e `examples/react-sample/` contêm problemas intencionais
documentados em `examples/README.md`. Trabalhe sempre numa cópia fora deste repositório.
