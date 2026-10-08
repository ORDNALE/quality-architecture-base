# Contribuindo

Obrigado por melhorar a Quality Architecture Base. Este guia vale para pessoas e agentes de IA.

## Princípios

- **Fonte única:** regras, perfis, workflows, papéis e templates ficam em `skills/quality-review/`.
  Adaptadores (`integrations/`, `.claude-plugin/`) e documentação só apontam para eles.
- **Neutralidade de fornecedor:** nada no núcleo depende de Claude Code ou Codex.
- **Evidência acima de opinião:** regras novas dizem o que comprova o problema e quando ele *não* é
  problema (falsos positivos).
- **Sem invenção:** não documente comandos, sintaxes ou suporte que não foram verificados; marque o
  que não foi testado.
- **Compatibilidade de versão:** recomendações dependentes de versão dizem para confirmar na
  documentação da versão em uso.

## Fluxo

1. Abra uma issue descrevendo o problema ou a regra proposta (com exemplo de código).
2. Crie um branch: `feat/<assunto>`, `fix/<assunto>`, `docs/<assunto>`, `rule/<ID>`.
3. Faça a mudança seguindo [docs/EXTENDING.md](docs/EXTENDING.md).
4. Valide localmente:

   ```bash
   python3 scripts/validate_repo.py
   python3 -m unittest discover -s tests -v
   claude plugin validate . --strict      # se tiver Claude Code instalado
   ```

5. Atualize o `CHANGELOG.md` (seção "Não lançado").
6. Abra o pull request explicando motivação, impacto em projetos consumidores e o que foi testado.

## Convenções

| Item | Convenção |
|---|---|
| Idioma | português brasileiro no conteúdo; identificadores e IDs em ASCII |
| IDs de regra | `<ÁREA>-<SUBÁREA>-<NNN>`, estáveis, nunca reaproveitados |
| IDs de conflito | `CF-NN` |
| Scripts | Python 3.10+, biblioteca padrão, sem rede, nunca gravam no projeto analisado |
| Exemplos | `examples/` são oráculos de teste; mudanças exigem atualizar `examples/README.md` e testes |
| Commits | mensagens no imperativo, ex.: `rule: adiciona PER-QRY-NNN para subconsultas correlacionadas` |

## Versionamento e releases

- Versionamento semântico (`MAJOR.MINOR.PATCH`) da base como um todo:
  - **MAJOR:** remoção/renomeação de IDs de regra, mudança incompatível em templates ou contratos
    (ex.: formato do bloco de autorização), mudança de estrutura de instalação.
  - **MINOR:** novas regras, perfis, conflitos, modos ou adaptadores compatíveis.
  - **PATCH:** correções de texto, falsos positivos, scripts sem mudança de interface.
- A versão aparece em três lugares que devem coincidir: `skills/quality-review/SKILL.md`
  (`metadata.version`), `.claude-plugin/plugin.json` (`version`) e o topo do `CHANGELOG.md`.
  O validador confere isso.
- Release: atualizar o `CHANGELOG.md`, criar a tag `vX.Y.Z` no commit da release e publicar a
  release no GitHub com o trecho do changelog. Projetos consumidores fixam versões com
  `git checkout vX.Y.Z` antes de instalar por cópia.
- O plugin do Claude Code só é atualizado para quem já o instalou quando `version` muda no
  `plugin.json`.

## O que não aceitamos

- Regras que impõem uma arquitetura sem passar pelo perfil do projeto.
- Recomendações universais sem condição de aplicação (ex.: "sempre use JOIN FETCH").
- Benchmarks ou resultados não reproduzíveis.
- Duplicação do agente de segurança: riscos de segurança são apenas registrados e encaminhados.
