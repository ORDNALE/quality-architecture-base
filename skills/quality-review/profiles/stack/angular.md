# Perfil de stack — Angular

## Detecção

| Item | Onde olhar | Confirmação |
|---|---|---|
| Angular | `@angular/core` em `package.json` (faixa declarada) | versão instalada no lockfile ou `npx ng version` (requer dependências instaladas) |
| TypeScript | `typescript` em `package.json`, `tsconfig.json` (`strict`) | `npx tsc -v` |
| RxJS | `rxjs` | lockfile |
| Builder | `angular.json` (`@angular-devkit/build-angular:application`/`browser`, esbuild/webpack) | — |
| Budgets | `angular.json` → `budgets` | saída de `ng build` |
| Testes | Karma/Jasmine, Jest, Vitest, Playwright, Cypress | scripts do `package.json` |
| Lint | `@angular-eslint/*`, `eslint.config.*` | — |

A faixa em `package.json` (`^17.3.0`) não é a versão instalada; use o lockfile
(`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`) como fonte.

## Regras a carregar

- `rules/frontend/common.md`
- `rules/frontend/angular.md`
- `rules/frontend/typescript.md`
- `rules/testing/testing-strategy.md` (TST-STR-005)

## Cuidados por versão (confirme na documentação oficial — angular.dev)

| Recurso | Observação |
|---|---|
| Standalone | Disponível a partir da linha 14; tornou-se o padrão de geração em versões posteriores. Verifique a versão antes de exigir. |
| Controle de fluxo `@if/@for/@switch` | Linha 17+; `@for` exige `track`. |
| `@defer` | Linha 17+. |
| Signals | Introduzidos na 16 (preview); o status de `signal`, `computed`, `effect` e APIs relacionadas (inputs/queries baseados em sinais) mudou ao longo das versões. |
| `takeUntilDestroyed` | `@angular/core/rxjs-interop`, linha 16+. |
| Zoneless | Experimental em versões iniciais; não recomendar como correção pontual. |
| Builder `application` (esbuild) | Padrão em projetos novos a partir da linha 17; projetos migrados podem usar o builder antigo. |

## Medição

```bash
npx ng build --configuration production --stats-json   # tamanhos de chunks/estatísticas, se o builder suportar
```

Use o que o projeto já tem (scripts, budgets). Não instale analisadores sem autorização (G-07).
