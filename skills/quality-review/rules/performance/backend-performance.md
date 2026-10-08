# Regras de performance — medição e backend

### PRF-MEA-001 — Afirmações de desempenho exigem medição registrada

- **Aplica-se quando:** qualquer achado ou critério de aceite de desempenho.
- **Verificar:** existe medição com ambiente, versão, volume de dados, aquecimento (JVM), número de execuções e comparação antes/depois nas mesmas condições.
- **Evidência mínima:** E1 completa. Sem ela, o achado é hipótese.
- **Severidade base:** INFO (procedimento)
- **Falsos positivos / cuidados:** números de outra máquina/execução anterior são E5; tempos de modo dev (hot reload) não representam produção.
- **Correção preferida:** registrar "não medido" e o que seria necessário medir.
- **Conflitos:** nenhum conhecido

### PRF-MEA-002 — Contagem de consultas como verificação de regressão

- **Aplica-se quando:** correções de N+1/carregamento.
- **Verificar:** número de statements SQL para um cenário fixo (ex.: listar 20 vendas) antes e depois, via log SQL, estatísticas do Hibernate ou proxy de datasource já disponível no projeto.
- **Evidência mínima:** E1 com contagens antes/depois.
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** ativar estatísticas/log só em perfil de teste/dev; nomes de propriedades variam por versão.
- **Correção preferida:** teste automatizado que falha se a contagem crescer com o número de itens (TST-STR-004).
- **Conflitos:** nenhum conhecido

### PRF-CAC-001 — Cache com consistência definida

- **Aplica-se quando:** cache de aplicação (ex.: `@CacheResult`), HTTP, segundo nível do Hibernate, cache no cliente.
- **Verificar:** dados mutáveis em cache sem invalidação; chave sem escopo de usuário/tenant; cache de saldo/estoque/preço; TTL arbitrário sem decisão.
- **Evidência mínima:** E3.
- **Severidade base:** HIGH (dado incorreto/vazamento entre usuários → segurança encaminhada)
- **Falsos positivos / cuidados:** dados de referência imutáveis ou raramente alterados com invalidação explícita.
- **Correção preferida:** invalidação nos pontos de escrita, chave completa; ou remover o cache.
- **Conflitos:** CF-05

### PRF-IO-001 — Chamadas remotas sequenciais, sem timeout ou em laço

- **Aplica-se quando:** clientes HTTP/REST, mensageria, integrações.
- **Verificar:** chamada remota por item em laço; chamadas independentes feitas em série em caminho crítico; ausência de timeout configurado.
- **Evidência mínima:** E3; E1 para quantificar.
- **Severidade base:** MEDIUM (HIGH sem timeout em caminho crítico)
- **Falsos positivos / cuidados:** paralelizar muda ordem de efeitos colaterais e carga no serviço remoto.
- **Correção preferida:** endpoint em lote, timeout explícito; paralelismo só com efeitos independentes.
- **Conflitos:** CF-13

### PRF-MEM-001 — Grandes volumes em memória

- **Aplica-se quando:** relatórios, exportações, respostas grandes.
- **Verificar:** montagem de listas/arquivos inteiros em memória; respostas JSON enormes sem paginação/streaming.
- **Evidência mínima:** E3; E1 (heap/tempo).
- **Severidade base:** HIGH em volumes grandes.
- **Falsos positivos / cuidados:** ver PER-PAG-008.
- **Correção preferida:** paginação, lotes, streaming.
- **Conflitos:** CF-11

### PRF-ASY-001 — Reativo/assíncrono apenas com ganho demonstrado

- **Aplica-se quando:** propostas de migrar para reativo, virtual threads, mensageria.
- **Verificar:** se há gargalo medido que a mudança resolve e se a versão em uso suporta a abordagem.
- **Evidência mínima:** E1 do gargalo.
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** CF-13.
- **Correção preferida:** otimizar o gargalo medido com a menor mudança.
- **Conflitos:** CF-13
