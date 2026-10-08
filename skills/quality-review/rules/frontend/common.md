# Regras de frontend — comuns (Angular, React e outros)

Desempenho de frontend se confirma com medição (relatório de bundle do build, DevTools/Lighthouse,
profiler do framework). Sem medição, achados de desempenho são hipóteses.

### FE-COM-001 — Lazy loading por rota/funcionalidade avaliado, não indiscriminado

- **Aplica-se quando:** SPA com múltiplas rotas/funcionalidades.
- **Verificar:** todas as funcionalidades no bundle inicial; ou, ao contrário, divisão excessiva (muitos chunks minúsculos, rotas principais lazy causando espera visível); ausência de preloading nas rotas mais usadas.
- **Evidência mínima:** E2/E1 (saída do build com tamanhos de chunks; waterfall de rede) para CONFIRMED; E3 para PROBABLE.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** apps pequenos; telas usadas logo após o login podem ficar no bundle inicial.
- **Correção preferida:** lazy por funcionalidade pouco usada/pesada; preloading seletivo; medir antes/depois (CF-04).
- **Conflitos:** CF-04

### FE-COM-002 — Bundle inicial e imports pesados

- **Aplica-se quando:** sempre.
- **Verificar:** importação de bibliotecas inteiras (utilitários, ícones, datas, gráficos) quando poucas funções são usadas; dependências pesadas no caminho inicial; avisos de orçamento (budgets) do build.
- **Evidência mínima:** E2 (relatório/estatísticas do build).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** tree-shaking pode já eliminar o código — só o relatório do build decide.
- **Correção preferida:** imports por módulo/função; carregamento dinâmico do recurso pesado.
- **Conflitos:** CF-04

### FE-COM-003 — Requisições duplicadas

- **Aplica-se quando:** sempre.
- **Verificar:** mesma requisição disparada várias vezes na inicialização (múltiplas assinaturas, componentes irmãos buscando o mesmo dado, efeitos sem controle).
- **Evidência mínima:** E1 (aba de rede) ou E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** React StrictMode executa efeitos duas vezes **apenas em desenvolvimento** — não é duplicação em produção.
- **Correção preferida:** compartilhar o resultado (serviço/estado/consulta com deduplicação).
- **Conflitos:** CF-05

### FE-COM-004 — Busca com debounce e cancelamento de respostas obsoletas

- **Aplica-se quando:** campos de busca/autocomplete/filtros que disparam requisições.
- **Verificar:** requisição a cada tecla; respostas antigas sobrescrevendo novas (condição de corrida); ausência de cancelamento (`switchMap`, `AbortController`).
- **Evidência mínima:** E3; E1 para CONFIRMED.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** debounce muito longo piora a percepção; ajuste com o time.
- **Correção preferida:** debounce + cancelamento + ignorar termos repetidos.
- **Conflitos:** CF-04

### FE-COM-005 — Paginação e filtros server-side para coleções grandes

- **Aplica-se quando:** listas/tabelas de coleções potencialmente grandes.
- **Verificar:** frontend carregando a coleção inteira e paginando/filtrando localmente; tabelas com paginação visual sobre lista completa.
- **Evidência mínima:** E3 (frontend + endpoint).
- **Severidade base:** HIGH
- **Falsos positivos / cuidados:** coordenar com o backend (PER-PAG-001); mudar para server-side altera contrato e UX (CF-11).
- **Correção preferida:** paginação/filtros server-side preservando estado na URL.
- **Conflitos:** CF-11

### FE-COM-006 — Cache de dados com invalidação

- **Aplica-se quando:** dados reutilizados entre telas.
- **Verificar:** dados buscados novamente a cada navegação sem necessidade; ou cache sem invalidação após escrita (tela mostra dado antigo).
- **Evidência mínima:** E3/E1.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** dados críticos (saldo, estoque) exigem frescor (CF-05).
- **Correção preferida:** mecanismo já existente no projeto (biblioteca de server state, serviço com cache) com invalidação nas mutações.
- **Conflitos:** CF-05

### FE-COM-007 — Virtualização de listas longas renderizadas

- **Aplica-se quando:** centenas ou mais de itens renderizados ao mesmo tempo, quando paginação não é adequada.
- **Verificar:** renderização de listas muito longas com rolagem lenta.
- **Evidência mínima:** E1 (profiler/FPS) para CONFIRMED.
- **Severidade base:** LOW (MEDIUM medido)
- **Falsos positivos / cuidados:** virtualização prejudica busca do navegador (Ctrl+F), impressão e alguns cenários de acessibilidade; prefira paginação quando possível.
- **Correção preferida:** CDK virtual scroll (Angular), bibliotecas de virtualização já presentes (React).
- **Conflitos:** CF-14

### FE-COM-008 — Vazamentos de memória

- **Aplica-se quando:** sempre.
- **Verificar:** assinaturas, listeners, timers, websockets e observers não liberados ao destruir componentes.
- **Evidência mínima:** E3; E1 (heap snapshots) para CONFIRMED.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** observables que completam sozinhos (ex.: `HttpClient`) não vazam.
- **Correção preferida:** liberação no ciclo de vida do framework.
- **Conflitos:** nenhum conhecido

### FE-COM-009 — Responsividade e esforço em dispositivos móveis

- **Aplica-se quando:** aplicações usadas em celular/tablet (ex.: vendedores, entregadores, estoque).
- **Verificar:** tabelas largas sem alternativa móvel; alvos de toque pequenos; formulários longos sem agrupamento; teclado inadequado (`inputmode`/`type` para números, telefone, e-mail); excesso de passos para tarefas frequentes.
- **Evidência mínima:** E3; teste em viewport móvel (E1).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** sistemas estritamente desktop registrados no perfil.
- **Correção preferida:** ajustes de layout/inputs; não redesenhar telas sem pedido.
- **Conflitos:** nenhum conhecido

### FE-COM-010 — Acessibilidade

- **Aplica-se quando:** sempre.
- **Verificar:** campos sem rótulo associado, controles não acessíveis por teclado, foco perdido em modais/troca de rota, contraste insuficiente, `aria-*` incorreto, imagens informativas sem texto alternativo.
- **Evidência mínima:** E3; E2 (linters de acessibilidade, auditoria automatizada).
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** ferramentas automatizadas não detectam tudo; registre o que não foi verificado.
- **Correção preferida:** elementos nativos semânticos antes de `aria-*`.
- **Conflitos:** nenhum conhecido

### FE-COM-011 — Navegação e estado preservados

- **Aplica-se quando:** listas com filtros/paginação, fluxos com várias etapas.
- **Verificar:** filtros/página perdidos ao voltar; estado não refletido na URL quando compartilhável; recarga completa desnecessária.
- **Evidência mínima:** E3/E1.
- **Severidade base:** LOW
- **Falsos positivos / cuidados:** —
- **Correção preferida:** estado de lista em parâmetros de rota/consulta.
- **Conflitos:** nenhum conhecido
