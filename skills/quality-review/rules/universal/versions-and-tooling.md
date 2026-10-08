# Regras universais — versões, compatibilidade e ferramentas

### UNI-VER-001 — Versões efetivas conhecidas antes de recomendar

- **Aplica-se quando:** sempre; obrigatório em INIT e antes de qualquer recomendação dependente de versão.
- **Verificar:** versões efetivamente configuradas (não "a mais recente") de linguagem, build, framework, ORM, mapper, banco, frontend; versões gerenciadas por BOM resolvidas ou marcadas como não resolvidas.
- **Evidência mínima:** arquivo de build/configuração com linha (E3) ou saída de comando (`mvn help:effective-pom`, `npm ls`) (E2).
- **Severidade base:** INFO (a ausência bloqueia recomendações dependentes de versão)
- **Falsos positivos / cuidados:** documentação/README desatualizados não são fonte de versão (E5).
- **Correção preferida:** registrar no `PROJECT_PROFILE.md` com fonte; marcar `NÃO RESOLVIDA` quando não for possível resolver.
- **Conflitos:** nenhum conhecido

### UNI-VER-002 — Recomendações compatíveis com a versão em uso

- **Aplica-se quando:** sempre.
- **Verificar:** toda recomendação usa APIs/recursos disponíveis na versão real; quando houver dúvida, consultar a documentação oficial **da versão** e citar.
- **Evidência mínima:** referência à documentação oficial ou ao código-fonte da dependência na versão.
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** não presumir que reativo, mais novo ou mais complexo é superior (CF-13).
- **Correção preferida:** oferecer a alternativa compatível e, separadamente, o ganho de um upgrade como item de planejamento.
- **Conflitos:** CF-13

### UNI-VER-003 — Combinação de análise de IA com ferramentas existentes

- **Aplica-se quando:** AUDIT, REVIEW, FIX.
- **Verificar:** quais ferramentas já estão configuradas e executáveis (compilador, testes, ArchUnit, Checkstyle, PMD, SpotBugs, Sonar, ESLint, `tsc`, testes frontend/E2E) e se foram usadas para confirmar achados.
- **Evidência mínima:** comando executado e resultado (E2), ou motivo de não execução.
- **Severidade base:** INFO
- **Falsos positivos / cuidados:** não instalar nem ativar ferramentas novas sem autorização (G-07); sugerir adoção como recomendação.
- **Correção preferida:** usar o que existe; propor adoção incremental de ferramentas no relatório (ex.: ArchUnit a partir de `templates/archunit/`).
- **Conflitos:** nenhum conhecido
