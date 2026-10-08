# Regras de arquitetura — gerais (independentes do perfil)

Aplicam-se sempre, inclusive quando a arquitetura desejada é desconhecida. Regras específicas de
perfil ficam em `layered.md`, `hexagonal.md` e `modular.md` e **só** são aplicadas quando o
`PROJECT_PROFILE.md` seleciona o perfil correspondente.

### ARC-GEN-001 — Arquitetura desejada definida antes de regras de perfil

- **Aplica-se quando:** sempre.
- **Verificar:** o perfil registra arquitetura existente (observada, com evidência) e desejada (decisão humana); se a desejada for `DESCONHECIDO`, nenhuma regra `ARC-LAY-*`, `ARC-HEX-*` ou `ARC-MOD-*` foi aplicada.
- **Evidência mínima:** `PROJECT_PROFILE.md` §3.
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** a arquitetura existente **não** é automaticamente a desejada; padrões dominantes no código são indício, não decisão.
- **Correção preferida:** registrar a incerteza e pedir a decisão; enquanto isso, auditar apenas as áreas independentes de perfil.
- **Conflitos:** CF-09

### ARC-GEN-002 — Sem migração arquitetural implícita

- **Aplica-se quando:** sempre.
- **Verificar:** recomendações ou mudanças que convertem o projeto para outra arquitetura (ex.: camadas → hexagonal/Clean) sem contrato explícito; FIX que reorganiza pacotes além do autorizado.
- **Evidência mínima:** E3/diff.
- **Severidade base:** HIGH (em FIX/REVIEW)
- **Falsos positivos / cuidados:** migrações aprovadas no `ARCHITECTURE_CONTRACT.md` §6.
- **Correção preferida:** reduzir ao escopo autorizado; propor migração como plano separado.
- **Conflitos:** CF-09

### ARC-GEN-003 — Fronteiras definidas são respeitadas de forma consistente

- **Aplica-se quando:** existe contrato arquitetural aprovado.
- **Verificar:** dependências proibidas pela matriz do contrato; exceções aplicadas apenas onde registradas.
- **Evidência mínima:** E2 (ArchUnit/linters de import) ou E3 (`import` + uso).
- **Severidade base:** MEDIUM (ou a severidade base da regra de perfil violada, se maior)
- **Falsos positivos / cuidados:** testes podem depender de qualquer camada; código gerado.
- **Correção preferida:** ajustar a dependência; registrar exceção justificada quando a violação for intencional.
- **Conflitos:** CF-08

### ARC-GEN-004 — Sem delegação inútil criada para "cumprir" arquitetura

- **Aplica-se quando:** sempre.
- **Verificar:** Services/Repositories/Mappers criados apenas para repassar chamadas sem regra, sem transação, sem consulta e sem fronteira de teste.
- **Evidência mínima:** E3.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** o perfil pode exigir a camada mesmo quando fina (consistência, futura regra, transação). Nesse caso, registre exceção ou aceite como padrão do projeto — não é achado.
- **Correção preferida:** não criar a delegação; se já existe e o perfil não exige, sugerir simplificação como `LOW`.
- **Conflitos:** CF-14

### ARC-GEN-005 — Exceções arquiteturais explícitas e justificadas

- **Aplica-se quando:** sempre.
- **Verificar:** desvios intencionais estão registrados no perfil/contrato com justificativa, responsável, data e revisão; nenhuma exceção é presumida.
- **Evidência mínima:** perfil/contrato.
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** comentário no código (ex.: `// TODO arquitetura`) não é exceção registrada.
- **Correção preferida:** registrar a exceção ou corrigir o desvio.
- **Conflitos:** CF-08
