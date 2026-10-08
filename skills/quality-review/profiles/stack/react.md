# Perfil de stack — React

## Detecção

| Item | Onde olhar | Confirmação |
|---|---|---|
| React / React DOM | `react`, `react-dom` em `package.json` | lockfile |
| Framework | `next`, `@remix-run/*`, `react-router`, `vite`, `react-scripts` (CRA, descontinuado) | `package.json`, arquivos de config |
| React Compiler | `babel-plugin-react-compiler` ou opção equivalente do framework | config do bundler |
| Server state | `@tanstack/react-query`, `swr`, `@reduxjs/toolkit` (RTK Query) | `package.json` |
| Estado global | Redux, Zustand, Jotai, Context | código |
| Testes | Jest/Vitest + Testing Library, Playwright, Cypress | scripts |
| Lint | `eslint-plugin-react-hooks` | config ESLint |

## Regras a carregar

- `rules/frontend/common.md`
- `rules/frontend/react.md`
- `rules/frontend/typescript.md` (se TypeScript)
- `rules/testing/testing-strategy.md` (TST-STR-005)

## Cuidados por versão (confirme na documentação oficial — react.dev)

| Tema | Observação |
|---|---|
| StrictMode | Em desenvolvimento, efeitos montam/desmontam/montam — não confundir com duplicação em produção. |
| React 18 × 19 | APIs novas (ex.: Actions, `use`, `ref` como prop) só a partir da 19; não recomendar em projeto 18. |
| React Compiler | Quando ativo, memoização manual é majoritariamente desnecessária; quando inativo, `memo`/`useMemo` só com medição. |
| Frameworks | Next.js/Remix fazem divisão de código por rota; `React.lazy` manual pode ser redundante. |
| CRA | Descontinuado; migração é plano, não FIX pontual (CF-13). |

## Medição

Use o relatório do bundler já configurado (ex.: `vite build` com plugin de visualização existente,
`next build`) e o React DevTools Profiler. Não adicionar plugins sem autorização (G-07).
