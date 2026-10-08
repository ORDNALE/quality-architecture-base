import json
import unittest

from _helpers import QUARKUS_SAMPLE, TempDirMixin, run_script

import arch_signals

# Oráculo: problemas intencionais documentados em examples/README.md
EXPECTED = {
    ("S-ARC-001", "ARC-LAY-001", "resource/ClienteResource.java", 18),
    ("S-DTO-001", "BCK-DTO-001", "resource/ClienteResource.java", 23),
    ("S-PER-004", "PER-QRY-001", "resource/ClienteResource.java", 24),
    ("S-PER-002", "PER-LOAD-001", "entity/Venda.java", 25),
    ("S-PER-005", "PER-N1-001", "service/VendaService.java", 39),
    ("S-PER-006", "PER-PAG-007", "repository/VendaRepository.java", 24),
    ("S-MAP-001", "BCK-MAP-004", "mapper/VendaMapper.java", 14),
}
PREFIX = "src/main/java/com/example/vendas/"


class ArchSignalsExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = arch_signals.analyze(QUARKUS_SAMPLE)

    def test_signals_match_documented_oracle_exactly(self):
        found = {(s.id, s.rule, s.file.removeprefix(PREFIX), s.line) for s in self.result.signals}
        self.assertEqual(found, EXPECTED)

    def test_all_signals_need_verification(self):
        self.assertTrue(all(s.state == "NEEDS_VERIFICATION" for s in self.result.signals))

    def test_layer_classification(self):
        self.assertEqual(self.result.layers, {"resource": 2, "service": 1, "repository": 3, "entity": 3, "dto": 1, "mapper": 1})

    def test_cli_json(self):
        proc = run_script("arch_signals.py", QUARKUS_SAMPLE, "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(json.loads(proc.stdout)["signals"]), len(EXPECTED))


class ArchSignalsUnitTest(TempDirMixin, unittest.TestCase):
    def write(self, rel, content):
        path = self.tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_strip_comments_keeps_strings_and_line_count(self):
        src = 'int a; // join fetch\n/* x\n y */ String s = "// not comment";\n'
        out = arch_signals.strip_comments(src)
        self.assertEqual(out.count("\n"), src.count("\n"))
        self.assertNotIn("join fetch", out)
        self.assertIn('"// not comment"', out)

    def test_clean_layered_project_has_no_architecture_signals(self):
        base = "src/main/java/com/acme/"
        self.write(base + "entity/Produto.java", "package com.acme.entity;\nimport jakarta.persistence.*;\n@Entity\npublic class Produto { @Id public Long id;\n @ManyToOne(fetch = FetchType.LAZY) public Categoria categoria; }\n")
        self.write(base + "repository/ProdutoRepository.java", "package com.acme.repository;\nimport com.acme.entity.Produto;\npublic class ProdutoRepository implements PanacheRepository<Produto> {\n public java.util.List<Produto> pagina(int p) { return findAll().page(p, 20).list(); }\n}\n")
        self.write(base + "service/ProdutoService.java", "package com.acme.service;\nimport com.acme.repository.ProdutoRepository;\npublic class ProdutoService { ProdutoRepository repo; }\n")
        self.write(base + "resource/ProdutoResource.java", "package com.acme.resource;\nimport com.acme.service.ProdutoService;\n@Path(\"/p\")\npublic class ProdutoResource { ProdutoService service;\n public java.util.List<ProdutoResponse> listar() { return null; } }\n")
        result = arch_signals.analyze(self.tmp)
        self.assertEqual([s.id for s in result.signals], [])

    def test_test_sources_ignored_by_default(self):
        self.write("src/test/java/x/FooRepositoryTest.java", "package x;\nclass FooRepositoryTest { void t() { try { } catch (Exception e) {} } }\n")
        self.assertEqual(arch_signals.analyze(self.tmp).signals, [])
        self.assertEqual(len(arch_signals.analyze(self.tmp, include_tests=True).signals), 1)

    def test_empty_project_declares_limitation(self):
        result = arch_signals.analyze(self.tmp)
        self.assertIn("Nenhum arquivo .java", result.limitations[0])


if __name__ == "__main__":
    unittest.main()
