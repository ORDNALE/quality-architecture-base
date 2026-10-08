# Instruções para agentes que trabalham NESTE repositório

Este repositório é a própria Quality Architecture Base (ferramenta), não um projeto consumidor.

- A fonte única de regras é `skills/quality-review/`. Não duplique regras em adaptadores,
  documentação ou exemplos; referencie os arquivos.
- Formato de regra e de achado: `skills/quality-review/references/contracts.md`. IDs de regra são
  estáveis; remoções vão para o `CHANGELOG.md`.
- Conteúdo em português brasileiro; identificadores e IDs em ASCII.
- Scripts: Python 3.10+ só com biblioteca padrão; nunca gravam no projeto analisado.
- Antes de concluir qualquer mudança, rode:
  - `python3 scripts/validate_repo.py`
  - `python3 -m unittest discover -s tests -v`
  - `claude plugin validate . --strict` (se o Claude Code estiver instalado)
- Exemplos em `examples/` são oráculos de teste: ao mudar código de exemplo, atualize
  `examples/README.md` e os testes.
- Não faça commit, push nem crie tags sem pedido explícito.
- Registre fases e decisões de construção em `docs/IMPLEMENTATION_STATE.md`.
