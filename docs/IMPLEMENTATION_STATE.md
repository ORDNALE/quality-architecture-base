# IMPLEMENTATION_STATE

> Registro de construção da própria Quality Architecture Base. Ao retomar, **não assuma** que o
> estado descrito continua válido: rode `python3 scripts/validate_repo.py` e
> `python3 -m unittest discover -s tests` e confira `git status` antes de prosseguir.

## Contexto da execução inicial

- Data: 2026-10-08
- Diretório: `/home/ordnale/Desktop/desenv/quality-architecture-base`
- Ferramentas inspecionadas: Claude Code 2.1.295, codex-cli 0.161.0, Python 3.12.3, Node 24.15.0
- Repositório Git: inicializado com `git init -b main` (autorizado pelo usuário). O remoto
  `https://github.com/ORDNALE/quality-architecture-base` existe, mas **não** foi configurado
  localmente; nenhum commit, push ou tag foi feito.
- ERP de água de coco: **não** auditado nem tocado.

## Plano por fases

| Fase | Situação |
|---|---|
| 1. Fundação | concluída |
| 2. Regras | concluída |
| 3. Perfis técnicos | concluída |
| 4. Skill e workflows | concluída |
| 5. Integrações | concluída |
| 6. Documentação | concluída |
| 7. Validação | concluída (com pendências declaradas abaixo) |

---

## Fase 1 — Fundação

**Entregas**

- `.gitignore`
- `docs/ARCHITECTURE.md` — arquitetura interna, justificativa de estrutura, mapeamento sugerido → implementado
- `skills/quality-review/references/contracts.md` — artefatos do consumidor, modos, autorização FIX,
  formato de regra, formato de achado, precedência
- `skills/quality-review/templates/` — `PROJECT_PROFILE.md`, `ARCHITECTURE_CONTRACT.md`,
  `AUDIT_REPORT.md`, `REVIEW_REPORT.md`, `REFACTORING_PLAN.md`, `REGRESSION_REPORT.md`, `QUALITY_STATE.md`

**Verificações feitas**

- `pwd` e `git rev-parse --show-toplevel` apontam para `quality-architecture-base`.
- Formatos atuais conferidos:
  - Codex (documentação oficial + strings do binário 0.161.0): skills em `.agents/skills` (repo,
    do CWD até a raiz) e `$HOME/.agents/skills`; `SKILL.md` exige `name` e `description`;
    `agents/openai.yaml` opcional dentro da skill; invocação `$nome` ou `/skills`; symlinks
    suportados; agentes customizados em `.codex/agents/*.toml` / `~/.codex/agents/*.toml` com
    `name`, `description`, `developer_instructions`.
  - Claude Code (documentação oficial + `claude plugin --help`): skills em `.claude/skills/<nome>/`
    e `~/.claude/skills/<nome>/`; plugin com `skills/` (invocação `/plugin:skill`); subagentes em
    `.claude/agents/*.md`; `claude plugin validate` disponível localmente.

**Decisões**

- D1: regras, perfis, workflows, papéis e templates ficam **dentro** de `skills/quality-review/`
  para a skill ser portátil (instalação por pasta). Ver `docs/ARCHITECTURE.md`.
- D2: papéis em `roles/` porque `agents/` é reservado pelo Codex dentro da skill.
- D3: artefatos do consumidor em `.quality/` do próprio projeto.
- D4: FIX controlado por bloco de autorização legível por máquina + `fix_gate.py`.
- D5: scripts só com biblioteca padrão Python (sem dependências a instalar).
- D6: conteúdo em português brasileiro; identificadores e IDs em inglês/ASCII.
- D7: template adicional `REVIEW_REPORT.md` (o modo REVIEW precisa de um parecer próprio).

**Pendências**: nenhuma específica da fase.

**Próximo passo**: Fase 2 — regras universais, evidência, perfis arquiteturais, conflitos.

---

## Fase 2 — Regras universais, evidência, perfis arquiteturais e conflitos

**Entregas**

- `skills/quality-review/references/evidence.md` — tipos de evidência E1–E5, estados, severidades,
  encaminhamento de segurança.
- `skills/quality-review/references/safety.md` — guardrails G-01…G-14.
- `skills/quality-review/references/conflict-resolution.md` — procedimento, prioridade padrão,
  catálogo CF-01…CF-16 (inclui N+1 × paginação, DTO × contrato, SQL × resultado, lazy × percepção,
  cache × consistência, camadas × transações/permissões).
