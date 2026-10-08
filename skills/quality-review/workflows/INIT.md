# Workflow INIT — perfilar o projeto

**Objetivo:** detectar stack e versões, mapear a arquitetura existente, obter a arquitetura desejada,
descobrir testes e ferramentas e preparar `.quality/PROJECT_PROFILE.md` e as regras aplicáveis.

**Papel:** Architecture Auditor (`roles/ARCHITECTURE_AUDITOR.md`).

## Pré-condições

- Projeto alvo confirmado (raiz Git) e `git status --porcelain` registrado.
- `references/safety.md` lido.

## Proibido

- Editar código-fonte, testes, build, configuração ou dependências (G-02).
- Escolher a arquitetura desejada pelo usuário. A existente é observada; a desejada é **perguntada**.
- Instalar dependências para "conseguir detectar" versões (G-07).

## Passos

1. **Detecção de stack (E3/E2)**
   - Rode `python3 scripts/detect_stack.py <projeto> --format markdown`.
   - Confira manualmente os arquivos citados pelo script; ele lê versões **declaradas**.
   - Para versões gerenciadas por BOM ou faixas npm, use o lockfile ou comandos de resolução do
     perfil de stack, se disponíveis sem instalar nada. Caso contrário, marque `NÃO RESOLVIDA`.
2. **Arquitetura existente (E3/E4)**
   - Rode `python3 scripts/arch_signals.py <projeto> --format markdown` (Java).
   - Leia uma amostra representativa por unidade (ex.: 2–3 Resources, Services, Repositories,
     Entities, Mappers; módulos/rotas do frontend) para confirmar os sinais.
   - Descreva a arquitetura existente com evidência: padrões dominantes e desvios.
3. **Arquitetura desejada (decisão humana)**
   - Apresente ao usuário: arquitetura observada, perfis disponíveis (`profiles/architecture/`),
     e as perguntas objetivas que faltam (ex.: "Active Record é aceito?", "Service obrigatório?").
   - Se o usuário não decidir, registre `DESCONHECIDO` e siga `profiles/architecture/custom.md`.
4. **Testes e ferramentas**
   - Identifique comandos reais (wrapper Maven, scripts npm, CI) para compilar, testar, lint,
     ArchUnit, análise estática, log SQL. Não os execute se forem lentos/pesados sem combinar;
     uma compilação rápida é aceitável para confirmar que o projeto compila.
5. **Políticas**
   - Pergunte ou infira com evidência (marcando como inferido): DTOs/MapStruct, persistência,
     paginação (tamanho padrão/máximo, formato), exceções existentes, restrições, modo de operação.
6. **Gerar artefatos** (apenas se a saída em arquivo for aceita; senão, mostre na conversa)
   - `.quality/PROJECT_PROFILE.md` a partir de `templates/PROJECT_PROFILE.md`.
   - `.quality/ARCHITECTURE_CONTRACT.md` a partir de `templates/ARCHITECTURE_CONTRACT.md`, com
     `Status: RASCUNHO`, **somente** se a arquitetura desejada foi decidida.
   - `.quality/QUALITY_STATE.md` a partir de `templates/QUALITY_STATE.md`, com a decisão pendente
     se houver.
   - Se `.quality/` já existir, leia antes e atualize sem apagar decisões humanas.
7. **Encerramento**
   - Resuma: stack/versões (com fontes), arquitetura existente, arquitetura desejada ou decisões
     pendentes, regras que serão aplicadas, limitações.
   - Peça revisão humana do perfil (campo "Última revisão humana").

## Critérios de saída

- [ ] Cada versão tem fonte ou `NÃO RESOLVIDA`.
- [ ] Arquitetura existente descrita com evidência.
- [ ] Arquitetura desejada decidida pelo usuário ou `DESCONHECIDO` com perguntas registradas.
- [ ] Comandos de verificação reais listados.
- [ ] Nenhuma fonte alterada (`git status --porcelain` igual ao inicial, exceto `.quality/`).
