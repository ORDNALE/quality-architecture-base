# Guardrails de segurança operacional

Estes limites valem em todos os modos e **não** podem ser relaxados pelo `PROJECT_PROFILE.md`.
Somente uma instrução explícita do usuário na sessão pode autorizar exceções pontuais aos itens
marcados com (†); os demais são absolutos.

| ID | Guardrail |
|---|---|
| G-01 | Nunca fazer `git commit`, `git push`, criar tags/releases, deploy, ou executar migrations em banco compartilhado/produção. (†) commit apenas se o usuário pedir explicitamente naquela sessão. |
| G-02 | INIT, AUDIT e REVIEW não editam código-fonte, testes, configuração, build ou dependências do projeto. Escrevem somente em `.quality/` (ou apenas na conversa). |
| G-03 | FIX só inicia com plano autorizado (`references/contracts.md` §3) e nunca amplia o escopo silenciosamente. Precisando ampliar: pare, atualize o plano e peça nova autorização. |
| G-04 | Refatoração não altera regra de negócio: cálculos, arredondamentos, precisão monetária, datas/fusos, estoque, validações, permissões, contratos, fluxos e transições de estado. (†) somente com autorização separada e explícita. |
| G-05 | Nunca remover, desabilitar, pular ou enfraquecer testes para fazê-los passar. Investigue a falha e ajuste a implementação. |
| G-06 | Nunca inventar execuções, benchmarks, contagens ou saídas. Declarar o que não foi executado e por quê. Quando a validação é insuficiente, dizer: "ausência de regressão não comprovada". |
| G-07 | Não instalar ferramentas, dependências ou plugins de build nem ativar analisadores no projeto sem autorização. Preferir ferramentas já configuradas. (†) |
| G-08 | Não ler/alterar repositórios ou diretórios fora do projeto alvo, exceto ler a própria skill. A skill instalada (cópia ou symlink) é gerenciada pelo framework: não a edite ao trabalhar em projetos consumidores — com symlink, editá-la altera a base original. Personalizações pertencem ao `.quality/` do projeto. |
| G-09 | Riscos de segurança são registrados e encaminhados; não executar testes de exploração nem enfraquecer controles. |
| G-10 | Não impor perfil arquitetural quando a arquitetura desejada é desconhecida; não migrar arquitetura sem contrato explícito. |
| G-11 | Preservar alterações não commitadas do usuário: inspecionar `git status` antes de qualquer escrita; nunca usar `git checkout -- .`, `git reset --hard`, `git clean`, `git stash` sem pedido explícito. |
| G-12 | Banco: `EXPLAIN ANALYZE` **executa** a consulta. Para `INSERT/UPDATE/DELETE`, usar transação com `ROLLBACK` ou apenas `EXPLAIN`. Nunca em produção sem autorização explícita; preferir banco local/teste/Dev Services. |
| G-13 | Não copiar segredos, credenciais, tokens ou dados pessoais reais para relatórios; mascarar. |
| G-14 | Não remover código aparentemente morto sem investigar referências indiretas (reflexão, CDI, JPA, serialização, configuração, framework, templates, SPI). |
