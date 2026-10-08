import json
import unittest

from _helpers import QUARKUS_SAMPLE, REACT_SAMPLE, TempDirMixin, run_script

import detect_stack


def facts(report):
    return {(c.kind, f.key): f for c in report.components for f in c.facts}


class DetectStackQuarkusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = detect_stack.detect(QUARKUS_SAMPLE)
        cls.facts = facts(cls.report)

    def test_java_release_from_property_with_source_line(self):
        fact = self.facts[("maven", "java (maven.compiler.release)")]
        self.assertEqual(fact.value, "21")
        self.assertRegex(fact.source, r"^pom\.xml:\d+$")

    def test_quarkus_platform_version_resolved_from_property(self):
        self.assertEqual(self.facts[("maven", "quarkus (quarkus.platform.version)")].value, "3.15.1")
        self.assertEqual(self.facts[("maven", "bom")].value, "io.quarkus.platform:quarkus-bom:3.15.1")

    def test_bom_managed_dependency_is_marked_unresolved(self):
        fact = self.facts[("maven", "dep io.quarkus:quarkus-hibernate-orm-panache")]
        self.assertIn("NÃO RESOLVIDA", fact.value)

    def test_mapstruct_version_and_annotation_processor(self):
        self.assertEqual(self.facts[("maven", "dep org.mapstruct:mapstruct")].value, "1.6.2")
        self.assertEqual(self.facts[("maven", "annotationProcessor org.mapstruct:mapstruct-processor")].value, "1.6.2")

    def test_maven_wrapper_postgres_and_config(self):
        self.assertEqual(self.facts[("maven-wrapper", "maven (wrapper)")].value, "3.9.9")
        self.assertEqual(self.facts[("docker-compose", "postgresql (imagem)")].value, "postgres:16")
        gen = self.facts[("app-config", "quarkus.hibernate-orm.database.generation")]
        self.assertEqual(gen.value, "drop-and-create")
        self.assertEqual(gen.note, "perfil: todos os perfis")
        self.assertEqual(self.facts[("app-config", "quarkus.hibernate-orm.log.sql")].note, "perfil: %dev")

    def test_limitations_are_declared(self):
        self.assertTrue(any("BOM" in item for item in self.report.limitations))

    def test_cli_json_output(self):
        proc = run_script("detect_stack.py", QUARKUS_SAMPLE, "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("components", data)


class DetectStackOtherTest(TempDirMixin, unittest.TestCase):
    def test_react_versions_from_lockfile(self):
        f = facts(detect_stack.detect(REACT_SAMPLE))
        self.assertEqual(f[("npm", "npm react")].value, "^18.3.1 (declarada); 18.3.1 (package-lock)")
        self.assertIn("~5.5.4", f[("npm", "npm typescript")].value)

    def test_empty_project_reports_limitation(self):
        report = detect_stack.detect(self.tmp)
        self.assertEqual(report.components, [])
        self.assertIn("Nenhum arquivo", report.limitations[0])

    def test_invalid_pom_does_not_crash(self):
        (self.tmp / "pom.xml").write_text("<project><broken>", encoding="utf-8")
        report = detect_stack.detect(self.tmp)
        self.assertTrue(any(f.key == "erro" for c in report.components for f in c.facts))

    def test_spring_boot_parent_is_flagged(self):
        (self.tmp / "pom.xml").write_text(
            '<project xmlns="http://maven.apache.org/POM/4.0.0"><parent><groupId>org.springframework.boot</groupId>'
            "<artifactId>spring-boot-starter-parent</artifactId><version>3.3.4</version></parent></project>",
            encoding="utf-8",
        )
        f = facts(detect_stack.detect(self.tmp))
        self.assertEqual(f[("maven", "spring-boot")].value, "3.3.4")

    def test_missing_directory_exit_code(self):
        proc = run_script("detect_stack.py", self.tmp / "nao-existe")
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
