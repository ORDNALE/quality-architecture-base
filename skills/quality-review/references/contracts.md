# Contratos internos da quality-review

Este arquivo define os contratos que todos os workflows, papéis, regras, perfis e templates seguem.
Se outro arquivo contradisser este, este prevalece e a contradição deve ser corrigida.

## 1. Onde ficam os artefatos do projeto consumidor

A base **nunca** guarda dados de um projeto consumidor. Cada projeto mantém os próprios artefatos em
um diretório de qualidade, por padrão `.quality/` na raiz do projeto (configurável no perfil):

| Artefato | Caminho padrão no projeto consumidor | Template de origem |
|---|---|---|
| Perfil do projeto | `.quality/PROJECT_PROFILE.md` | `templates/PROJECT_PROFILE.md` |
| Contrato arquitetural | `.quality/ARCHITECTURE_CONTRACT.md` | `templates/ARCHITECTURE_CONTRACT.md` |
| Relatório de auditoria | `.quality/reports/AUDIT-<AAAA-MM-DD>[-<sufixo>].md` | `templates/AUDIT_REPORT.md` |
| Parecer de revisão | `.quality/reports/REVIEW-<AAAA-MM-DD>[-<sufixo>].md` | `templates/REVIEW_REPORT.md` |
| Plano de refatoração | `.quality/plans/PLAN-<AAAA-MM-DD>-<slug>.md` | `templates/REFACTORING_PLAN.md` |
| Relatório de regressão | `.quality/reports/REGRESSION-<AAAA-MM-DD>-<slug>.md` | `templates/REGRESSION_REPORT.md` |
| Estado da qualidade | `.quality/QUALITY_STATE.md` | `templates/QUALITY_STATE.md` |

Regras:

- O diretório `.quality/` contém documentação de qualidade, **não** código-fonte. Escrever nele não
  conta como "editar fontes", mas só é feito quando o modo permite (ver seção 3) e o usuário não pediu
  saída apenas na conversa.
- Se o projeto não quiser artefatos versionados, o perfil pode indicar `Saída: somente conversa`.
- Nenhum arquivo fora do projeto consumidor e fora de `.quality/` é criado pelos modos INIT, AUDIT e REVIEW.

## 2. Modos de operação

| Modo | Pode ler código | Pode escrever em `.quality/` | Pode editar fontes/testes/config | Pode executar comandos |
|---|---|---|---|---|
| INIT | Sim | Sim (perfil, contrato, estado) | **Não** | Somente leitura (ex.: `mvn -v`, `git log`, detecção de versões) |
| AUDIT | Sim | Sim (relatório, estado) | **Não** | Somente leitura e verificações que não alteram fontes (compilação, testes, linters existentes) |
| REVIEW | Sim | Sim (parecer) | **Não** | Somente leitura e verificações que não alteram fontes |
| FIX | Sim | Sim (plano, regressão, estado) | **Sim, apenas o escopo autorizado** | Build, testes e medições; nunca commit, push, deploy ou migration em ambiente real |

"Verificações que não alteram fontes" podem gerar diretórios de build (`target/`, `dist/`,
`node_modules/`). Isso é aceitável; alterar arquivos versionados não é.

Nenhum modo faz `git commit`, `git push`, criação de tags, deploy, execução de migrations em bancos
compartilhados ou alterações de produção.

## 3. Autorização para FIX

FIX só começa quando existe um plano (`templates/REFACTORING_PLAN.md`) cuja seção **Autorização**
contém, de forma verificável:

- `Status: AUTHORIZED`;
- `Autorizado por:` preenchido (pessoa responsável);
- `Evidência da autorização:` preenchida (citação literal da mensagem do usuário ou referência ao ticket);
- pelo menos um ID em `Achados autorizados:`;
- pelo menos um caminho/glob em `Arquivos autorizados:`;
- `Evidência da autorização:` contendo o **identificador do plano** (nome do arquivo sem `.md`,
  ex.: `PLAN-2026-10-08-cliente-resource-dto`).

