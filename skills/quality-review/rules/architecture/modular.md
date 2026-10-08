# Regras de arquitetura — modular (monólito modular / módulos por funcionalidade)

Aplicam-se **somente** quando o perfil seleciona `profiles/architecture/modular.md` e o contrato
lista os módulos e suas APIs públicas. Dentro de cada módulo pode valer outro perfil (ex.: camadas);
o contrato indica qual.

### ARC-MOD-001 — Acesso entre módulos somente pela API pública

- **Aplica-se quando:** perfil modular.
- **Verificar:** imports de pacotes internos de outro módulo (`..internal..`, `..impl..`, repositórios e entidades alheios).
- **Evidência mínima:** E2 (ArchUnit, Maven multi-módulo, ESLint `no-restricted-imports`, dependency-cruiser) ou E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** módulo `shared/common` previsto no contrato.
- **Correção preferida:** expor operação na API pública do módulo dono.
- **Conflitos:** CF-10

### ARC-MOD-002 — Sem ciclos entre módulos

- **Aplica-se quando:** perfil modular.
- **Verificar:** ciclos de dependência entre módulos (complementa UNI-QUA-003).
- **Evidência mínima:** E2 ou E3 com o ciclo completo.
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** —
- **Correção preferida:** extrair o conceito compartilhado, eventos de domínio se o contrato prevê.
- **Conflitos:** CF-14

### ARC-MOD-003 — Propriedade de dados por módulo

- **Aplica-se quando:** perfil modular **e** contrato define propriedade de tabelas.
- **Verificar:** módulo consultando/alterando tabelas de outro módulo diretamente (JPQL/SQL/entidade alheia).
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM (HIGH se escreve em dados alheios)
- **Falsos positivos / cuidados:** relatórios/leitura analítica autorizados no contrato.
- **Correção preferida:** chamada à API do módulo dono ou projeção de leitura acordada.
- **Conflitos:** CF-03

### ARC-MOD-004 — Módulos de frontend por funcionalidade

- **Aplica-se quando:** perfil modular aplicado ao frontend.
- **Verificar:** funcionalidades importando componentes/serviços internos de outras funcionalidades em vez de `shared` ou da API pública da funcionalidade.
- **Evidência mínima:** E2/E3.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** —
- **Correção preferida:** mover para `shared` ou expor via barrel público definido no contrato.
- **Conflitos:** CF-04, CF-10
