# Perfil de stack — TypeScript (frontend ou Node)

## Detecção

| Item | Onde olhar |
|---|---|
| Versão | `typescript` no lockfile |
| Rigor | `tsconfig*.json`: `strict`, `noImplicitAny`, `strictNullChecks`, `noUnusedLocals`, `noUnusedParameters` |
| Lint | `@typescript-eslint/*` |
| Contratos | geração a partir de OpenAPI (`openapi-generator`, `orval`, `openapi-typescript`) |

## Regras a carregar

- `rules/frontend/typescript.md`
- `rules/universal/*`

## Verificação

```bash
npx tsc --noEmit -p tsconfig.json      # requer dependências instaladas
```

Se `node_modules` não existir, instalar dependências altera o ambiente local do projeto
(`node_modules/`, possivelmente o lockfile): peça autorização ou declare a verificação como não
executada. Prefira `npm ci` (respeita o lockfile) quando autorizado.