- `skills/quality-review/rules/universal/` — `code-quality.md` (UNI-QUA-001…009),
  `errors-and-logging.md` (UNI-ERR-001…004), `business-rule-preservation.md` (UNI-BRP-001…006),
  `versions-and-tooling.md` (UNI-VER-001…003).
- `skills/quality-review/rules/architecture/` — `general.md` (ARC-GEN-001…005), `layered.md`
  (ARC-LAY-001…009), `hexagonal.md` (ARC-HEX-001…004), `modular.md` (ARC-MOD-001…004).
- `skills/quality-review/profiles/architecture/` — `layered.md`, `hexagonal.md`, `modular.md`,
  `custom.md` (inclui o tratamento de arquitetura desejada desconhecida).

**Verificações feitas**: revisão manual de coerência entre IDs citados e definidos (validação
automatizada virá na Fase 7).

**Decisões**

- D8: regras (o que verificar) separadas de perfis (quando aplicar e parâmetros).
- D9: regras específicas de um projeto ficam no contrato do próprio projeto com prefixo `PRJ-`.
- D10: estado `CONFIRMED` para desempenho exige medição (E1).

**Pendências**: IDs citados antecipadamente e ainda não definidos — `BCK-DTO-001`, `BCK-MAP-001`,
`BCK-MAP-003`, `PER-PAG-001`, `PER-PAG-002` (serão criados na Fase 3); `templates/archunit/`
(Fase 3).

**Próximo passo**: Fase 3 — regras de backend, persistência, performance, frontend e testes;
perfis de stack.

---

## Fase 3 — Perfis técnicos e regras por área

**Entregas**

- `rules/backend/` — `dto-mapstruct.md` (BCK-DTO-001…004, BCK-MAP-001…005), `java-quarkus.md`
  (BCK-QRK-001…006).
- `rules/persistence/` — `query-efficiency.md` (PER-N1-001…002, PER-LOAD-001…003, PER-QRY-001…004),
  `pagination.md` (PER-PAG-001…008), `transactions-and-integrity.md` (PER-TX-001…004),
  `indexes-and-plans.md` (PER-IDX-001…004).
- `rules/performance/backend-performance.md` (PRF-MEA-001…002, PRF-CAC-001, PRF-IO-001,
  PRF-MEM-001, PRF-ASY-001).
- `rules/frontend/` — `common.md` (FE-COM-001…011), `angular.md` (FE-NG-001…008), `react.md`
  (FE-RX-001…006), `typescript.md` (FE-TS-001…003).
- `rules/testing/` — `testing-strategy.md` (TST-STR-001…006), `static-analysis.md` (TST-TOOL-001…003).
- `profiles/stack/` — `java-quarkus.md`, `postgresql.md`, `angular.md`, `react.md`, `typescript.md`.
- `templates/archunit/LayeredArchitectureTest.java.template` (ARC-LAY-001/002/009, ciclos, Entity em
  assinaturas de Resource incluindo genéricos).

**Verificações feitas**: revisão manual. Afirmações dependentes de versão foram redigidas com
"confirme na documentação da versão" quando não verificadas nesta execução (ex.: nomes de
propriedades do Hibernate/Quarkus, status de APIs de signals). CF-06 foi corrigido para não afirmar
comportamento de autoinvocação independente de container.

**Decisões**

- D11: perfis de stack trazem detecção + regras a carregar + cuidados por versão; não fixam versões.
- D12: placeholder `${EE_NS}` no modelo ArchUnit para suportar `jakarta`/`javax`.

**Pendências**: compilar o modelo ArchUnit contra a biblioteca real (Fase 7, se houver rede).

**Próximo passo**: Fase 4 — SKILL.md (roteador), workflows INIT/AUDIT/FIX/REVIEW, papéis e scripts.

---

## Fase 4 — Skill, workflows, papéis, scripts e exemplos

**Entregas**

- `skills/quality-review/SKILL.md` — roteador enxuto (frontmatter `name`, `description`,
  `metadata.version`), escolha de modo, perfil, tabela de carregamento sob demanda, papéis, scripts.
- `skills/quality-review/workflows/` — `INIT.md`, `AUDIT.md`, `FIX.md`, `REVIEW.md` (pré-condições,
  proibições, passos, critérios de saída).
- `skills/quality-review/roles/` — `ARCHITECTURE_AUDITOR.md`, `CONTROLLED_REFACTORER.md`,
  `REGRESSION_VALIDATOR.md`.
