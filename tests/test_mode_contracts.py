"""Garantias verificáveis sem executar um modelo de IA.

- Os utilitários usados em INIT/AUDIT/REVIEW não alteram o projeto analisado.
- FIX exige autorização: plano pendente é recusado; os workflows tornam o portão obrigatório.
- AUDIT/REVIEW/INIT proíbem edição de fontes; nenhum modo autoriza commit/push.
"""

import unittest

from _helpers import QUARKUS_SAMPLE, REACT_SAMPLE, SKILL, TempDirMixin, run_script


class ReadOnlyToolsTest(TempDirMixin, unittest.TestCase):
    def test_detection_tools_do_not_modify_project(self):
        for sample in (QUARKUS_SAMPLE, REACT_SAMPLE):
            with self.subTest(sample=sample.name):
                project = self.copy_example(sample, sample.name)
                snap = self.tmp / f"{sample.name}.json"
                self.assertEqual(run_script("tree_snapshot.py", "create", project, "--output", snap).returncode, 0)
                for script in ("detect_stack.py", "arch_signals.py"):
                    for fmt in ("json", "markdown"):
                        self.assertEqual(run_script(script, project, "--format", fmt).returncode, 0)
                self.assertEqual(run_script("fix_gate.py", "check", SKILL / "templates/REFACTORING_PLAN.md").returncode, 2)
                proc = run_script("tree_snapshot.py", "compare", project, "--snapshot", snap)
                self.assertEqual(proc.returncode, 0, proc.stdout)
                self.assertEqual(sorted(p.name for p in project.rglob("__pycache__")), [])


class WorkflowContractTest(unittest.TestCase):
    def read(self, rel):
        return (SKILL / rel).read_text(encoding="utf-8")

    def test_read_only_modes_forbid_source_edits(self):
        for wf in ("INIT", "AUDIT", "REVIEW"):
            with self.subTest(workflow=wf):
                text = self.read(f"workflows/{wf}.md")
                proibido = text.split("## Proibido", 1)[1].split("## ", 1)[0]
                self.assertIn("G-02", proibido)

    def test_fix_requires_authorization_gate_before_editing(self):
        text = self.read("workflows/FIX.md")
        pre = text.split("## Pré-condições", 1)[1].split("## Proibido", 1)[0]
        self.assertIn("fix_gate.py", pre)
        self.assertIn("AUTHORIZED", pre)
        self.assertIn("pare", pre.lower())

    def test_skill_never_infers_fix(self):
        self.assertIn("Nunca** entre em FIX por inferência", self.read("SKILL.md"))

    def test_no_mode_allows_commit_or_push(self):
        safety = self.read("references/safety.md")
        self.assertIn("Nunca fazer `git commit`, `git push`", safety)
        for wf in ("FIX", "REVIEW"):
            self.assertRegex(self.read(f"workflows/{wf}.md"), r"(?i)commit")

    def test_unknown_architecture_disables_profile_rules(self):
        text = self.read("profiles/architecture/custom.md")
        self.assertIn("**Não** aplique `rules/architecture/layered.md`", text)


if __name__ == "__main__":
    unittest.main()
