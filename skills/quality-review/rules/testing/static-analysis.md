# Regras de testes — análise estática e verificação arquitetural

### TST-TOOL-001 — Ferramentas existentes usadas antes de propor novas

- **Aplica-se quando:** AUDIT, REVIEW, FIX.
- **Verificar:** quais ferramentas estão configuradas (plugins Maven, scripts `package.json`, CI) e executáveis localmente: compilador, testes, ArchUnit, Checkstyle, PMD, SpotBugs, Sonar, ESLint, `tsc`, Karma/Jest/Vitest, Playwright/Cypress.
- **Evidência mínima:** arquivos de build/CI (E3) e execução (E2) ou motivo de não execução.
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** não instalar/ativar tudo (G-07); ferramentas que exigem rede ou servidor (Sonar) podem não estar disponíveis — declarar.
- **Correção preferida:** recomendar adoção incremental, com o custo, como item do relatório.
- **Conflitos:** nenhum conhecido

### TST-TOOL-002 — Regras ArchUnit condicionadas ao perfil

- **Aplica-se quando:** perfil arquitetural selecionado **e** projeto Java com testes JUnit.
- **Verificar:** existência de testes arquiteturais que impeçam: Resource → Repository, Resource → `EntityManager`, ciclos entre pacotes, Entity em assinaturas de Resource (perfil layered); núcleo → adaptadores (hexagonal); acesso a internos de outro módulo (modular).
- **Evidência mínima:** E3.
- **Severidade base:** INFO (recomendação)
- **Falsos positivos / cuidados:** adicionar ArchUnit é dependência nova de teste (G-07); regras devem refletir o contrato **desejado** e as exceções registradas, senão quebram o build com violações conhecidas — use `FreezingArchRule` ou escopo restrito para dívida existente, se a versão suportar.
- **Correção preferida:** partir de `templates/archunit/LayeredArchitectureTest.java.template`, ajustando pacotes.
- **Conflitos:** CF-08, CF-09

### TST-TOOL-003 — Avisos do compilador considerados

- **Aplica-se quando:** sempre.
- **Verificar:** avisos de depreciação, unchecked, MapStruct (campos não mapeados), `tsc` com `strict` desligado/`any` implícito.
- **Evidência mínima:** E2 (saída do build).
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** ligar opções mais estritas pode gerar muitos erros — tratar como plano.
- **Correção preferida:** reportar avisos relevantes; ajustar configuração apenas com autorização.
- **Conflitos:** nenhum conhecido