Regras de autorização:

- **O pedido que inicia o FIX não é a autorização.** "Corrija F-001" pede um plano; não aprova
  escopo, arquivos nem riscos que o usuário ainda não viu.
- A autorização é uma mensagem do usuário **posterior à apresentação do plano**, que se refere a
  esse plano pelo identificador (ex.: "Autorizo PLAN-2026-10-08-cliente-resource-dto"). Ao
  apresentar o plano, o agente informa a frase exata e **encerra o turno**.
- O agente **não** pode marcar `AUTHORIZED` por iniciativa própria; só transcreve, literalmente,
  a autorização recebida. Alterar ou compor a citação é fabricação de evidência (G-06).
- Em execução não interativa (sem resposta humana possível), FIX termina com o plano `PENDING`.

O script `scripts/fix_gate.py` verifica esse bloco (inclusive a menção ao identificador do plano) e
confere se os arquivos alterados estão dentro do escopo autorizado.

## 4. Formato de regra

Cada regra fica em um arquivo de `rules/` e segue exatamente este formato:

```markdown
### <ID> — <Título curto>

- **Aplica-se quando:** <condições de perfil/stack; "sempre" para universais>
- **Verificar:** <o que inspecionar>
- **Evidência mínima:** <o que comprova o achado; ver references/evidence.md>
- **Severidade base:** <CRITICAL|HIGH|MEDIUM|LOW|INFO> (ajustável pelo impacto real)
- **Falsos positivos / cuidados:** <quando não é problema>
- **Correção preferida:** <opções, da menos invasiva para a mais invasiva>
- **Conflitos:** <IDs de conflito em references/conflict-resolution.md ou "nenhum conhecido">
```

IDs seguem o padrão `<ÁREA>-<SUBÁREA>-<NNN>` (ex.: `PER-N1-001`). Áreas válidas:
`UNI` (universal), `ARC` (arquitetura), `BCK` (backend), `PER` (persistência), `PRF` (performance),
`FE` (frontend), `TST` (testes). IDs são estáveis: uma regra removida deixa o ID reservado e é
registrada no `CHANGELOG.md`.

## 5. Formato de achado

Todo achado em relatório usa os campos abaixo (o template `templates/AUDIT_REPORT.md` os materializa):

| Campo | Conteúdo |
|---|---|
| ID | `F-NNN`, único no relatório |
| Severidade | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO` |
| Estado | `CONFIRMED`, `PROBABLE`, `NEEDS_VERIFICATION`, `NOT_REPRODUCED` |
| Local | arquivo e linhas (`caminho/Arquivo.java:42-57`) |
| Regra | ID da regra (ex.: `ARC-LAY-001`) |
| Descrição | o que está errado, em uma ou duas frases |
| Evidência | trecho, consulta, log, contagem, saída de ferramenta; tipo de evidência (ver `references/evidence.md`) |
| Impacto | efeito concreto (desempenho, manutenção, correção, segurança → encaminhar) |
| Correção sugerida | alternativa recomendada e alternativas descartadas |
| Conflitos | IDs de `references/conflict-resolution.md` aplicáveis |
| Risco de regressão | o que pode quebrar ao corrigir |
| Testes necessários | testes que precisam existir/passar antes e depois |

Severidade e estado são independentes: um achado pode ser `HIGH` e `NEEDS_VERIFICATION`.

## 6. Precedência de instruções

Da maior para a menor:

1. Instruções explícitas do usuário na sessão atual (inclusive limites de escopo).
2. Guardrails de segurança desta skill (`references/safety.md`) — não podem ser relaxados pelo perfil.
3. `ARCHITECTURE_CONTRACT.md` e `PROJECT_PROFILE.md` do projeto consumidor, incluindo exceções justificadas.
4. Perfis de arquitetura e de stack selecionados.
5. Regras universais e regras por área.

Quando um nível inferior é contrariado por um superior, o relatório registra a divergência e a
justificativa — nunca silenciosamente. Ver `references/conflict-resolution.md`.
