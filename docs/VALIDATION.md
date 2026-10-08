# Validação

Como a base é validada, o que foi testado e o que **não** foi. Resultados registrados em
2026-10-08 com Claude Code 2.1.295, codex-cli 0.161.0, Python 3.12.3, javac 25.0.1.

## 1. Como rodar

```bash
python3 scripts/validate_repo.py                       # integridade e coerência da base
python3 -m unittest discover -s tests -v               # testes automatizados
claude plugin validate . --strict                      # marketplace (se tiver Claude Code)
claude plugin validate .claude-plugin/plugin.json --strict
QAB_INTEGRATION=1 python3 -m unittest discover -s tests -p "test_integration_tools.py" -v   # opt-in: Codex
```

## 2. Validador da base (`scripts/validate_repo.py`)

| Verificação | O que pega |
|---|---|
| Arquivos vazios | arquivos sem conteúdo |
| Links e âncoras Markdown | links relativos quebrados, âncoras inexistentes (ignora blocos de código) |
| `SKILL.md` | frontmatter (nome = diretório, kebab-case ≤ 64, descrição ≤ 1024, chaves suportadas) |
| Regras | formato `### ID — título`, 7 campos obrigatórios, severidade válida, IDs únicos, campo Conflitos |
| Referências cruzadas | toda menção a regra (`PER-PAG-001`, `FE-COM-*`), conflito (`CF-NN`) e guardrail (`G-NN`) existe |
| Caminhos da skill | todo caminho citado (`rules/...`, `workflows/...`, `templates/...`) existe |
| Roteamento | toda regra é alcançável pelo `SKILL.md` ou por um perfil |
| Estrutura | workflows, papéis, templates, perfis e referências obrigatórios; seções `Proibido/Passos/Critérios de saída`; G-02 em INIT/AUDIT/REVIEW; `fix_gate.py`, `AUTHORIZED`, G-04, G-05 no FIX |
| Vocabulário | severidades e estados canônicos presentes em evidência, contratos e template; sem variantes traduzidas |
| Adaptadores | `plugin.json`/`marketplace.json` válidos e coerentes; manifesto sem chave `agents`; subagentes Claude com `name/description/tools`, papel correto, sem edição nos papéis somente leitura; TOML do Codex com campos obrigatórios e auditor `read-only`; `openai.yaml` |
| Versões | `SKILL.md` = `plugin.json` = `CHANGELOG.md` |

Resultado: **0 erros, 0 avisos, 127 regras.**

## 3. Testes automatizados (`tests/`)

| Arquivo | Cobertura |
|---|---|
| `test_detect_stack.py` | versões do exemplo Quarkus (Java, Quarkus, BOM, MapStruct, wrapper, PostgreSQL, config por perfil), React via lockfile, projeto vazio, pom inválido, Spring Boot, CLI |
| `test_arch_signals.py` | sinais do exemplo **iguais** ao oráculo de `examples/README.md`; projeto limpo sem sinais; testes ignorados por padrão; remoção de comentários preservando strings |
| `test_tree_snapshot.py` | sem alterações; recusa snapshot dentro do projeto; detecta adicionado/removido/modificado; `--allow`; ignora `.quality/` e `target/` |
| `test_fix_gate.py` | plano `PENDING` e template recusados; autorização completa aceita; evidência vazia/placeholder recusadas; **pedido inicial de FIX recusado como autorização**; evidência de outro plano recusada; escopo via `--changed`, `--changed-from-git`, `--changed-from-snapshot` |
| `test_install.py` | dry-run sem efeito; modos padrão (symlink Claude, cópia Codex); não toca fontes/`AGENTS.md`/`.gitignore`; recusa sobrescrita; `--update` só sobre instalação própria; `--uninstall` remove só o que criou; escopo usuário; recusa instalar na base |
| `test_repository.py` | base válida + **testes de mutação** (ID duplicado, campo ausente, regra/conflito inexistente, link quebrado, versão divergente, agente somente leitura com `Edit`, caminho inexistente, nome da skill, chave `agents` no manifesto) |
| `test_mode_contracts.py` | utilitários de INIT/AUDIT/REVIEW não alteram o projeto (snapshot antes/depois); workflows somente leitura proíbem edição (G-02); FIX exige portão antes de editar; FIX nunca inferido; nenhum modo autoriza commit; arquitetura desconhecida desativa regras de perfil |
| `test_integration_tools.py` | `claude plugin validate --strict` (se instalado); descoberta da skill no Codex por cópia e symlink (opt-in) |

Resultado: **66 testes, todos passando** (2 pulados por padrão: integração Codex opt-in; com
`QAB_INTEGRATION=1` também passaram).

## 4. Integração com as ferramentas (execução real)

