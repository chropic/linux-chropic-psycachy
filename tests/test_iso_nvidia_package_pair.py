#!/usr/bin/env python3
"""Exercise the NVIDIA package-pair discovery embedded in the installer."""
import hashlib
import json
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "iso/install-target.sh"
MARKER = "python3 - \"$repo\" /var/lib/psycachy/nvidia-package-identity.json <<'PY'\n"


def package_discovery_script():
    source = INSTALLER.read_text(encoding="utf-8")
    if source.count(MARKER) != 1:
        raise AssertionError("installer must contain one NVIDIA package discovery block")
    start = source.index(MARKER) + len(MARKER)
    end = source.index("\nPY\n)", start)
    return source[start:end]


class NvidiaPackagePairTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.identity = self.root / "nvidia-package-identity.json"

    def tearDown(self):
        self.temp.cleanup()

    def build_package(self, package, version):
        stage = self.root / f"stage-{package}-{version}"
        control = stage / "DEBIAN"
        control.mkdir(parents=True)
        (control / "control").write_text(
            f"Package: {package}\nVersion: {version}\nArchitecture: amd64\n"
            "Maintainer: Test Fixture <nobody@example.invalid>\n"
            "Description: disposable NVIDIA package fixture\n",
            encoding="utf-8",
        )
        deb = self.repo / f"{package}_{version}_amd64.deb"
        subprocess.run(
            ["dpkg-deb", "--build", str(stage), str(deb)],
            check=True, capture_output=True,
        )
        return deb

    def run_discovery(self):
        return subprocess.run(
            ["python3", "-", str(self.repo), str(self.identity)],
            input=package_discovery_script(),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_matching_packages_are_identified_from_labeled_deb_fields(self):
        version = "615.71.09-0ubuntu1"
        driver = self.build_package("nvidia-driver-615-open", version)
        dkms = self.build_package("nvidia-dkms-615-open", version)
        self.build_package("nvidia-dkms-614-open", "614.9-0ubuntu1")

        result = self.run_discovery()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), {
            "nvidia-driver-615-open", "nvidia-dkms-615-open",
        })
        identity = json.loads(self.identity.read_text(encoding="utf-8"))
        self.assertEqual(identity["schema_version"], 1)
        self.assertEqual(identity["architecture"], "amd64")
        self.assertEqual({item["name"] for item in identity["packages"]}, {
            "nvidia-driver-615-open", "nvidia-dkms-615-open",
        })
        for package in identity["packages"]:
            path = self.repo / package["filename"]
            self.assertEqual(package["version"], version)
            self.assertEqual(package["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual({driver.name, dkms.name}, {
            item["filename"] for item in identity["packages"]
        })
        self.assertEqual(self.identity.stat().st_mode & 0o777, 0o600)

    def test_mismatched_versions_do_not_form_a_pair(self):
        self.build_package("nvidia-driver-615-open", "615.71.09-0ubuntu1")
        self.build_package("nvidia-dkms-615-open", "615.71.10-0ubuntu1")

        result = self.run_discovery()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("one matching NVIDIA driver/DKMS pair", result.stderr)
        self.assertFalse(self.identity.exists())

    def test_multiple_matching_pairs_are_rejected(self):
        for release, version in (("615", "615.71.09-0ubuntu1"), ("616", "616.1-0ubuntu1")):
            self.build_package(f"nvidia-driver-{release}-open", version)
            self.build_package(f"nvidia-dkms-{release}-open", version)

        result = self.run_discovery()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("one matching NVIDIA driver/DKMS pair", result.stderr)
        self.assertFalse(self.identity.exists())

    def test_duplicate_package_name_versions_are_rejected(self):
        self.build_package("nvidia-driver-615-open", "615.71.09-0ubuntu1")
        self.build_package("nvidia-driver-615-open", "615.71.10-0ubuntu1")
        self.build_package("nvidia-dkms-615-open", "615.71.09-0ubuntu1")

        result = self.run_discovery()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate NVIDIA package", result.stderr)
        self.assertFalse(self.identity.exists())


if __name__ == "__main__":
    unittest.main()
