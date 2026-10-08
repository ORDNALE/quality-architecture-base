# Regras de frontend — React

Confirme a versão de `react`/`react-dom`, o bundler e se o React Compiler está ativo
(perfil §2, `profiles/stack/react.md`) antes de recomendar.

### FE-RX-001 — `React.lazy` + `Suspense` por rota/funcionalidade

- **Aplica-se quando:** React SPA com roteamento.
- **Verificar:** todas as rotas importadas estaticamente; ou `lazy` em componentes pequenos/críticos causando cascata de carregamentos; `Suspense` sem fallback adequado.
- **Evidência mínima:** E2 (chunks do build) / E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** CF-04; frameworks (Next.js, Remix/React Router com data APIs) têm divisão própria.
- **Correção preferida:** `lazy` no nível de rota/funcionalidade com fallback e preload em hover/intenção quando útil.
- **Conflitos:** CF-04

### FE-RX-002 — Efeitos corretos: dependências, limpeza e corridas

- **Aplica-se quando:** `useEffect`/`useLayoutEffect`.
- **Verificar:** dependências omitidas/supressão de `react-hooks/exhaustive-deps`; busca de dados sem cancelamento (`AbortController`) ou sem ignorar respostas obsoletas; efeitos que só derivam estado (deveria ser cálculo no render); listeners/timers sem limpeza.
- **Evidência mínima:** E3; E2 (ESLint `react-hooks`).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** StrictMode duplica efeitos apenas em desenvolvimento.
- **Correção preferida:** limpeza no retorno do efeito; biblioteca de server state se o projeto já usa.
- **Conflitos:** nenhum conhecido

### FE-RX-003 — Estado no nível certo e sem duplicação

- **Aplica-se quando:** React.
- **Verificar:** estado global para dados locais; estado derivado armazenado (e dessincronizado); server state copiado para estado local/global manualmente.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** —
- **Correção preferida:** colocar o estado onde é usado; derivar no render; usar a biblioteca de server state existente.
- **Conflitos:** CF-05, CF-14

### FE-RX-004 — Renderizações desnecessárias medidas

- **Aplica-se quando:** telas lentas, listas grandes, formulários complexos.
- **Verificar:** valor de Context recriado a cada render atingindo muitos consumidores; props instáveis anulando `memo`; componentes pesados re-renderizando a cada tecla.
- **Evidência mínima:** E1 (React DevTools Profiler) para CONFIRMED.
- **Severidade base:** LOW (MEDIUM medido)
- **Falsos positivos / cuidados:** re-render barato não é problema.
- **Correção preferida:** dividir contexto, mover estado para baixo, isolar componentes pesados.
- **Conflitos:** CF-14

### FE-RX-005 — Memoização somente justificada

- **Aplica-se quando:** React.
- **Verificar:** `useMemo`/`useCallback`/`memo` aplicados indiscriminadamente sem medição; ou ausência de memoização onde o profiler mostra custo.
- **Evidência mínima:** E1 para recomendar adicionar; E3 para apontar excesso (`LOW`).
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** com React Compiler ativo, memoização manual é em grande parte desnecessária — confirme se está habilitado no build.
- **Correção preferida:** memoizar apenas cálculos caros ou valores passados a componentes memoizados.
- **Conflitos:** CF-14

### FE-RX-006 — Chaves estáveis em listas

- **Aplica-se quando:** renderização de listas.
- **Verificar:** `key={index}` em listas que reordenam/inserem/removem; chaves aleatórias geradas no render.
- **Evidência mínima:** E3.
- **Severidade base:** LOW (MEDIUM se causa estado trocado entre itens)
- **Falsos positivos / cuidados:** listas estáticas.
- **Correção preferida:** identificador estável do dado.
- **Conflitos:** nenhum conhecido