- `skills/quality-review/scripts/` — `_common.py`, `detect_stack.py`, `arch_signals.py`,
  `tree_snapshot.py`, `fix_gate.py` (Python 3.10+, só biblioteca padrão).
- `examples/quarkus-layered-sample/` (com `.quality/PROJECT_PROFILE.md` e plano FIX `PENDING`),
  `examples/react-sample/`, `examples/README.md` (oráculo de problemas intencionais).

**Verificações feitas (execução real)**

- `detect_stack.py` nos dois exemplos: versões e fontes corretas; versões de BOM marcadas como
  não resolvidas; executado com `python3 -W error` sem avisos.
- `arch_signals.py` no exemplo Quarkus: 7 sinais, todos correspondentes a problemas intencionais;
  falso positivo (JOIN FETCH em comentário) detectado e corrigido.
- `fix_gate.py check` no plano de exemplo `PENDING`: exit 2 (não autorizado), como esperado.
- Referências de linha do `examples/README.md` conferidas com `sed`/`grep` e corrigidas.

**Decisões**

- D13: sinais de scripts são sempre `NEEDS_VERIFICATION` (E4).
- D14: `fix_gate.py` oferece `--changed-from-snapshot` porque `--changed-from-git` não distingue
  alterações do usuário anteriores ao FIX.
- D15: exemplos não são compilados (sem Maven/dependências); isso está declarado nos arquivos.

**Pendências**: testes automatizados (Fase 7).

**Próximo passo**: Fase 5 — adaptadores Claude Code (plugin, subagentes) e Codex (metadados da
skill, agentes customizados), instalador.

---

## Fase 5 — Integrações Claude Code e Codex CLI

**Entregas**

- Claude Code: `.claude-plugin/plugin.json` (plugin `quality-architecture-base`, agentes listados
  explicitamente), `.claude-plugin/marketplace.json` (fonte `./`),
  `integrations/claude/agents/{quality-auditor,quality-refactorer,quality-validator}.md`,
  `integrations/claude/README.md`.
- Codex CLI: `skills/quality-review/agents/openai.yaml`,
  `integrations/codex/agents/{quality_auditor,quality_refactorer,quality_validator}.toml`,
  `integrations/codex/README.md`.
- `integrations/PROJECT_INSTRUCTIONS_SNIPPET.md` (opcional, aplicado manualmente pelo time).
- `scripts/install.sh` (projeto/usuário, symlink/cópia, `--update`, `--uninstall`, `--dry-run`).
- `AGENTS.md` com instruções para quem mantém esta base.

**Verificações feitas (execução real)**

- `claude plugin validate . --strict` (marketplace), `claude plugin validate .claude-plugin/plugin.json --strict`,
  `claude plugin validate skills --strict`, `claude plugin validate integrations/claude/agents --strict`:
  todos "Validation passed", exit 0.
- `codex debug prompt-input` (sem chamada ao modelo) num projeto temporário com a skill instalada:
  - por cópia → skill listada como `quality-review`;
  - por symlink → listada como `quality-architecture-base:quality-review` (o Codex segue o link e
    detecta `.claude-plugin/plugin.json`).
- `install.sh` exercitado em diretórios temporários: dry-run, instalação, recusa de sobrescrita,
  `--update` só sobre instalação própria (marcador `.qab-install`), recusa de diretório alheio,
  `--uninstall` remove só o que criou, recusa de instalar na própria base.

**Decisões**

- D16: `--mode auto` = symlink para Claude, cópia para Codex (nome determinístico `quality-review`).
- D17: `CLAUDE.md` não fica na raiz (o validador de plugin alerta que não é carregado);
  instruções de manutenção em `AGENTS.md`.
- D18: subagentes do Claude localizam a skill por `${CLAUDE_PLUGIN_ROOT}` (plugin) ou pelos
  caminhos de instalação por diretório.

**Pendências / não verificado**

- Descoberta dos agentes customizados do Codex não verificada em execução (não aparece em
  `prompt-input`).
- Instalação do plugin a partir do GitHub não testada (o repositório remoto ainda não tem os
  arquivos; nenhum push foi feito).

**Próximo passo**: Fase 6 — README público, CONTRIBUTING, CHANGELOG e documentação técnica.

---

## Fase 6 — Documentação

**Entregas**

