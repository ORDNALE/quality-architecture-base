# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e versionamento
semântico. Política de versões em [CONTRIBUTING.md](CONTRIBUTING.md#versionamento-e-releases).

## [0.1.0] — Não lançado

Primeira versão da base. Nenhuma tag foi criada.

### Adicionado

- Skill `quality-review` com roteamento sob demanda e modos INIT, AUDIT, REVIEW e FIX.
- Papéis Architecture Auditor, Controlled Refactorer e Regression/Performance Validator.
- Referências: contratos, critérios de evidência (E1–E5, estados, severidades), guardrails
  G-01…G-14, catálogo de conflitos CF-01…CF-16.
- Regras: universais (UNI-QUA, UNI-ERR, UNI-BRP, UNI-VER), arquitetura (ARC-GEN, ARC-LAY, ARC-HEX,
  ARC-MOD), backend (BCK-DTO, BCK-MAP, BCK-QRK), persistência (PER-N1, PER-LOAD, PER-QRY, PER-PAG,
  PER-TX, PER-IDX), performance (PRF), frontend (FE-COM, FE-NG, FE-RX, FE-TS) e testes (TST-STR,
  TST-TOOL).
- Perfis arquiteturais: layered, hexagonal, modular, custom (inclui arquitetura desconhecida).
- Perfis de stack: Java/Quarkus, PostgreSQL, Angular, React, TypeScript.
- Templates: PROJECT_PROFILE, ARCHITECTURE_CONTRACT, AUDIT_REPORT, REVIEW_REPORT, REFACTORING_PLAN,
  REGRESSION_REPORT, QUALITY_STATE e modelo ArchUnit para camadas.
- Scripts: `detect_stack.py`, `arch_signals.py`, `tree_snapshot.py`, `fix_gate.py`.
- Adaptadores: plugin e marketplace do Claude Code, subagentes Claude, metadados e agentes
  customizados do Codex, instalador `scripts/install.sh`.
- Validação: `scripts/validate_repo.py` e testes em `tests/`.
- Exemplos: `examples/quarkus-layered-sample`, `examples/react-sample`.
