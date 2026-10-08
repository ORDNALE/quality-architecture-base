# Trecho opcional para instruções do projeto consumidor

O instalador **não** altera `AGENTS.md`, `CLAUDE.md` nem outros arquivos do projeto. Se o time
quiser que os agentes lembrem da skill sem precisar invocá-la explicitamente, copie manualmente o
trecho abaixo para o arquivo de instruções do projeto (`AGENTS.md` para Codex; `CLAUDE.md` para
Claude Code — ou um `CLAUDE.md` contendo `@AGENTS.md`).

```markdown
## Qualidade e arquitetura

- Este projeto usa a skill `quality-review` (Quality Architecture Base).
- Perfil do projeto: `.quality/PROJECT_PROFILE.md`; contrato: `.quality/ARCHITECTURE_CONTRACT.md`.
- Auditorias e revisões são somente leitura (modos AUDIT e REVIEW).
- Refatorações (modo FIX) só com plano autorizado em `.quality/plans/` e `fix_gate.py` aprovado.
- Nunca fazer commit, push ou migrations automaticamente.
```
