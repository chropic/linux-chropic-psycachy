#!/usr/bin/env python3
import importlib.util
import gzip
import json
import os
import pathlib
import hashlib
import io
import lzma
import shutil
import subprocess
import struct
import tarfile
import tempfile
import threading
import types
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "phase2_kernel_trial", ROOT / "tools/phase2-kernel-trial.py"
)
trial = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trial)


class GrubEntryDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.config = """\
submenu 'Advanced options for Ubuntu' $menuentry_id_option 'gnulinux-advanced-abc123' {
    menuentry 'Ubuntu, with Linux 7.3.0-10-generic' --class ubuntu $menuentry_id_option 'gnulinux-7.3.0-10-generic-advanced-abc123' {
        linux /vmlinuz-7.3.0-10-generic root=UUID=root
    }
    menuentry 'Ubuntu, with Linux 7.3.1-psycachy' --class ubuntu $menuentry_id_option 'gnulinux-7.3.1-psycachy-advanced-abc123' {
        linux /vmlinuz-7.3.1-psycachy root=UUID=root
    }
    menuentry 'Ubuntu, with Linux 7.3.1-psycachy (recovery mode)' --class ubuntu $menuentry_id_option 'gnulinux-7.3.1-psycachy-recovery-abc123' {
        linux /vmlinuz-7.3.1-psycachy root=UUID=root recovery
    }
}
"""

    def test_discovers_candidate_and_fallback_under_submenu(self):
        entries = trial.discover_grub_entries(
            self.config, {"7.3.0-10-generic", "7.3.1-psycachy"}
        )
        self.assertEqual(
            entries["7.3.0-10-generic"],
            "gnulinux-advanced-abc123>gnulinux-7.3.0-10-generic-advanced-abc123",
        )
        self.assertEqual(
            entries["7.3.1-psycachy"],
            "gnulinux-advanced-abc123>gnulinux-7.3.1-psycachy-advanced-abc123",
        )

    def test_refuses_missing_or_ambiguous_entry(self):
        with self.assertRaises(trial.TrialError):
            trial.discover_grub_entries(self.config, {"7.3.2-unknown"})
        duplicate = self.config.replace(
            "\n}\n",
            "\n    menuentry 'Ubuntu, with Linux 7.3.1-psycachy' --class ubuntu $menuentry_id_option 'gnulinux-7.3.1-psycachy-alt-abc123' {\n    }\n}\n",
        )
        with self.assertRaises(trial.TrialError):
            trial.discover_grub_entries(duplicate, {"7.3.1-psycachy"})

    def test_top_level_entry_is_not_given_a_false_submenu_prefix(self):
        config = "menuentry 'Ubuntu, with Linux 7.3.1-psycachy' $menuentry_id_option 'gnulinux-7.3.1-psycachy-abc123' {\n}\n"
        self.assertEqual(
            trial.discover_grub_entries(config, {"7.3.1-psycachy"})[
                "7.3.1-psycachy"
            ],
            "gnulinux-7.3.1-psycachy-abc123",
        )

    def test_nested_submenus_are_qualified_and_comments_are_ignored(self):
        config = """\
# menuentry 'Ubuntu, with Linux 7.3.1-psycachy' $menuentry_id_option 'gnulinux-7.3.1-psycachy-fake' {
submenu 'Outer' $menuentry_id_option 'gnulinux-advanced-outer' {
    submenu 'Inner' $menuentry_id_option 'gnulinux-advanced-inner' {
        menuentry 'Ubuntu, with Linux 7.3.1-psycachy' $menuentry_id_option 'gnulinux-7.3.1-psycachy-advanced-real' {
        }
    }
}
"""
        self.assertEqual(
            trial.discover_grub_entries(config, {"7.3.1-psycachy"})[
                "7.3.1-psycachy"
            ],
            "gnulinux-advanced-outer>gnulinux-advanced-inner>gnulinux-7.3.1-psycachy-advanced-real",
        )

    def test_wrapped_entry_and_release_prefix_collision_fail_closed(self):
        wrapped = "submenu 'Options' $menuentry_id_option 'gnulinux-advanced-a' {\nmenuentry 'Ubuntu Linux 7.3.1-psycachy' {\n}\n}\n"
        with self.assertRaisesRegex(trial.TrialError, "malformed GRUB menuentry"):
            trial.discover_grub_entries(wrapped, {"7.3.1-psycachy"})
        collision = "menuentry 'Ubuntu, with Linux 7.3.1-psycachy-debug' $menuentry_id_option 'gnulinux-7.3.1-psycachy-debug-a' {\n}\n"
        with self.assertRaises(trial.TrialError):
            trial.discover_grub_entries(collision, {"7.3.1-psycachy"})

    def test_fallback_entry_block_is_bound_to_kernel_and_initrd(self):
        block = """menuentry 'Ubuntu, with Linux 7.3.0-10-generic' $menuentry_id_option 'gnulinux-7.3.0-10-generic-a' {
    linux /boot/vmlinuz-7.3.0-10-generic root=UUID=root
    initrd /boot/initrd.img-7.3.0-10-generic
}
"""
        self.assertEqual(len(trial.verify_grub_entry_payloads(block, "7.3.0-10-generic")), 64)
        with self.assertRaisesRegex(trial.TrialError, "pinned kernel"):
            trial.verify_grub_entry_payloads(block.replace("vmlinuz-7.3.0-10-generic", "vmlinuz-other"),
                                             "7.3.0-10-generic")
        with self.assertRaisesRegex(trial.TrialError, "pinned initrd"):
            trial.verify_grub_entry_payloads(block.replace("initrd.img-7.3.0-10-generic", "initrd-other"),
                                             "7.3.0-10-generic")


