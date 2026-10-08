import json
import shutil
import unittest

from _helpers import QUARKUS_SAMPLE, SKILL, TempDirMixin, git, run_script

import fix_gate

PENDING_PLAN = QUARKUS_SAMPLE / ".quality/plans/PLAN-2026-10-08-cliente-resource-dto.md"


def authorized_plan(files=("src/main/java/com/example/vendas/resource/ClienteResource.java", "src/test/java/**")):
    items = "\n".join(f"  - {f}" for f in files)
    return f"""# plano
<!-- qab:authorization:start -->
- Status: AUTHORIZED
- Autorizado por: Responsável Técnico
- Data: 2026-10-08
- Evidência da autorização: "Autorizo PLAN-2026-10-08-teste" (mensagem do usuário após ver o plano)
- Achados autorizados: F-001, F-002
- Arquivos autorizados:
{items}
- Alteração de regra de negócio autorizada: NÃO
<!-- qab:authorization:end -->
"""


class FixGateTest(TempDirMixin, unittest.TestCase):
    def plan(self, text, name="PLAN-2026-10-08-teste.md"):
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_example_pending_plan_is_rejected(self):
        proc = run_script("fix_gate.py", "check", PENDING_PLAN)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("PENDING", proc.stdout)

    def test_blank_template_is_rejected(self):
        proc = run_script("fix_gate.py", "check", SKILL / "templates/REFACTORING_PLAN.md")
        self.assertEqual(proc.returncode, 2)

    def test_complete_authorization_passes(self):
        proc = run_script("fix_gate.py", "check", self.plan(authorized_plan()), "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        data = json.loads(proc.stdout)
        self.assertEqual(data["authorization"]["findings"], ["F-001", "F-002"])
        self.assertEqual(len(data["authorization"]["files"]), 2)

    def test_authorized_without_evidence_is_rejected(self):
        text = authorized_plan().replace('"Autorizo PLAN-2026-10-08-teste" (mensagem do usuário após ver o plano)', "")
        proc = run_script("fix_gate.py", "check", self.plan(text))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Evidência da autorização", proc.stdout)

    def test_initial_fix_request_is_not_authorization(self):
        # Reproduz o caso real observado no teste ponta a ponta: o agente usou o pedido inicial
        # ("FIX F-001 ... Corrija isso.") como evidência e marcou AUTHORIZED por conta própria.
        text = authorized_plan().replace(
            '"Autorizo PLAN-2026-10-08-teste" (mensagem do usuário após ver o plano)',
            '"FIX F-001: o ClienteResource acessa o ClienteRepository diretamente. Corrija isso."')
        proc = run_script("fix_gate.py", "check", self.plan(text))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("não cita o identificador do plano", proc.stdout)

    def test_evidence_must_cite_this_plan_not_another(self):
        proc = run_script("fix_gate.py", "check", self.plan(authorized_plan(), name="PLAN-2026-10-09-outro.md"))
        self.assertEqual(proc.returncode, 2)

    def test_placeholder_counts_as_empty(self):
        text = authorized_plan().replace("Responsável Técnico", "<nome>")
        self.assertEqual(run_script("fix_gate.py", "check", self.plan(text)).returncode, 2)

    def test_missing_block_is_usage_error(self):
        self.assertEqual(run_script("fix_gate.py", "check", self.plan("# sem bloco\n")).returncode, 1)

    def test_changed_files_in_scope_and_out_of_scope(self):
        plan = self.plan(authorized_plan())
        ok = run_script("fix_gate.py", "check", plan, "--changed", "src/main/java/com/example/vendas/resource/ClienteResource.java",
                        "--changed", "src/test/java/com/example/vendas/ClienteResourceTest.java", "--changed", ".quality/reports/R.md")
        self.assertEqual(ok.returncode, 0, ok.stdout)
        bad = run_script("fix_gate.py", "check", plan, "--changed", "src/main/java/com/example/vendas/service/VendaService.java")
        self.assertEqual(bad.returncode, 3)
        self.assertIn("FORA DO ESCOPO", bad.stdout)

    @unittest.skipUnless(shutil.which("git"), "git indisponível")
    def test_changed_from_git(self):
        project = self.copy_example(QUARKUS_SAMPLE)
        git(project, "init", "-q")
        git(project, "add", "-A")
        git(project, "commit", "-qm", "baseline")
        (project / "src/main/java/com/example/vendas/resource/ClienteResource.java").write_text("// fix\n")
        plan = self.plan(authorized_plan())
        self.assertEqual(run_script("fix_gate.py", "check", plan, "--project", project, "--changed-from-git").returncode, 0)
        (project / "src/main/java/com/example/vendas/service/VendaService.java").write_text("// fora\n")
        self.assertEqual(run_script("fix_gate.py", "check", plan, "--project", project, "--changed-from-git").returncode, 3)

    def test_changed_from_snapshot_ignores_preexisting_user_changes(self):
        project = self.copy_example(QUARKUS_SAMPLE)
        (project / "README-local.md").write_text("alteração do usuário anterior ao FIX")
        snap = self.tmp / "baseline.json"
        self.assertEqual(run_script("tree_snapshot.py", "create", project, "--output", snap).returncode, 0)
        (project / "src/main/java/com/example/vendas/resource/ClienteResource.java").write_text("// fix\n")
        proc = run_script("fix_gate.py", "check", self.plan(authorized_plan()), "--project", project, "--changed-from-snapshot", snap)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_parse_handles_inline_comment_in_status(self):
        auth = fix_gate.parse_authorization(authorized_plan().replace("Status: AUTHORIZED", "Status: AUTHORIZED <!-- ok -->"))
        self.assertEqual(auth.status, "AUTHORIZED")


if __name__ == "__main__":
    unittest.main()