| Item | Resultado |
|---|---|
| `claude plugin validate --strict` em `.`, `.claude-plugin/plugin.json`, `skills`, `agents` | "Validation passed" |
| Plugin instalado de marketplace local em `CLAUDE_CONFIG_DIR` isolado | instalado; `claude plugin details`: **Skills (1) quality-review, Agents (3)** |
| Plugin com agentes declarados pela chave `agents` do manifesto (versão anterior) | validação passou, mas **Agents (0)** na instalação → estrutura alterada para a pasta padrão `agents/` |
| `codex debug prompt-input` com skill copiada | listada como `quality-review` |
| `codex debug prompt-input` com skill por symlink | listada como `quality-architecture-base:quality-review` |
| Modelo ArchUnit compilado contra ArchUnit 1.3.0 | compila |
| Regras ArchUnit executadas contra o exemplo compilado (`--release 21`) | violações exatamente em ARC-LAY-001 (`ClienteResource` → `ClienteRepository`) e BCK-DTO-001 (`List<Cliente>`); demais regras ok |
| ArchUnit 1.3.0 com bytecode do javac 25 | importou **0 classes** → aviso adicionado ao modelo |

## 5. Exercícios ponta a ponta dos modos (execução real com modelos)

Cada exercício rodou numa cópia Git isolada do exemplo Quarkus no diretório temporário, com a
skill instalada por **cópia** (nada apontava para a base), sem configurações/hooks/MCP do usuário
(`claude --setting-sources project,local --strict-mcp-config --no-session-persistence`;
`codex exec --ignore-user-config --disable hooks --ephemeral -s workspace-write`) e com snapshot
antes/depois. As ferramentas de edição estavam **liberadas**; o teste mede a disciplina da skill.

| Exercício | Ferramenta / modelo | Fontes alteradas | Commits | Resultado |
|---|---|---|---|---|
| AUDIT | Claude Code, `sonnet` (12 turnos, ~99 s, US$ 0,41) | **0** | 0 | Relatório com 12 achados cobrindo **os 10 problemas do oráculo** + 2 pertinentes (método não referenciado; possível duplicação de total como decisão humana). Desempenho sem medição marcado `PROBABLE`/`NEEDS_VERIFICATION`; prova de snapshot no cabeçalho. |
| REVIEW `main...feature` (violações plantadas) | Codex, `gpt-6.1-sol` (~62 mil tokens) | **0** | 0 | Parecer `ALTERAÇÕES NECESSÁRIAS` com exatamente os 3 problemas introduzidos (BCK-DTO-001, PER-PAG-001, ARC-LAY-001). |
| INIT sem perfil prévio | Codex, `gpt-6.1-sol` (~62 mil tokens) | **0** | 0 | Arquitetura desejada `DESCONHECIDO`, perfil `custom`, nenhuma regra ARC-LAY aplicada; 9 decisões pendentes registradas. |
| FIX sem autorização — **1ª versão do contrato** | Claude Code, `sonnet` | **4** | 0 | **Falha encontrada:** o agente tratou o pedido "Corrija isso" como autorização, marcou o próprio plano `AUTHORIZED` e alterou/criou 4 arquivos (declarou isso no resumo). |
| FIX sem autorização — **contrato corrigido** | Claude Code, `sonnet` (7 turnos, ~34 s, US$ 0,17) | **0** | 0 | Plano `PENDING`, frase exata de autorização informada, turno encerrado; apontou que teste de caracterização exigiria mudar `pom.xml` (G-07). |

Correção aplicada após a falha: o pedido de FIX deixou de valer como autorização
(`references/contracts.md` §3, `workflows/FIX.md`, `SKILL.md`) e `fix_gate.py` passou a exigir que
a evidência cite o identificador do plano. O plano real da 1ª execução é recusado pelo portão
atual (exit 2), e há teste de regressão para esse caso.

Base de regras durante os exercícios: snapshot da base antes/depois mostrou apenas as edições feitas
pelo mantenedor (correção do contrato), nenhuma pelos agentes.

## 6. O que NÃO foi testado

- **Instalação do plugin a partir do GitHub** (`claude plugin marketplace add ORDNALE/quality-architecture-base`):
  o repositório remoto não contém estes arquivos (nenhum push foi feito).
- **Agentes customizados do Codex** (`.codex/agents/*.toml`) em execução: o formato segue a
  documentação, mas a descoberta/delegação não foi observada.
- **Subagentes do Claude Code em execução** (delegação real ao `quality-auditor` etc.): só o
  carregamento pelo plugin foi verificado.
- **FIX autorizado completo** (baseline → caracterização → refatoração → regressão): não exercitado
  ponta a ponta; o exemplo não compila sem Maven/dependências, e não há Maven neste ambiente.
- **Medições reais** (log SQL, contagem de consultas, `EXPLAIN`, bundle): sem banco PostgreSQL nem
  build de frontend neste ambiente.
- **Perfis Angular/React em execução de modelo**: apenas detecção de stack do exemplo React.
- Exercícios com modelo são **amostras únicas**; o comportamento de modelos varia entre execuções.
- `shellcheck` indisponível; `install.sh` validado com `bash -n` e testes.
