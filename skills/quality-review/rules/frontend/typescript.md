# Regras de frontend — TypeScript

### FE-TS-001 — Tipagem que protege contratos

- **Aplica-se quando:** projetos TypeScript.
- **Verificar:** `any` explícito/implícito em dados de API; tipos de DTO do frontend divergentes do backend; asserções (`as X`) que escondem incompatibilidades; `strict` desligado.
- **Evidência mínima:** E2 (`tsc --noEmit`, ESLint) ou E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** ligar `strict` em projeto existente gera muitos erros — plano incremental.
- **Correção preferida:** tipos de contrato centralizados (gerados de OpenAPI se o projeto já gera); `unknown` + validação na fronteira.
- **Conflitos:** CF-02

### FE-TS-002 — Valores monetários e datas no cliente

- **Aplica-se quando:** frontend que calcula ou formata dinheiro/quantidades/datas.
- **Verificar:** cálculos financeiros com `number` (ponto flutuante) no cliente; conversões de fuso implícitas com `Date`; formatação divergente da regra do backend.
- **Evidência mínima:** E3.
- **Severidade base:** HIGH se o valor calculado no cliente é enviado/persistido; MEDIUM se só exibido.
- **Falsos positivos / cuidados:** mudar o cálculo é regra de negócio (G-04).
- **Correção preferida:** cálculo autoritativo no backend; cliente apenas exibe e formata com `Intl`.
- **Conflitos:** CF-16

### FE-TS-003 — Código não utilizado e imports

- **Aplica-se quando:** projetos TypeScript.
- **Verificar:** exports, componentes, serviços e imports não usados apontados por `tsc`/ESLint (`noUnusedLocals`, `no-unused-vars`).
- **Evidência mínima:** E2.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** referências por string (rotas lazy, injeção por token, templates) — CF-07.
- **Correção preferida:** remover com testes verdes.
- **Conflitos:** CF-07