class TrialStateHelpersTests(unittest.TestCase):
    def test_preerase_activation_mode_is_required_and_bound_to_target_serial(self):
        with tempfile.TemporaryDirectory() as directory:
            mode = pathlib.Path(directory) / "activation-mode.json"
            with self.assertRaisesRegex(trial.TrialError, "missing or unsafe"):
                trial.verified_activation_mode(mode, "/dev/test1")
            mode.write_text(json.dumps({"schema_version": 1, "mode": "first-install",
                                        "disk_serial": "disk-A",
                                        "operator_confirmed_no_displaced_candidate_payload": True}),
                            encoding="utf-8")
            mode.chmod(0o600)
            original_stat = pathlib.Path.stat
            def root_owned(path, *args, **kwargs):
                result = original_stat(path, *args, **kwargs)
                return types.SimpleNamespace(st_uid=0, st_mode=result.st_mode) if path == mode else result
            commands = [
                subprocess.CompletedProcess([], 0, "disk /dev/test\n", ""),
                subprocess.CompletedProcess([], 0, "ID_SERIAL=disk-A\n", ""),
            ]
            with mock.patch.object(pathlib.Path, "stat", root_owned), \
                    mock.patch.object(trial, "command", side_effect=commands):
                self.assertEqual(trial.verified_activation_mode(mode, "/dev/test1")["mode"],
                                 "first-install")
            commands = [
                subprocess.CompletedProcess([], 0, "disk /dev/test\n", ""),
                subprocess.CompletedProcess([], 0, "ID_SERIAL=disk-B\n", ""),
            ]
            with mock.patch.object(pathlib.Path, "stat", root_owned), \
                    mock.patch.object(trial, "command", side_effect=commands):
                with self.assertRaisesRegex(trial.TrialError, "does not match"):
                    trial.verified_activation_mode(mode, "/dev/test1")

    def test_replacement_activation_mode_without_backup_fails_and_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            mode = pathlib.Path(directory) / "activation-mode.json"
            mode.write_text(json.dumps({"schema_version": 1, "mode": "replacement",
                                        "disk_serial": "disk-A"}), encoding="utf-8")
            mode.chmod(0o600)
            original_stat = pathlib.Path.stat
            def root_owned(path, *args, **kwargs):
                result = original_stat(path, *args, **kwargs)
                return types.SimpleNamespace(st_uid=0, st_mode=result.st_mode) if path == mode else result
            commands = [
                subprocess.CompletedProcess([], 0, "disk /dev/test\n", ""),
                subprocess.CompletedProcess([], 0, "ID_SERIAL=disk-A\n", ""),
            ]
            with mock.patch.object(pathlib.Path, "stat", root_owned), \
                    mock.patch.object(trial, "command", side_effect=commands):
                with self.assertRaisesRegex(trial.TrialError, "pre-verified"):
                    trial.verified_activation_mode(mode, "/dev/test1")
            mode.chmod(0o644)
            with self.assertRaisesRegex(trial.TrialError, "missing or unsafe"):
                trial.verified_activation_mode(mode, "/dev/test1")

    def test_verified_nvidia_package_identity_uses_installed_package_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            identity = pathlib.Path(directory) / "nvidia.json"
            value = {"schema_version": 1, "architecture": "amd64", "packages": [
                {"name": "nvidia-driver-900-open", "version": "900.4.1-2",
                 "filename": "nvidia-driver-900-open.deb", "sha256": "a" * 64},
                {"name": "nvidia-dkms-900-open", "version": "900.4.1-2",
                 "filename": "nvidia-dkms-900-open.deb", "sha256": "b" * 64}]}
            identity.write_text(json.dumps(value), encoding="utf-8")
            identity.chmod(0o600)
            original_stat = pathlib.Path.stat
            def root_owned(path, *args, **kwargs):
                result = original_stat(path, *args, **kwargs)
                return types.SimpleNamespace(st_uid=0, st_mode=result.st_mode) if path == identity else result
            def installed(argv, *, allow_failure=False):
                package = argv[-1]
                return subprocess.CompletedProcess(argv, 0, "ii 900.4.1-2 amd64\n", "")
            with mock.patch.object(pathlib.Path, "stat", root_owned), \
                    mock.patch.object(trial, "command", side_effect=installed):
                self.assertEqual(trial.installed_nvidia_package_identity(identity), value)
            with mock.patch.object(pathlib.Path, "stat", root_owned), \
                    mock.patch.object(trial, "command", return_value=subprocess.CompletedProcess([], 0, "ii 1.0 amd64\n", "")):
                with self.assertRaisesRegex(trial.TrialError, "does not match"):
                    trial.installed_nvidia_package_identity(identity)

    def test_health_attestation_is_bound_to_local_candidate_and_all_physical_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            attest_dir = root / "attestations"
            attest_dir.mkdir()
            attestation_path = attest_dir / "health.json"
            state = {"machine_id": "a" * 32, "pin_sha256": "b" * 64,
                     "candidate_payload_hashes": {"vmlinuz": "c" * 64},
                     "local_activation_identity": {"kernel_signing_certificate_sha256": "d" * 64,
                                                    "module_signing_certificate_sha256": "e" * 64}}
            attestation = {"schema_version": 1, "reviewed": True, "reviewer": "operator",
                "reviewed_at_utc": "2026-11-14T00:00:00Z", "machine_id": "a" * 32,
                "candidate_pin_sha256": "b" * 64, "candidate_payload_hashes": {"vmlinuz": "c" * 64},
                "kernel_signing_certificate_sha256": "d" * 64,
                "module_signing_certificate_sha256": "e" * 64,
                "physical_gates": {name: True for name in trial.ATTESTATION_GATES}}
            attestation_path.write_text(json.dumps(attestation), encoding="utf-8")
            attestation_path.chmod(0o600)
            original_stat = pathlib.Path.stat
            def root_owned(path, *args, **kwargs):
                result = original_stat(path, *args, **kwargs)
                return types.SimpleNamespace(st_uid=0, st_mode=result.st_mode) if path == attestation_path else result
            with mock.patch.object(trial, "ATTESTATION_DIR", attest_dir), \
                    mock.patch.object(trial, "ensure_attestation_directory"), \
                    mock.patch.object(pathlib.Path, "stat", root_owned):
                self.assertEqual(trial.verify_health_attestation(attestation_path, state)["reviewer"], "operator")
                attestation["candidate_pin_sha256"] = "0" * 64
                attestation_path.write_text(json.dumps(attestation), encoding="utf-8")
                with self.assertRaisesRegex(trial.TrialError, "does not match current candidate_pin_sha256"):
                    trial.verify_health_attestation(attestation_path, state)

    def test_parse_grub_environment(self):
        state = trial.parse_grubenv(
            "saved_entry=gnulinux-generic\nnext_entry=gnulinux-candidate\n"
        )
        self.assertEqual(state["saved_entry"], "gnulinux-generic")
        self.assertEqual(state["next_entry"], "gnulinux-candidate")

    def test_timeout_units_are_armed_after_userspace_and_do_not_change_default(self):
        start, timeout = trial.render_units(
            pathlib.Path("/var/lib/psycachy/kernel-trial.json"), 120
        )
        self.assertIn("After=multi-user.target", start)
        self.assertIn("arm-timeout", start)
        self.assertIn("OnActiveSec=120s", timeout)
        self.assertIn("ExecStart=/usr/local/sbin/phase2-kernel-trial", timeout)
        self.assertNotIn("grub-set-default", start + timeout)

    def test_secure_boot_enabled_is_detected_before_owner_identity_checks(self):
        result = subprocess.CompletedProcess(
            ["mokutil", "--sb-state"], 0, "SecureBoot enabled\n", ""
        )
        with mock.patch.object(trial, "command", return_value=result):
            self.assertEqual(trial.secure_boot_state(), "enabled")

    def test_secure_boot_enabled_requires_separate_owner_certificate_pins(self):
        secure = subprocess.CompletedProcess(
            ["mokutil", "--sb-state"], 0, "SecureBoot enabled\n", ""
        )
        with mock.patch.object(trial, "command", return_value=secure):
            self.assertEqual(trial.secure_boot_state(), "enabled")
            with self.assertRaisesRegex(trial.TrialError, "identities are not pinned"):
                trial.verify_secure_boot_identity(
                    {"module_signing_certificate_sha256": "a" * 64},
                    "7.3.1-psycachy",
                )

    def test_secure_boot_unenrolled_owner_certificate_is_refused(self):
        result = subprocess.CompletedProcess(
            ["mokutil", "--test-key", "/tmp/module.der"], 1, "", "not enrolled\n"
        )
        with mock.patch.object(trial, "command", return_value=result):
            with self.assertRaisesRegex(trial.TrialError, "not confirmed enrolled"):
                trial._require_enrolled_certificate(pathlib.Path("/tmp/module.der"))

    def test_per_install_owner_certificates_bind_once_to_the_installed_pin(self):
        kernel_digest = "a" * 64
        module_digest = "b" * 64
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            pin_path = root / "amd64-kernel-pin.json"
            pin = json.loads((ROOT / "config/amd64-iso-kernel.json").read_text(encoding="utf-8"))
            pin_path.write_text(json.dumps(pin), encoding="utf-8")
            key_dir = root / "secureboot"
            key_dir.mkdir(mode=0o700)
            for name in ("kernel.pem", "kernel.der", "module.der", "kernel.key", "module.key"):
                path = key_dir / name
                path.write_text("test material", encoding="ascii")
                path.chmod(0o600)

            def fake_command(argv, *, allow_failure=False):
                if "-subject" in argv:
                    subject = ("subject=CN=PsyCachy Secure Boot Kernel\n"
                               if any("kernel.pem" in arg for arg in argv) else
                               "subject=CN=PsyCachy DKMS Module Signing\n")
                    return subprocess.CompletedProcess(argv, 0, subject, "")
                if "-pubkey" in argv or argv[1] == "pkey":
                    return subprocess.CompletedProcess(argv, 0, "same public key\n", "")
                raise AssertionError(argv)

            def fake_fingerprint(path, *, der):
                return module_digest if path.name == "module.der" else kernel_digest

            with mock.patch.object(trial, "require_root"), \
                    mock.patch.object(trial, "_require_root_owned_path"), \
                    mock.patch.object(trial, "_certificate_sha256", side_effect=fake_fingerprint), \
                    mock.patch.object(trial, "command", side_effect=fake_command):
                bound = trial.bind_owner_certificates(pin_path, key_dir)
                self.assertEqual(bound, {
                    "certificate_binding": "bound-per-install",
                    "kernel_certificate_sha256": kernel_digest,
                    "module_certificate_sha256": module_digest,
                })
                saved = json.loads(pin_path.read_text(encoding="utf-8"))
                self.assertEqual(saved["secure_boot"]["certificate_binding"], "bound-per-install")
                self.assertEqual(saved["secure_boot"]["kernel_certificate_sha256"], kernel_digest)
                self.assertEqual(saved["secure_boot"]["module_certificate_sha256"], module_digest)
                with self.assertRaisesRegex(trial.TrialError, "not awaiting its one-time"):
                    trial.bind_owner_certificates(pin_path, key_dir)

    def test_secure_boot_identity_refuses_an_unbound_per_install_pin(self):
        pin = json.loads((ROOT / "config/amd64-iso-kernel.json").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(trial.TrialError, "not bound to this installation"):
            trial.verify_secure_boot_identity(pin, "7.3.1-psycachy")

    def test_secure_boot_enrollment_accepts_known_keyring_diagnostic_with_exact_success(self):
        cert = pathlib.Path("/tmp/owner module.der")
        result = subprocess.CompletedProcess(
            ["mokutil", "--test-key", str(cert)], 1,
            f"{cert} is already enrolled\n",
            "Failed to access kernel trusted keyring: Required key not available\n",
        )
        with mock.patch.object(trial, "command", return_value=result):
            trial._require_enrolled_certificate(cert)

        alternate = subprocess.CompletedProcess(
            ["mokutil", "--test-key", str(cert)], 1,
            "Failed to access kernel trusted keyring: Required key not available\n",
            f"{cert} is already in db\n",
        )
        with mock.patch.object(trial, "command", return_value=alternate):
            trial._require_enrolled_certificate(cert)

        ambiguous = subprocess.CompletedProcess(
            ["mokutil", "--test-key", str(cert)], 0,
            f"{cert} is already enrolled\nUnexpected extra output\n", "",
        )
        with mock.patch.object(trial, "command", return_value=ambiguous):
            with self.assertRaisesRegex(trial.TrialError, "not confirmed enrolled"):
                trial._require_enrolled_certificate(cert)

    def test_module_signature_rejects_different_certificate_with_the_same_cn(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for label in ("expected", "same-cn-other-key"):
                subprocess.run(
                    ["openssl", "req", "-new", "-x509", "-newkey", "rsa:2048",
                     "-nodes", "-keyout", str(root / f"{label}.key"),
                     "-out", str(root / f"{label}.pem"),
                     "-subj", "/CN=Same Module Signer", "-days", "1"],
                    check=True, capture_output=True,
                )
                subprocess.run(
                    ["openssl", "x509", "-in", str(root / f"{label}.pem"),
                     "-outform", "DER", "-out", str(root / f"{label}.der")],
                    check=True, capture_output=True,
                )
            payload_path = root / "module.payload"
            payload_path.write_bytes(b"module bytes bound to the expected signing key")
            signature_path = root / "module.p7s"
            subprocess.run(
                ["openssl", "cms", "-sign", "-binary", "-noattr", "-nosmimecap",
                 "-nocerts", "-in", str(payload_path), "-signer", str(root / "expected.pem"),
                 "-inkey", str(root / "expected.key"), "-outform", "DER",
                 "-out", str(signature_path)],
                check=True, capture_output=True,
            )
            signature = signature_path.read_bytes()
            header = struct.pack(
                ">BBBBB3sI", 0, 0, trial.MODULE_SIGNATURE_TYPE_PKCS7,
                0, 0, b"\0\0\0", len(signature),
            )
            module_path = root / "nvidia.ko"
            module_path.write_bytes(
                payload_path.read_bytes() + signature + header + trial.MODULE_SIGNATURE_MARKER
            )

            trial._verify_module_signature(module_path, root / "expected.der")
            metadata_header = struct.pack(
                ">BBBBB3sI", 0, 0, trial.MODULE_SIGNATURE_TYPE_PKCS7,
                3, 2, b"\0\0\0", len(signature),
            )
            metadata_module = root / "metadata-fields.ko"
            metadata_module.write_bytes(
                payload_path.read_bytes() + b"sigid" + signature
                + metadata_header + trial.MODULE_SIGNATURE_MARKER
            )
            trial._verify_module_signature(metadata_module, root / "expected.der")
            malformed = root / "malformed.ko"
            malformed_header = struct.pack(
                ">BBBBB3sI", 0, 0, trial.MODULE_SIGNATURE_TYPE_PKCS7,
                0, 0, b"\0\0\0", len(module_path.read_bytes()) + 1,
            )
            malformed.write_bytes(
                payload_path.read_bytes() + signature + malformed_header
                + trial.MODULE_SIGNATURE_MARKER
            )
            with self.assertRaisesRegex(trial.TrialError, "invalid signature lengths"):
                trial._verify_module_signature(malformed, root / "expected.der")
            with self.assertRaisesRegex(trial.TrialError, "does not verify with the pinned certificate"):
                trial._verify_module_signature(module_path, root / "same-cn-other-key.der")
            for suffix, packed in (
                (".ko.gz", gzip.compress(module_path.read_bytes())),
                (".ko.xz", lzma.compress(module_path.read_bytes())),
            ):
                compressed = root / f"nvidia{suffix}"
                compressed.write_bytes(packed)
                trial._verify_module_signature(compressed, root / "expected.der")
                with self.assertRaisesRegex(trial.TrialError, "does not verify with the pinned certificate"):
                    trial._verify_module_signature(compressed, root / "same-cn-other-key.der")
            if shutil.which("zstd"):
                compressed = root / "nvidia.ko.zst"
                packed = subprocess.run(
                    ["zstd", "-q", "-c", str(module_path)],
                    check=True, capture_output=True,
                )
                compressed.write_bytes(packed.stdout)
                trial._verify_module_signature(compressed, root / "expected.der")
                with self.assertRaisesRegex(trial.TrialError, "does not verify with the pinned certificate"):
                    trial._verify_module_signature(compressed, root / "same-cn-other-key.der")

    def test_secure_boot_module_path_must_be_regular_and_confined(self):
        for case in ("outside", "symlink"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                boot = root / "boot"
                boot.mkdir()
                (boot / "config-7.3.1-psycachy").write_text(
                    "CONFIG_MODULE_SIG=y\nCONFIG_MODULE_SIG_ALL=y\nCONFIG_MODULE_SIG_FORCE=y\n",
                    encoding="ascii",
                )
                module_root = root / "modules" / "7.3.1-psycachy"
                module_root.mkdir(parents=True)
                outside = root / "outside.ko"
                outside.write_bytes(b"signed module placeholder")
                if case == "symlink":
                    listed_path = module_root / "nvidia.ko"
                    listed_path.symlink_to(outside)
                    expected_error = "missing or unsafe"
                else:
                    listed_path = outside
                    expected_error = "outside its pinned module tree"

                def fake_command(argv, *, allow_failure=False):
                    if argv[3] == "-n":
                        value = str(listed_path)
                    else:
                        value = "Test DKMS Signer" if argv[4] == "signer" else "PKCS#7"
                    return subprocess.CompletedProcess(argv, 0, value + "\n", "")

                with mock.patch.object(trial, "BOOT_DIR", boot), \
                        mock.patch.object(trial, "MODULES_DIR", root / "modules"), \
                        mock.patch.object(trial, "command", side_effect=fake_command):
                    with self.assertRaisesRegex(trial.TrialError, expected_error):
                        trial._verify_required_module_signers(
                            "7.3.1-psycachy", {"nvidia": "Test DKMS Signer"},
                            module_certificate=root / "module.der",
                            loaded_modules=["nvidia"], runtime=False,
                        )

    def test_secure_boot_identity_checks_certificates_signature_and_transformed_bytes(self):
        kernel_digest = "a" * 64
        module_digest = "b" * 64
        payload = b"exact unsigned package kernel payload"
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            boot = root / "boot"
            boot.mkdir()
            kernel_cert = root / "kernel.pem"
            kernel_cert.write_bytes(b"kernel certificate")
            kernel_der = root / "kernel.der"
            kernel_der.write_bytes(b"kernel certificate DER")
            module_cert = root / "module.der"
            module_cert.write_bytes(b"module certificate DER")
            image = boot / "vmlinuz-7.3.1-psycachy"
            image.write_bytes(payload + b"--SIGNATURE--")
            (boot / "config-7.3.1-psycachy").write_text(
                "CONFIG_MODULE_SIG=y\nCONFIG_MODULE_SIG_ALL=y\nCONFIG_MODULE_SIG_FORCE=y\n",
                encoding="ascii",
            )
            pin = {
                "kernel_payload_sha256": hashlib.sha256(payload).hexdigest(),
                "secure_boot": {
                    "certificate_binding": "bound-per-install",
                    "kernel_certificate_sha256": kernel_digest,
                    "module_certificate_sha256": module_digest,
                    "required_module_signers": {"nvidia": "Test DKMS Signer"},
                    "required_loaded_modules": ["nvidia"],
                },
            }
            module_root = root / "modules" / "7.3.1-psycachy"
            module_root.mkdir(parents=True)
            module_path = module_root / "nvidia.ko"
            module_path.write_bytes(b"test module")

            def fake_command(argv, *, allow_failure=False):
                if argv[0] == "openssl":
                    path = pathlib.Path(argv[3])
                    digest = module_digest if path == module_cert else kernel_digest
                    fingerprint = ":".join(digest[index:index + 2].upper()
                                            for index in range(0, len(digest), 2))
                    return subprocess.CompletedProcess(argv, 0,
                                                        f"sha256 Fingerprint={fingerprint}\n", "")
                if argv[:2] == ["mokutil", "--test-key"]:
                    return subprocess.CompletedProcess(argv, 1, f"{argv[2]} is already enrolled\n", "")
                if argv[0] == "sbverify":
                    return subprocess.CompletedProcess(argv, 0, "Signature verification OK\n", "")
                if argv[0] == "sbattach":
                    path = pathlib.Path(argv[-1])
                    path.write_bytes(path.read_bytes().removesuffix(b"--SIGNATURE--"))
                    return subprocess.CompletedProcess(argv, 0, "", "")
                if argv[0] == "modinfo":
                    if argv[3] == "-n":
                        value = str(module_path)
                    else:
                        value = "Test DKMS Signer" if argv[4] == "signer" else "PKCS#7"
                    return subprocess.CompletedProcess(argv, 0, value + "\n", "")
                raise AssertionError(argv)

            with mock.patch.object(trial, "BOOT_DIR", boot), \
                    mock.patch.object(trial, "MODULES_DIR", root / "modules"), \
                    mock.patch.object(trial, "_verify_module_signature"), \
                    mock.patch.object(trial, "command", side_effect=fake_command):
                identity = trial.verify_secure_boot_identity(
                    pin, "7.3.1-psycachy", image_path=image,
                    kernel_certificate=kernel_cert, module_certificate=module_cert,
                )
            self.assertEqual(identity["owner_kernel_certificate_sha256"], kernel_digest)
            self.assertEqual(identity["enrolled_kernel_certificate_sha256"], kernel_digest)
            self.assertEqual(identity["owner_module_certificate_sha256"], module_digest)
            self.assertEqual(identity["enrolled_module_certificate_sha256"], module_digest)
            self.assertEqual(identity["unsigned_kernel_payload_sha256"], pin["kernel_payload_sha256"])
            self.assertEqual(identity["signed_kernel_payload_sha256"], hashlib.sha256(image.read_bytes()).hexdigest())
            self.assertEqual(identity["required_module_signers"], {"nvidia": "Test DKMS Signer"})

    def test_secure_boot_module_runtime_requires_lockdown_enforcement_and_loaded_signer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            boot = root / "boot"
            boot.mkdir()
            (boot / "config-7.3.1-psycachy").write_text(
                "CONFIG_MODULE_SIG=y\nCONFIG_MODULE_SIG_ALL=y\nCONFIG_MODULE_SIG_FORCE=y\n",
                encoding="ascii",
            )
            lockdown = root / "lockdown"
            lockdown.write_text("none [integrity] confidentiality\n", encoding="ascii")
            enforce = root / "sig_enforce"
            enforce.write_text("Y\n", encoding="ascii")
            modules = root / "sys-module"
            (modules / "nvidia").mkdir(parents=True)
            module_root = root / "modules" / "7.3.1-psycachy"
            module_root.mkdir(parents=True)
            module_path = module_root / "nvidia.ko"
            module_path.write_bytes(b"test module")
            commands = []

            def fake_command(argv, *, allow_failure=False):
                commands.append(argv)
                if argv[3] == "-n":
                    value = str(module_path)
                else:
                    field = argv[4]
                    value = "Test DKMS Signer" if field == "signer" else "PKCS#7"
                return subprocess.CompletedProcess(argv, 0, value + "\n", "")

            with mock.patch.object(trial, "BOOT_DIR", boot), \
                    mock.patch.object(trial, "MODULES_DIR", root / "modules"), \
                    mock.patch.object(trial, "LOCKDOWN_STATUS", lockdown), \
                    mock.patch.object(trial, "MODULE_ENFORCE_STATUS", enforce), \
                    mock.patch.object(trial, "SYS_MODULE_DIR", modules), \
                    mock.patch.object(trial, "_verify_module_signature"), \
                    mock.patch.object(trial, "command", side_effect=fake_command):
                trial._verify_required_module_signers(
                    "7.3.1-psycachy", {"nvidia": "Test DKMS Signer"},
                    module_certificate=root / "module.der",
                    loaded_modules=["nvidia"], runtime=True,
                )
            self.assertEqual(len(commands), 2)
            self.assertNotIn("signer", [argv[4] for argv in commands if len(argv) > 4])

            enforce.write_text("N\n", encoding="ascii")
            with mock.patch.object(trial, "BOOT_DIR", boot), \
                    mock.patch.object(trial, "LOCKDOWN_STATUS", lockdown), \
                    mock.patch.object(trial, "MODULE_ENFORCE_STATUS", enforce), \
                    mock.patch.object(trial, "SYS_MODULE_DIR", modules):
                with self.assertRaisesRegex(trial.TrialError, "not enforcing module signatures"):
                    trial._verify_required_module_signers(
                        "7.3.1-psycachy", {"nvidia": "Test DKMS Signer"},
                        module_certificate=root / "module.der",
                        loaded_modules=["nvidia"], runtime=True,
                    )

    def test_secure_boot_candidate_verification_failure_requests_automatic_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            state_file = pathlib.Path(directory) / "state.json"
            state = {
                "schema_version": 1,
                "state": "pending",
                "kernel_release": "7.3.1-psycachy",
                "fallback_release": "7.3.0-10-generic",
                "fallback_entry": "fallback-entry",
                "secure_boot_mode": "enabled",
                "secure_boot_identity": {"owner_kernel_certificate_sha256": "a" * 64},
                "required_units": [],
                "runtime": {},
            }
            trial.write_state(state_file, state)
            rollback = {"state": "timeout_reboot_requested"}
            with mock.patch.object(trial, "verify_fallback_unchanged"), \
                    mock.patch.object(trial, "verify_candidate_integrity",
                                      side_effect=trial.TrialError("module trust check failed")), \
                    mock.patch.object(trial, "rollback_locked", return_value=rollback) as request_rollback, \
                    mock.patch.object(trial.os, "uname",
                                      return_value=types.SimpleNamespace(release="7.3.1-psycachy")):
                result = trial.arm_timeout_locked(state_file)
            self.assertEqual(result, rollback)
            request_rollback.assert_called_once_with(state_file, expired=True)
            self.assertEqual(
                trial.read_state(state_file)["security_verification_error"],
                "module trust check failed",
            )

    def test_secure_boot_disabled_is_recorded(self):
        result = subprocess.CompletedProcess(
            ["mokutil", "--sb-state"], 0, "SecureBoot disabled\n", ""
        )
        with mock.patch.object(trial, "command", return_value=result):
            self.assertEqual(trial.secure_boot_state(), "disabled")

    def test_secure_boot_unknown_or_unreadable_fails_closed(self):
        unknown = subprocess.CompletedProcess(["mokutil"], 0, "state unavailable\n", "")
        unreadable = subprocess.CompletedProcess(["mokutil"], 1, "", "permission denied")
        for result in (unknown, unreadable):
            with mock.patch.object(trial, "command", return_value=result):
                with self.assertRaisesRegex(trial.TrialError, "refusing"):
                    trial.secure_boot_state()

    def test_fallback_identity_change_is_refused(self):
        state = {
            "architecture": "amd64",
            "fallback_release": "7.3.0-10-generic",
            "fallback_image_package_version": "1.0",
            "fallback_headers_package_version": "1.0",
            "fallback_payload_hashes": {"vmlinuz": "a" * 64},
        }
        changed = {
            "image_package_version": "1.0",
            "headers_package_version": "1.0",
            "payload_hashes": {"vmlinuz": "b" * 64},
        }
        with mock.patch.object(trial, "fallback_identity", return_value=changed):
            with self.assertRaisesRegex(trial.TrialError, "fallback payload changed"):
                trial.verify_fallback_unchanged(state)

    def _make_backup(self, directory, *, corrupt_payload=False):
        pin = trial.read_pin(ROOT / "config/amd64-iso-kernel.json")
        root = pathlib.Path(directory)
        archive_path = root / "displaced.tar"
        backup_root = root / "backup-tree"
        members = {
            "image_deb": "backup/image.deb",
            "headers_deb": "backup/headers.deb",
            "vmlinuz": "backup/vmlinuz",
            "initrd": "backup/initrd",
            "kernel_config": "backup/config",
            "system_map": "backup/System.map",
            "modules_tree": "backup/modules",
            "headers_tree": "backup/headers-tree",
            "signed_payload": "backup/signed.efi",
            "grub_config": "backup/grub.cfg",
        }
        files = {
            "image_deb": b"image-deb-bytes",
            "headers_deb": b"headers-deb-bytes",
            "vmlinuz": b"old-kernel",
            "initrd": b"old-initrd",
            "kernel_config": b"old-config",
            "system_map": b"old-system-map",
            "signed_payload": b"old-signed-image",
            "grub_config": b"old-grub-config",
        }
        trees = {
            "modules_tree": ("backup/modules", {"kernel/module.ko": b"old-module"}),
            "headers_tree": ("backup/headers-tree", {"include/linux/test.h": b"old-header"}),
        }
        records = {}
        for semantic, content in files.items():
            records[semantic] = (content, 0o644, "file")
        for semantic, (archive_root, tree_files) in trees.items():
            local_root = backup_root / semantic
            local_root.mkdir(parents=True)
            for relative, content in tree_files.items():
                local_path = local_root / relative
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(content)
                local_path.chmod(0o644)
                local_dir = local_path.parent
                while local_dir != local_root:
                    local_dir.chmod(0o755)
                    local_dir = local_dir.parent
            records[semantic] = (local_root, 0o755, "tree")

        with tarfile.open(archive_path, "w") as archive:
            parent = tarfile.TarInfo("backup")
            parent.type = tarfile.DIRTYPE
            parent.mode = 0o755
            archive.addfile(parent)
            for semantic, content in files.items():
                if corrupt_payload and semantic == "vmlinuz":
                    content = b"wrong-kernel"
                info = tarfile.TarInfo(members[semantic])
                info.size = len(content)
                info.mode = 0o644
                archive.addfile(info, io.BytesIO(content))
            for semantic, (archive_root, tree_files) in trees.items():
                root_info = tarfile.TarInfo(archive_root)
                root_info.type = tarfile.DIRTYPE
                root_info.mode = 0o755
                archive.addfile(root_info)
                dirs = set()
                for relative in tree_files:
                    parent = pathlib.PurePosixPath(relative).parent
                    while str(parent) != ".":
                        dirs.add(str(parent))
                        parent = parent.parent
                for relative_dir in sorted(dirs, key=lambda item: (item.count("/"), item)):
                    directory_info = tarfile.TarInfo(archive_root + "/" + relative_dir)
                    directory_info.type = tarfile.DIRTYPE
                    directory_info.mode = 0o755
                    archive.addfile(directory_info)
                for relative, content in tree_files.items():
                    info = tarfile.TarInfo(archive_root + "/" + relative)
                    info.size = len(content)
                    info.mode = 0o644
                    archive.addfile(info, io.BytesIO(content))

        payloads = {}
        for semantic, value in records.items():
            content, mode, kind = value
            if kind == "file":
                payloads[semantic] = hashlib.sha256(content).hexdigest()
            else:
                payloads[semantic] = trial.hash_tree(content)
        manifest = {
            "schema_version": 1,
            "architecture": pin["architecture"],
            "kernel_release": pin["kernel_release"],
            "backup_volume_id": "approved-backup-uuid",
            "archive_path": str(archive_path),
            "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
            "archive_members": members,
            "payloads": payloads,
            "displaced_package_versions": {
                f"linux-image-{pin['kernel_release']}": "7.2.0-1",
                f"linux-headers-{pin['kernel_release']}": "7.2.0-1",
            },
        }
        manifest_path = root / "backup.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
        expected_manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        return pin, manifest_path, expected_manifest_hash, payloads

    def _backup_commands(self, argv, *, allow_failure=False):
        if argv[0] == "findmnt":
            volume = "approved-backup-uuid" if argv[-1] != "/" else "root-volume-uuid"
            return subprocess.CompletedProcess(argv, 0, volume + "\n", "")
        if argv[0] == "dpkg-deb":
            pin = trial.read_pin(ROOT / "config/amd64-iso-kernel.json")
            package_type = "image" if b"image-deb" in pathlib.Path(argv[2]).read_bytes() else "headers"
            package = f"linux-{package_type}-{pin['kernel_release']}"
            return subprocess.CompletedProcess(
                argv, 0,
                f"Package: {package}\nVersion: 7.2.0-1\nArchitecture: amd64\n", "",
            )
        self.fail(f"Unexpected backup verification command: {argv}")

    def test_displaced_backup_verifies_reviewed_volume_archive_and_members(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            pin, manifest_path, expected_hash, payloads = self._make_backup(directory)
            with mock.patch.object(trial, "command", side_effect=self._backup_commands):
                result = trial.verify_displaced_backup(
                    manifest_path, pin,
                    expected_manifest_sha256=expected_hash,
                    approved_volume_id="approved-backup-uuid",
                )
            self.assertEqual(result["backup_volume_id"], "approved-backup-uuid")
            self.assertEqual(result["payloads"]["vmlinuz"], payloads["vmlinuz"])

    def test_displaced_backup_on_selected_erase_disk_is_rejected(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            pin, manifest_path, expected_hash, _ = self._make_backup(directory)

            def commands(argv, *, allow_failure=False):
                if argv[0] == "findmnt" and argv[3] == "UUID":
                    volume = "approved-backup-uuid" if argv[-1] != "/" else "root-volume-uuid"
                    return subprocess.CompletedProcess(argv, 0, volume + "\n", "")
                if argv[0] == "findmnt" and argv[3] == "SOURCE":
                    return subprocess.CompletedProcess(argv, 0, "/dev/sdb1\n", "")
                if argv[0] == "lsblk":
                    return subprocess.CompletedProcess(argv, 0, "part /dev/sdb1\ndisk /dev/sdb\n", "")
                if argv[0] == "udevadm":
                    return subprocess.CompletedProcess(argv, 0, "ID_SERIAL=erase-target-1\n", "")
                if argv[0] == "dpkg-deb":
                    return self._backup_commands(argv, allow_failure=allow_failure)
                self.fail(f"Unexpected backup verification command: {argv}")

            with mock.patch.object(trial, "command", side_effect=commands):
                with self.assertRaisesRegex(trial.TrialError, "different serial-identified disk"):
                    trial.verify_displaced_backup(manifest_path, pin,
                        expected_manifest_sha256=expected_hash,
                        approved_volume_id="approved-backup-uuid",
                        target_disk_serial="erase-target-1")

    def test_displaced_backup_manifest_must_remain_on_the_reviewed_volume(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            pin, manifest_path, expected_hash, _ = self._make_backup(directory)

            def commands(argv, *, allow_failure=False):
                if argv[0] == "findmnt":
                    if argv[3] == "UUID" and argv[-1] == str(manifest_path):
                        volume = "root-volume-uuid"
                    else:
                        volume = "approved-backup-uuid" if argv[-1] != "/" else "root-volume-uuid"
                    return subprocess.CompletedProcess(argv, 0, volume + "\n", "")
                if argv[0] == "dpkg-deb":
                    return self._backup_commands(argv, allow_failure=allow_failure)
                self.fail(f"Unexpected backup verification command: {argv}")

            with mock.patch.object(trial, "command", side_effect=commands):
                with self.assertRaisesRegex(trial.TrialError, "manifest is not on the reviewed backup volume"):
                    trial.verify_displaced_backup(manifest_path, pin,
                        expected_manifest_sha256=expected_hash,
                        approved_volume_id="approved-backup-uuid")

    def test_displaced_backup_path_missing_after_reboot_is_rejected(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            pin, manifest_path, expected_hash, _ = self._make_backup(directory)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            pathlib.Path(manifest["archive_path"]).unlink()
            with mock.patch.object(trial, "command", side_effect=self._backup_commands):
                with self.assertRaisesRegex(trial.TrialError, "archive is missing or unsafe"):
                    trial.verify_displaced_backup(manifest_path, pin,
                        expected_manifest_sha256=expected_hash,
                        approved_volume_id="approved-backup-uuid")

    def test_displaced_backup_rejects_archive_bytes_not_bound_to_payload_hash(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            pin, manifest_path, expected_hash, _ = self._make_backup(directory, corrupt_payload=True)
            with mock.patch.object(trial, "command", side_effect=self._backup_commands):
                with self.assertRaisesRegex(trial.TrialError, "archive hash mismatch for vmlinuz"):
                    trial.verify_displaced_backup(
                        manifest_path, pin,
                        expected_manifest_sha256=expected_hash,
                        approved_volume_id="approved-backup-uuid",
                    )

    def test_displaced_backup_rejects_unreviewed_manifest_or_volume(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            pin, manifest_path, expected_hash, _ = self._make_backup(directory)
            with self.assertRaisesRegex(trial.TrialError, "reviewed hash"):
                trial.verify_displaced_backup(
                    manifest_path, pin,
                    expected_manifest_sha256="0" * 64,
                    approved_volume_id="approved-backup-uuid",
                )
            with self.assertRaisesRegex(trial.TrialError, "reviewed volume identity"):
                trial.verify_displaced_backup(
                    manifest_path, pin,
                    expected_manifest_sha256=expected_hash,
                    approved_volume_id="other-volume-uuid",
                )

    def test_ack_and_expire_transitions_are_serialized(self):
        with tempfile.TemporaryDirectory() as directory:
            state_file = pathlib.Path(directory) / "state.json"
            state = {
                "schema_version": 1,
                "state": "pending",
                "kernel_release": "7.3.1-psycachy",
                "fallback_release": "7.3.0-10-generic",
                "fallback_entry": "fallback-entry",
                "required_units": ["ssh.service"],
                "runtime": {"script_created": False, "unit_files_created": []},
            }
            trial.write_state(state_file, state)
            reboots = []
            command_lock = threading.Lock()

            def fake_command(argv, *, allow_failure=False):
                with command_lock:
                    if argv[:3] == ["grub-editenv", "/boot/grub/grubenv", "list"]:
                        output = "saved_entry=fallback-entry\n"
                        return subprocess.CompletedProcess(argv, 0, output, "")
                    if argv[:2] == ["systemctl", "reboot"]:
                        reboots.append(True)
                    return subprocess.CompletedProcess(argv, 0, "", "")

            barrier = threading.Barrier(3)
            errors = []

            def run_ack():
                barrier.wait()
                try:
                    with trial.lock_state(state_file):
                        trial.acknowledge_locked(state_file)
                except trial.TrialError as exc:
                    errors.append(str(exc))

            def run_expire():
                barrier.wait()
                try:
                    with trial.lock_state(state_file):
                        trial.rollback_locked(state_file, expired=True)
                except trial.TrialError as exc:
                    errors.append(str(exc))

            with mock.patch.object(trial, "command", side_effect=fake_command), \
                    mock.patch.object(trial.os, "uname", return_value=types.SimpleNamespace(release="7.3.1-psycachy")), \
                    mock.patch.object(trial.os, "geteuid", return_value=0), \
                    mock.patch.object(trial, "verify_fallback_unchanged"):
                threads = [threading.Thread(target=run_ack), threading.Thread(target=run_expire)]
                for thread in threads:
                    thread.start()
                barrier.wait()
                for thread in threads:
                    thread.join(timeout=5)

            final = trial.read_state(state_file)
            self.assertIn(final["state"], {"acknowledged", "timeout_reboot_requested"})
            self.assertLessEqual(len(reboots), 1)
            self.assertEqual(len(errors), 1)

    def test_rollback_request_is_finalized_only_after_fallback_boots(self):
        with tempfile.TemporaryDirectory() as directory:
            state_file = pathlib.Path(directory) / "state.json"
            state = {
                "schema_version": 1,
                "state": "pending",
                "kernel_release": "7.3.1-psycachy",
                "fallback_release": "7.3.0-10-generic",
                "fallback_entry": "fallback-entry",
                "required_units": [],
                "runtime": {},
            }
            trial.write_state(state_file, state)
            commands = []
            reboot_attempts = []

            def fake_command(argv, *, allow_failure=False):
                commands.append(argv)
                if argv[:3] == ["grub-editenv", "/boot/grub/grubenv", "list"]:
                    return subprocess.CompletedProcess(argv, 0, "saved_entry=fallback-entry\n", "")
                if argv[:2] == ["systemctl", "reboot"]:
                    reboot_attempts.append(True)
                    if len(reboot_attempts) == 1:
                        raise trial.TrialError("simulated reboot command failure")
                return subprocess.CompletedProcess(argv, 0, "", "")

            with mock.patch.object(trial, "verify_fallback_unchanged"), \
                    mock.patch.object(trial, "grub_state", return_value={"saved_entry": "fallback-entry"}), \
                    mock.patch.object(trial, "command", side_effect=fake_command), \
                    mock.patch.object(trial.os, "uname", return_value=types.SimpleNamespace(release="7.3.1-psycachy")):
                with self.assertRaisesRegex(trial.TrialError, "simulated reboot"):
                    trial.rollback_locked(state_file)
                self.assertEqual(trial.read_state(state_file)["state"], "rollback_requested")
                trial.arm_timeout_locked(state_file)
                self.assertEqual(trial.read_state(state_file)["state"], "rollback_requested")

                with mock.patch.object(trial.os, "uname", return_value=types.SimpleNamespace(release="7.3.0-10-generic")), \
                        mock.patch.object(trial, "cleanup_runtime"):
                    final = trial.arm_timeout_locked(state_file)
            self.assertEqual(final["state"], "rolled_back")
            self.assertEqual(final["observed_kernel_release"], "7.3.0-10-generic")

    def test_promotion_requires_acknowledged_running_candidate_and_attestation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            state_file = root / "state.json"
            grubenv = root / "grubenv"
            grubenv.write_bytes(b"env")
            state = {"schema_version": 1, "state": "acknowledged",
                "kernel_release": "7.3.1-psycachy", "fallback_release": "7.3.0-10-generic",
                "fallback_entry": "fallback", "candidate_entry": "candidate",
                "secure_boot_mode": "enabled", "required_units": [], "runtime": {},
                "pin_sha256": "a" * 64, "candidate_payload_hashes": {"vmlinuz": "b" * 64},
                "machine_id": "c" * 32,
                "local_activation_identity": {"kernel_signing_certificate_sha256": "d" * 64,
                                               "module_signing_certificate_sha256": "e" * 64}}
            trial.write_state(state_file, state)
            current = {"saved_entry": "fallback", "next_entry": ""}
            calls = []

            def fake_command(argv, *, allow_failure=False):
                calls.append(argv)
                if argv[0] == "grub-editenv" and argv[2] == "set":
                    current["saved_entry"] = argv[3].split("=", 1)[1]
                return subprocess.CompletedProcess(argv, 0, "", "")

            with mock.patch.object(trial, "GRUBENV_PATH", grubenv), \
                    mock.patch.object(trial, "grub_state", side_effect=lambda _: dict(current)), \
                    mock.patch.object(trial, "command", side_effect=fake_command), \
                    mock.patch.object(trial, "verify_candidate_integrity") as integrity, \
                    mock.patch.object(trial, "verify_fallback_unchanged") as fallback, \
                    mock.patch.object(trial, "require_clean_packages"), \
                    mock.patch.object(trial, "verify_health_attestation", return_value={"sha256": "f" * 64}), \
                    mock.patch.object(trial.os, "uname", return_value=types.SimpleNamespace(release="7.3.1-psycachy")):
                promoted = trial.promote_locked(state_file, root / "attestation.json")
            self.assertEqual(promoted["state"], "promoted")
            self.assertEqual(current["saved_entry"], "candidate")
            integrity.assert_called_once_with(promoted, runtime=True)
            fallback.assert_called_once_with(promoted)
            self.assertEqual(calls[0][3], "saved_entry=candidate")

    def test_rollback_from_acknowledged_or_promoted_restores_fallback_default(self):
        for initial_state, default in (("acknowledged", "fallback"), ("promoted", "candidate")):
            with self.subTest(initial_state=initial_state), tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                state_file = root / "state.json"
                grubenv = root / "grubenv"
                grubenv.write_bytes(b"env")
                state = {"schema_version": 1, "state": initial_state,
                    "kernel_release": "7.3.1-psycachy", "fallback_release": "7.3.0-10-generic",
                    "fallback_entry": "fallback", "candidate_entry": "candidate",
                    "architecture": "amd64", "runtime": {}, "required_units": []}
                trial.write_state(state_file, state)
                grub = {"saved_entry": default, "next_entry": ""}
                commands = []

                def fake_command(argv, *, allow_failure=False):
                    commands.append(argv)
                    if argv[0] == "grub-editenv" and argv[2] == "set":
                        grub["saved_entry"] = argv[3].split("=", 1)[1]
                    if argv[:2] == ["systemctl", "reboot"]:
                        return subprocess.CompletedProcess(argv, 0, "", "")
                    return subprocess.CompletedProcess(argv, 0, "", "")

                with mock.patch.object(trial, "GRUBENV_PATH", grubenv), \
                        mock.patch.object(trial, "grub_state", side_effect=lambda _: dict(grub)), \
                        mock.patch.object(trial, "command", side_effect=fake_command), \
                        mock.patch.object(trial, "verify_fallback_unchanged"), \
                        mock.patch.object(trial.os, "uname", return_value=types.SimpleNamespace(release="7.3.1-psycachy")):
                    result = trial.rollback_locked(state_file)
                self.assertEqual(result["state"], "rollback_requested")
                self.assertEqual(grub["saved_entry"], "fallback")
                self.assertIn(["systemctl", "reboot"], commands)

    def test_prepare_parser_forbids_first_install_and_replacement_manifest_mix(self):
        with self.assertRaises(SystemExit):
            trial.build_parser().parse_args(["prepare", "--pin", "pin.json", "--packages", "pkgs",
                                             "--first-install", "--backup-manifest", "backup.json"])


class BuildManifestTests(unittest.TestCase):
    def test_amd64_build_manifest_hashes_trial_helper(self):
        script = (ROOT / "iso/build.sh").read_text(encoding="utf-8")
        rows = [line for line in script.splitlines()
                if "sha256sum" in line and "$root/tools/psycachy-secureboot.sh" in line]
        self.assertEqual(len(rows), 1)
        self.assertIn("$root/tools/phase2-kernel-trial.py", rows[0])


class PinValidationTests(unittest.TestCase):
    def test_current_amd64_pin_parses_as_candidate(self):
        pin = trial.read_pin(ROOT / "config/amd64-iso-kernel.json")
        self.assertEqual(pin["architecture"], "amd64")
        self.assertEqual(pin["kernel_release"], "7.3.1-psycachy")
        self.assertEqual(len(pin["packages"]), 2)
        self.assertEqual(pin["secure_boot"]["certificate_binding"], "per-install")
        self.assertIsNone(pin["secure_boot"]["kernel_certificate_sha256"])
        self.assertIsNone(pin["secure_boot"]["module_certificate_sha256"])
        self.assertEqual(pin["secure_boot"]["required_loaded_modules"], ["nvidia"])

    def test_current_arm64_pin_parses_as_candidate(self):
        pin = trial.read_pin(ROOT / "config/arm64-iso-kernel.json")
        self.assertEqual(pin["architecture"], "arm64")
        self.assertEqual(pin["kernel_release"], "7.3.1-psycachy-sp121")


if __name__ == "__main__":
    unittest.main()
