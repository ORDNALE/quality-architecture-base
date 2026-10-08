# Perfil arquitetural — modular

## Quando selecionar

Monólito modular ou organização por funcionalidade (backend ou frontend), com módulos e APIs
públicas listados no `ARCHITECTURE_CONTRACT.md`. Cada módulo pode adotar internamente outro perfil
(ex.: camadas); o contrato indica qual, e as regras desse perfil se aplicam dentro do módulo.

## Contrato lógico

```text
módulo A ──(API pública)──▶ módulo B
   │ interno: camadas/hexagonal conforme contrato
   └── dados próprios (tabelas/esquemas) — outros módulos não acessam diretamente
```

## Identificação

| Sinal | Exemplo |
|---|---|
| Maven multi-módulo | `<modules>` no `pom.xml` raiz |
| Pacotes por funcionalidade | `com.empresa.vendas`, `com.empresa.estoque` |
| API pública | pacote `api`/`spi`, classes `public` × `package-private`, barrels `index.ts` |
| Frontend | `src/app/features/<funcionalidade>` com rotas próprias |

## Regras ativadas

- `rules/architecture/general.md`
- `rules/architecture/modular.md`
- Regras do perfil interno de cada módulo (ex.: `rules/architecture/layered.md`).

## Parâmetros configuráveis

| Parâmetro | Padrão |
|---|---|
| Módulos compartilhados permitidos | `shared`/`common`, sem regra de negócio |
| Propriedade de tabelas por módulo (ARC-MOD-003) | não exigida até o contrato listar |
| Comunicação entre módulos | chamada síncrona à API pública; eventos somente se previstos |