- `README.md` (pt-BR, público): problema, funcionalidades, tecnologias, pré-requisitos, instalação
  Claude/Codex, uso dos quatro modos, perfil/arquitetura, atualização via GitHub, documentação,
  escopo de segurança, contribuição e situação da licença (não definida; não declarado open source).
- `CONTRIBUTING.md` (fluxo, convenções, versionamento semântico, releases e tags planejadas).
- `CHANGELOG.md` (0.1.0 não lançado).
- `docs/INSTALLATION.md`, `docs/USAGE.md`, `docs/CONFIGURATION.md`, `docs/RULE_CONFLICTS.md`,
  `docs/EXTENDING.md` (além de `docs/ARCHITECTURE.md` da Fase 1).

**Verificações feitas**: comandos citados conferidos contra `--help` das ferramentas instaladas
(`claude plugin marketplace add|update`, `claude plugin install|update|uninstall|validate`,
`claude --plugin-dir`, `codex debug prompt-input`); exemplos de IDs fictícios trocados por `NNN`
para não colidir com a validação.

**Decisões**

- D19: nenhuma licença criada; README declara a pendência.
- D20: `docs/VALIDATION.md` será escrito na Fase 7 com resultados reais.

**Próximo passo**: Fase 7 — `scripts/validate_repo.py`, testes automatizados, validações de
integração e `docs/VALIDATION.md`.

---

## Fase 7 — Validação

**Entregas**

- `scripts/validate_repo.py` (integridade, links/âncoras, frontmatter, formato e unicidade de
  regras, referências cruzadas, roteamento, estrutura, vocabulário, adaptadores, versões).
- `tests/` com 66 testes (`unittest`, só biblioteca padrão), incluindo testes de mutação do
  validador e integração opt-in com o Codex.
- `docs/VALIDATION.md` com resultados reais e o que não foi testado.

**Verificações feitas (resultados reais)** — detalhes em `docs/VALIDATION.md`

- Validador: 0 erros, 0 avisos, 127 regras. Testes: 66 OK (2 opt-in, que também passaram com
  `QAB_INTEGRATION=1`). `claude plugin validate --strict`: 4 alvos aprovados.
- Plugin instalado de marketplace local (configuração isolada): Skills (1), Agents (3).
- Modelo ArchUnit compilado e executado contra o exemplo: detecta ARC-LAY-001 e BCK-DTO-001.
- Exercícios com modelos reais em cópias isoladas: AUDIT (Claude), REVIEW e INIT (Codex), FIX sem
  autorização (Claude, duas versões do contrato). Nenhuma fonte alterada nem commit, exceto na 1ª
  versão do FIX (falha documentada e corrigida).

**Correções feitas durante a validação**

- C1: severidade inválida em ARC-GEN-003 (detectada pelo validador).
- C2: falso positivo de JOIN FETCH em comentário (`arch_signals.py`).
- C3: scripts gravavam `__pycache__` dentro da skill → `sys.dont_write_bytecode`.
- C4: subagentes Claude declarados pela chave `agents` não carregavam via marketplace → movidos
  para a pasta padrão `agents/` na raiz (substitui o registrado na Fase 5 sobre
  `integrations/claude/agents/`); validador proíbe a chave.
- C5: **FIX autoaprovado pelo pedido inicial** (E2E) → contrato reforçado e `fix_gate.py` exige o
  identificador do plano na evidência; teste de regressão adicionado; reexecução confirmou o
  comportamento correto.
- C6: aviso de compatibilidade de bytecode no modelo ArchUnit (ArchUnit 1.3.0 × javac 25).

**Pendências (não concluídas nesta execução)**

1. Push para `https://github.com/ORDNALE/quality-architecture-base` e teste de instalação do
   plugin a partir do GitHub (não feito: commits/push fora do escopo desta execução).
2. Execução real dos agentes customizados do Codex e da delegação a subagentes do Claude Code.
3. FIX autorizado completo ponta a ponta (requer projeto compilável com Maven e, idealmente,
   PostgreSQL para medições).
4. Exercícios com modelo para perfis Angular/React.
5. Definição de licença pelo proprietário.
6. Primeira release/tag `v0.1.0` (após revisão humana e commit pelo proprietário).

**Estado final do repositório**: arquivos criados no diretório de trabalho; **nenhum commit**,
nenhum remoto configurado, nenhuma tag, nenhum push. ERP não acessado.

**Próximo passo sugerido**: revisão humana, `git add` + commit pelo proprietário, configurar o
remoto e push; depois validar a instalação via GitHub (pendência 1).
