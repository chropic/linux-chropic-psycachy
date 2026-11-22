import hashlib
import importlib.util
import pathlib
import stat
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "normalize_arm64_header_gdb_links",
    ROOT / "tools/normalize-arm64-header-gdb-links.py",
)
NORMALIZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NORMALIZER)


class Arm64HeaderGdbBuilderIntegrationTests(unittest.TestCase):
    def test_builder_normalizes_headers_before_package_verification(self):
        builder = (ROOT / "targets/sp121-arm64/build.sh").read_text()
        normalize = builder.index("normalize-arm64-header-gdb-links.py")
        verify = builder.index('tools/verify-arm64-packages.py')
        self.assertLess(normalize, verify)
        self.assertIn('--source-date-epoch "$headers_source_date_epoch"', builder)
        self.assertIn("header-gdb-normalization.json", builder)


class Arm64HeaderGdbNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp_dir.name)
        self.release = "7.3.5-psycachy-sp121-test"
        self.stage = self.root / "stage"
        self.source = self.root / "source"
        self.helper_root = (
            self.stage / "usr/src" / f"linux-headers-{self.release}"
            / "scripts/gdb/linux"
        )
        self.source_helpers = self.source / "scripts/gdb/linux"
        (self.stage / "DEBIAN").mkdir(parents=True)
        self.helper_root.mkdir(parents=True)
        self.source_helpers.mkdir(parents=True)
        (self.stage / "DEBIAN/control").write_text("Package: test\n")
        (self.stage / f"usr/src/linux-headers-{self.release}/.config").write_text(
            "CONFIG_ARM64=y\n"
        )
        self.epoch = 1795219200

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dereferences_source_links_and_rebuilds_md5sums(self):
        payloads = {
            "__init__.py": b"# gdb helpers\n",
            "btf.py": b"def inspect():\n    return True\n",
        }
        for name, payload in payloads.items():
            source = self.source_helpers / name
            source.write_bytes(payload)
            source.chmod(0o640)
            (self.helper_root / name).symlink_to(source)

        report = NORMALIZER.normalize_header_gdb_links(
            self.stage, self.source, self.release, self.epoch, expected_links=2
        )

        self.assertEqual(report["status"], "normalized-relocatable-gdb-helpers")
        self.assertEqual(report["dereferenced_symlink_count"], 2)
        self.assertEqual(report["remaining_symlink_count"], 0)
        for name, payload in payloads.items():
            path = self.helper_root / name
            self.assertFalse(path.is_symlink())
            self.assertEqual(path.read_bytes(), payload)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
            self.assertEqual(int(path.stat().st_mtime), self.epoch)
        sums = (self.stage / "DEBIAN/md5sums").read_text().splitlines()
        for name, payload in payloads.items():
            relative = f"usr/src/linux-headers-{self.release}/scripts/gdb/linux/{name}"
            expected = hashlib.md5(payload, usedforsecurity=False).hexdigest()
            self.assertIn(f"{expected}  {relative}", sums)
        self.assertTrue(any(line.endswith("/.config") for line in sums))

    def test_rejects_link_outside_the_pinned_source_tree_without_modifying_it(self):
        outside = self.root / "outside.py"
        outside.write_text("# not from the pinned source tree\n")
        link = self.helper_root / "bad.py"
        link.symlink_to(outside)

        with self.assertRaisesRegex(ValueError, "escapes the pinned source tree"):
            NORMALIZER.normalize_header_gdb_links(
                self.stage, self.source, self.release, self.epoch, expected_links=1
            )
        self.assertTrue(link.is_symlink())

    def test_expected_link_count_fails_before_rewriting(self):
        source = self.source_helpers / "helper.py"
        source.write_text("# helper\n")
        link = self.helper_root / "helper.py"
        link.symlink_to(source)

        with self.assertRaisesRegex(ValueError, "expected 2 GDB helper symlinks"):
            NORMALIZER.normalize_header_gdb_links(
                self.stage, self.source, self.release, self.epoch, expected_links=2
            )
        self.assertTrue(link.is_symlink())

    def test_rejects_source_helper_directory_resolved_outside_source_root(self):
        external = self.root / "external"
        (external / "gdb/linux").mkdir(parents=True)
        (external / "gdb/linux/helper.py").write_text("# outside source root\n")
        (self.source / "scripts/gdb/linux").rmdir()
        (self.source / "scripts/gdb").rmdir()
        (self.source / "scripts").rmdir()
        (self.source / "scripts").symlink_to(external, target_is_directory=True)
        link = self.helper_root / "helper.py"
        link.symlink_to(external / "gdb/linux/helper.py")

        with self.assertRaisesRegex(ValueError, "outside the pinned source tree"):
            NORMALIZER.normalize_header_gdb_links(
                self.stage, self.source, self.release, self.epoch, expected_links=1
            )
        self.assertTrue(link.is_symlink())


if __name__ == "__main__":
    unittest.main()
