# Regras universais — erros, exceções e logs

### UNI-ERR-001 — Exceções engolidas

- **Aplica-se quando:** sempre.
- **Verificar:** `catch` vazio, `catch` que só loga e segue como se nada tivesse acontecido em fluxo que deveria falhar, `catch (Exception e) { return null; }`, promessas/observables sem tratamento de erro.
- **Evidência mínima:** E3 mostrando o fluxo após a exceção.
- **Severidade base:** HIGH em fluxos financeiros/transacionais; MEDIUM nos demais.
- **Falsos positivos / cuidados:** tentativas opcionais documentadas (ex.: limpeza best-effort) com log adequado.
- **Correção preferida:** propagar, converter para exceção de domínio ou tratar explicitamente; manter o status HTTP e a semântica de rollback atuais (CF-06).
- **Conflitos:** CF-06

### UNI-ERR-002 — Captura genérica que altera semântica

- **Aplica-se quando:** sempre.
- **Verificar:** `catch (Exception|Throwable)` que mascara erros de programação; captura de exceção dentro de método `@Transactional` impedindo rollback esperado; conversão de toda falha em 500 ou em 200.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM (HIGH se impede rollback)
- **Falsos positivos / cuidados:** pontos de fronteira (ExceptionMapper, handler global) que fazem captura genérica intencional.
- **Correção preferida:** capturar exceções específicas; centralizar mapeamento HTTP em `ExceptionMapper`/handler global.
- **Conflitos:** CF-06

### UNI-ERR-003 — Mapeamento consistente de erros na fronteira

- **Aplica-se quando:** projeto expõe API.
- **Verificar:** formatos de erro diferentes por endpoint, `try/catch` repetido em cada Resource, mensagens internas (stack trace, SQL) devolvidas ao cliente.
- **Evidência mínima:** E3.
- **Severidade base:** MEDIUM
- **Falsos positivos / cuidados:** mudar o formato de erro é mudança de contrato (CF-02); vazamento de detalhes internos → encaminhar à segurança.
- **Correção preferida:** handler central preservando os formatos atuais; mudanças de formato só com autorização.
- **Conflitos:** CF-02

### UNI-ERR-004 — Logs úteis, proporcionais e sem dados sensíveis

- **Aplica-se quando:** sempre.
- **Verificar:** ausência de log em falhas relevantes; log duplicado da mesma exceção em várias camadas; nível errado (erro esperado como `ERROR`); `System.out`/`console.log` em código de produção; concatenação cara em log de nível desabilitado; log dentro de laço quente; dados pessoais/segredos em log.
- **Evidência mínima:** E3.
- **Severidade base:** LOW (dados sensíveis → seção de segurança encaminhada)
- **Falsos positivos / cuidados:** logs de auditoria exigidos por negócio/regulação.
- **Correção preferida:** log uma vez na fronteira com contexto (IDs, não dados pessoais); usar o logger do framework.
- **Conflitos:** nenhum conhecido
