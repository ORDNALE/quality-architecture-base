# Regras de frontend — Angular

Recursos variam muito entre versões do Angular. Confirme a versão de `@angular/core` (perfil §2) e
consulte `profiles/stack/angular.md` antes de recomendar.

### FE-NG-001 — Standalone components quando compatíveis

- **Aplica-se quando:** Angular com suporte a standalone (consulte a versão).
- **Verificar:** novos componentes criados em NgModules quando o projeto já adota standalone; mistura inconsistente sem plano.
- **Evidência mínima:** E3.
- **Severidade base:** INFO (LOW se o perfil exige standalone)
- **Falsos positivos / cuidados:** migrar em massa de NgModules não é FIX pequeno; use os schematics oficiais de migração da versão em um plano dedicado.
- **Correção preferida:** standalone em código novo/tocado; migração planejada.
- **Conflitos:** CF-09, CF-13

### FE-NG-002 — Rotas com carregamento sob demanda

- **Aplica-se quando:** Angular com roteamento.
- **Verificar:** funcionalidades importadas estaticamente nas rotas (`component:` de funcionalidades pesadas/pouco usadas) em vez de `loadComponent`/`loadChildren`; estratégia de preloading.
- **Evidência mínima:** E3 + E2 (chunks do build).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** FE-COM-001/CF-04.
- **Correção preferida:** `loadComponent`/`loadChildren` por funcionalidade; preloading seletivo.
- **Conflitos:** CF-04

### FE-NG-003 — Change detection e custo de templates

- **Aplica-se quando:** Angular.
- **Verificar:** chamadas de método/getters custosos em templates; componentes de listas grandes sem `OnPush` quando o projeto o adota; mutação de objetos impedindo `OnPush`.
- **Evidência mínima:** E3; E1 (Angular DevTools profiler) para CONFIRMED.
- **Severidade base:** LOW (MEDIUM medido)
- **Falsos positivos / cuidados:** mudar para `OnPush` exige imutabilidade/sinais — pode deixar a tela desatualizada se feito sem cuidado. Zoneless depende da versão e de estabilidade — não recomendar como correção pontual.
- **Correção preferida:** valores calculados (pipes puros, `computed`) em vez de métodos em template.
- **Conflitos:** CF-14

### FE-NG-004 — Rastreamento de itens em listas

- **Aplica-se quando:** `@for` (controle de fluxo embutido) ou `*ngFor`.
- **Verificar:** `@for` com `track` por `$index` ou pelo objeto em listas que mudam/reordenam; `*ngFor` de listas grandes sem `trackBy`.
- **Evidência mínima:** E3.
- **Severidade base:** LOW (MEDIUM em listas grandes atualizadas com frequência)
- **Falsos positivos / cuidados:** listas estáticas.
- **Correção preferida:** `track item.id` / `trackBy` por identificador estável.
- **Conflitos:** nenhum conhecido

### FE-NG-005 — RxJS: assinaturas, encadeamento e cancelamento

- **Aplica-se quando:** Angular com RxJS.
- **Verificar:** `subscribe` sem liberação em observables longos; `subscribe` aninhado; `mergeMap` em busca (deveria cancelar → `switchMap`); múltiplas assinaturas do mesmo HTTP sem compartilhamento.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** `HttpClient` completa após a resposta; `async` pipe libera automaticamente.
- **Correção preferida:** `async` pipe, `takeUntilDestroyed` (se disponível na versão), operadores de achatamento adequados, `shareReplay` com critério.
- **Conflitos:** CF-05

### FE-NG-006 — Signals e RxJS com papéis claros

- **Aplica-se quando:** versão do Angular com signals estáveis para o uso proposto.
- **Verificar:** estado duplicado em `BehaviorSubject` e `signal` ao mesmo tempo; `effect` usado para derivar estado (deveria ser `computed`); conversões repetidas sem necessidade.
- **Evidência mínima:** E3.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** APIs de signals mudaram de status (preview → estável) entre versões; confirme antes de recomendar.
- **Correção preferida:** signals para estado síncrono de UI, RxJS para fluxos assíncronos/eventos, interop oficial onde necessário.
- **Conflitos:** CF-13, CF-14

### FE-NG-007 — Separação entre serviços e componentes

- **Aplica-se quando:** Angular.
- **Verificar:** chamadas HTTP, regras de negócio e transformação de dados dentro de componentes; serviços que manipulam DOM.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** lógica puramente de apresentação pertence ao componente.
- **Correção preferida:** serviço de dados/fachada injetado; componente orquestra a apresentação.
- **Conflitos:** CF-14

### FE-NG-008 — Carregamento adiado de blocos pesados

- **Aplica-se quando:** versão do Angular com `@defer`.
- **Verificar:** componentes pesados abaixo da dobra/raramente exibidos carregados com a rota.
- **Evidência mínima:** E2 (tamanho de chunk) / E1.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** `@defer` em conteúdo visível imediatamente piora a percepção (CF-04).
- **Correção preferida:** `@defer` com gatilho adequado (`on viewport`, `on interaction`) e placeholder.
- **Conflitos:** CF-04
