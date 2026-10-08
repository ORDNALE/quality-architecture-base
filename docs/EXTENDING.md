# Estendendo a base

Toda extensão acontece em `skills/quality-review/` (fonte única). Adaptadores e documentação apenas
referenciam. Depois de qualquer mudança, rode:

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
claude plugin validate . --strict   # se tiver Claude Code
```

## Adicionar uma regra

1. Escolha o arquivo da área em `rules/<área>/` (ou crie um novo arquivo coeso).
2. Use o formato de `references/contracts.md` §4, com **todos** os campos:

   ```markdown
   ### PER-QRY-NNN — Título curto

   - **Aplica-se quando:** ...
   - **Verificar:** ...
   - **Evidência mínima:** ...
   - **Severidade base:** MEDIUM
   - **Falsos positivos / cuidados:** ...
   - **Correção preferida:** ...
   - **Conflitos:** CF-03
   ```

3. ID: `<ÁREA>-<SUBÁREA>-<NNN>`, próximo número livre. Áreas: `UNI`, `ARC`, `BCK`, `PER`, `PRF`,
   `FE`, `TST`. IDs nunca são reaproveitados.
4. Se a regra for nova num arquivo novo, inclua o arquivo na tabela de roteamento do `SKILL.md` ou
   no perfil de stack que o carrega.
5. Registre no `CHANGELOG.md`.

O validador falha se: o ID estiver duplicado, faltar campo, a severidade for inválida, ou algum
arquivo citar um ID/conflito inexistente.

## Adicionar um conflito

1. Em `references/conflict-resolution.md`, adicione `### CF-NN — A × B` com tensão, resolução
   preferida e (se houver) o que é proibido.
2. Cite `CF-NN` no campo "Conflitos" das regras afetadas.

## Adicionar um perfil de stack (ex.: Spring Boot, Vue)

1. Crie `profiles/stack/<stack>.md` com: detecção (arquivos e comandos somente leitura), regras a
   carregar, cuidados por versão (sempre "confirme na documentação da versão"), ferramentas.
2. Crie regras específicas em `rules/<área>/<stack>.md` se necessário.
3. Se valer a pena, ensine `scripts/detect_stack.py` a reconhecer a stack e adicione um teste.
4. Adicione a linha correspondente na tabela de roteamento do `SKILL.md`.

## Adicionar um perfil arquitetural (ex.: CQRS, vertical slices)

1. `profiles/architecture/<nome>.md`: quando selecionar, contrato lógico, identificação no código,
   regras ativadas, parâmetros configuráveis.
2. `rules/architecture/<nome>.md` com prefixo de subárea próprio (ex.: `ARC-CQR-NNN`).
3. Atualize o template `PROJECT_PROFILE.md` (§3) e `docs/CONFIGURATION.md`.
4. Se possível, um modelo ArchUnit em `templates/archunit/`.

Regras úteis só para um projeto não entram aqui: ficam no `ARCHITECTURE_CONTRACT.md` desse projeto
com prefixo `PRJ-` (ver `profiles/architecture/custom.md`).

## Adicionar suporte a outra ferramenta de IA

1. Descubra o formato **atual** suportado pela versão instalada (documentação oficial, `--help`).
2. Crie `integrations/<ferramenta>/` com adaptadores finos que apontem para a skill.
3. Ensine `scripts/install.sh` os caminhos de instalação, se aplicável.
4. Documente em `docs/INSTALLATION.md` o que foi e o que não foi verificado.

## Scripts

- Python 3.10+, apenas biblioteca padrão, sem rede, sem escrita no projeto analisado.
- Saídas como sinais (E4) ou verificações (E2) — nunca "achados confirmados".
- Cada script novo precisa de testes em `tests/` usando os exemplos ou diretórios temporários.
