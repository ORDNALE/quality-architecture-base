import json
import unittest

from _helpers import QUARKUS_SAMPLE, TempDirMixin, run_script


class TreeSnapshotTest(TempDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.project = self.copy_example(QUARKUS_SAMPLE)
        self.snap = self.tmp / "snap.json"
        proc = run_script("tree_snapshot.py", "create", self.project, "--output", self.snap)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def compare(self, *extra):
        return run_script("tree_snapshot.py", "compare", self.project, "--snapshot", self.snap, "--format", "json", *extra)

    def test_no_changes(self):
        proc = self.compare()
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(json.loads(proc.stdout)["ok"])

    def test_refuses_snapshot_inside_project(self):
        proc = run_script("tree_snapshot.py", "create", self.project, "--output", self.project / "x.json")
        self.assertEqual(proc.returncode, 1)
        self.assertFalse((self.project / "x.json").exists())

    def test_detects_modified_added_removed(self):
        java = self.project / "src/main/java/com/example/vendas/resource/ClienteResource.java"
        java.write_text(java.read_text() + "\n// alterado\n")
        (self.project / "novo.txt").write_text("x")
        (self.project / "docker-compose.yml").unlink()
        proc = self.compare()
        self.assertEqual(proc.returncode, 3)
        data = json.loads(proc.stdout)["disallowed"]
        self.assertEqual(data["modified"], ["src/main/java/com/example/vendas/resource/ClienteResource.java"])
        self.assertEqual(data["added"], ["novo.txt"])
        self.assertEqual(data["removed"], ["docker-compose.yml"])

    def test_allow_globs(self):
        java = self.project / "src/main/java/com/example/vendas/resource/ClienteResource.java"
        java.write_text("// alterado\n")
        proc = self.compare("--allow", "src/main/java/**/resource/*.java")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["allowed"]["modified"], ["src/main/java/com/example/vendas/resource/ClienteResource.java"])

    def test_quality_dir_and_build_outputs_are_ignored(self):
        (self.project / ".quality/reports").mkdir(parents=True)
        (self.project / ".quality/reports/AUDIT-2026-10-08.md").write_text("relatório")
        (self.project / "target/classes").mkdir(parents=True)
        (self.project / "target/classes/A.class").write_bytes(b"\x00")
        self.assertEqual(self.compare().returncode, 0)


if __name__ == "__main__":
    unittest.main()
