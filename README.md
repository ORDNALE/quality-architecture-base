# Quality Architecture Base

> Reusable AI-powered toolkit for software architecture, code quality, performance auditing, and safe refactoring.

Base reutilizável de regras, perfis e fluxos de trabalho para que agentes de IA (**Claude Code** e
**Codex CLI**) auditem, revisem e refatorem projetos com segurança, seguindo a arquitetura que
**cada projeto** escolheu.

## Que problema resolve

Pedir a um agente "melhore a arquitetura" costuma gerar recomendações genéricas, refatorações
estéticas, `JOIN FETCH` que quebra paginação, DTOs que mudam o JSON da API ou "otimizações" sem
medição. A Quality Architecture Base dá ao agente:

- **regras explícitas** com critérios de evidência (o que é fato, o que é hipótese);
- **perfil por projeto**: a arquitetura desejada é decidida por pessoas, nunca imposta;
- **modos separados**: auditar e revisar nunca editam código; refatorar exige autorização escrita;
- **resolução de conflitos** entre diretrizes (N+1 × paginação, DTO × contrato, cache × consistência…);
- **preservação de regra de negócio** com baseline, testes de caracterização e validação de regressão.

## Principais funcionalidades

| Recurso | Descrição |
|---|---|
| Skill `quality-review` | Ponto de entrada único, carrega regras sob demanda |
| Modos INIT · AUDIT · REVIEW · FIX | Perfilar, auditar (somente leitura), revisar diff (somente leitura), refatorar (com autorização) |
| Papéis | Architecture Auditor, Controlled Refactorer, Regression/Performance Validator (com subagentes nativos opcionais) |
| Regras | Qualidade universal, arquitetura, DTO/MapStruct, N+1, carregamento, paginação, índices, transações, performance, frontend, testes |
| Evidência | Severidade (CRITICAL…INFO) **e** estado (CONFIRMED, PROBABLE, NEEDS_VERIFICATION, NOT_REPRODUCED) |
| Scripts determinísticos | Detecção de stack, sinais de arquitetura, snapshot que prova "nada mudou", portão de autorização do FIX |
| Templates | Perfil do projeto, contrato arquitetural, relatórios de auditoria/revisão/regressão, plano de refatoração, estado da qualidade, ArchUnit |

## Tecnologias e arquiteturas

- **Arquiteturas:** camadas (Resource → Service → Repository → Entity), hexagonal, modular e personalizada.
- **Backend:** Java, Quarkus, Maven, Hibernate ORM/Panache, MapStruct, PostgreSQL.
- **Frontend:** Angular, React, TypeScript.

Perfis de tecnologia e de arquitetura são independentes e combináveis.

## Pré-requisitos

- Claude Code e/ou Codex CLI instalados e autenticados.
- Git.
- Python 3.10+ (scripts auxiliares; só biblioteca padrão).
- Bash (instalador).

## Instalação

```bash
git clone https://github.com/ORDNALE/quality-architecture-base.git
cd quality-architecture-base
```

### Claude Code

```bash
# Opção A — skill no projeto (comando /quality-review)
scripts/install.sh --tool claude --scope project --project /caminho/do/projeto --with-agents

# Opção B — para o seu usuário, em todos os projetos
scripts/install.sh --tool claude --scope user --with-agents

# Opção C — como plugin (comando /quality-architecture-base:quality-review)
claude plugin marketplace add ORDNALE/quality-architecture-base
claude plugin install quality-architecture-base@quality-architecture-base
```

### Codex CLI

```bash
# no projeto (cria .agents/skills/quality-review e .codex/agents/*.toml)
scripts/install.sh --tool codex --scope project --project /caminho/do/projeto --with-agents

# para o seu usuário (~/.agents/skills e ~/.codex/agents)
scripts/install.sh --tool codex --scope user --with-agents
```

Use `--dry-run` para ver o que será feito. O instalador não edita código nem configurações do
projeto. Detalhes, diferenças entre symlink e cópia e o que foi verificado:
[docs/INSTALLATION.md](docs/INSTALLATION.md).

## Uso

| Modo | Claude Code | Codex CLI | Efeito |
|---|---|---|---|
| INIT | `/quality-review INIT` | `$quality-review INIT` | Detecta stack/versões, pergunta a arquitetura desejada, propõe `.quality/PROJECT_PROFILE.md` |
| AUDIT | `/quality-review AUDIT` | `$quality-review AUDIT` | Relatório priorizado em `.quality/reports/` — **não edita fontes** |
| REVIEW | `/quality-review REVIEW main...HEAD` | `$quality-review REVIEW main...HEAD` | Parecer sobre o diff — **não edita fontes** |
| FIX | `/quality-review FIX F-001 F-002` | `$quality-review FIX F-001 F-002` | Cria plano; só altera código após autorização explícita registrada |

Com a instalação como plugin no Claude Code, use `/quality-architecture-base:quality-review`.
Também funciona em linguagem natural: "Use a skill quality-review para auditar o módulo de vendas".
Exemplos completos em [docs/USAGE.md](docs/USAGE.md).

## Selecionar a arquitetura e editar o perfil

1. Rode **INIT**. O agente mostra a arquitetura existente e pergunta qual é a **desejada**.
2. Revise `.quality/PROJECT_PROFILE.md` no seu projeto: versões, arquitetura desejada
   (`layered`, `hexagonal`, `modular`, `custom` ou `DESCONHECIDO`), políticas de DTO/MapStruct,
   persistência, paginação, testes, exceções justificadas e restrições.
3. Se a arquitetura desejada ficar `DESCONHECIDO`, nenhuma regra específica de arquitetura é
   aplicada até a decisão.

Guia completo: [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Atualizar e reutilizar

```bash
cd quality-architecture-base && git pull
# instalações por symlink (padrão no Claude) já refletem a atualização
# cópias (padrão no Codex) precisam ser reinstaladas:
scripts/install.sh --tool codex --scope project --project /caminho/do/projeto --with-agents --update
# plugin do Claude Code (o plugin só muda quando o campo "version" do plugin.json muda):
claude plugin marketplace update quality-architecture-base
claude plugin update quality-architecture-base@quality-architecture-base
```

Fixe uma versão com `git checkout <tag>` quando houver releases (ver [CHANGELOG.md](CHANGELOG.md)).

## Documentação

| Documento | Conteúdo |
|---|---|
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Instalação por ferramenta e escopo, verificação, remoção |
| [docs/USAGE.md](docs/USAGE.md) | Os quatro modos com exemplos e artefatos gerados |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Perfil do projeto, contrato, exceções, prioridades |
| [docs/RULE_CONFLICTS.md](docs/RULE_CONFLICTS.md) | Como a base trata diretrizes conflitantes |
| [docs/EXTENDING.md](docs/EXTENDING.md) | Novas regras, perfis, stacks e arquiteturas |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura interna da base |
| [docs/VALIDATION.md](docs/VALIDATION.md) | O que é testado e como validar |
| [docs/IMPLEMENTATION_STATE.md](docs/IMPLEMENTATION_STATE.md) | Estado da construção e pendências |
| [examples/README.md](examples/README.md) | Projetos de exemplo com problemas intencionais |

## Escopo e segurança

Esta base cobre arquitetura, qualidade, performance, testes e refatoração. **Não** é uma
ferramenta de auditoria de segurança: riscos de segurança percebidos são apenas registrados e
encaminhados para análise especializada.

## Contribuição

Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

Ainda não há licença definida pelo proprietário. Sem um arquivo `LICENSE`, este repositório **não**
é open source; a definição de licença é uma decisão pendente do proprietário.
