#!/usr/bin/env python3
"""Focused tests for the AMD64 compiler native-target fail-closed guard."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
TARGET_LINE = ' "/usr/lib/llvm-22/bin/clang" "-cc1" "-target-cpu" "znver3"'


class Amd64CpuTargetGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="amd64-cpu-target-")
        self.root = Path(self.temp.name) / "repo"
        (self.root / "config").mkdir(parents=True)
        (self.root / "build.sh").write_bytes((REPO / "build.sh").read_bytes())
        (self.root / "config/source-pin.sh").write_bytes(
            (REPO / "config/source-pin.sh").read_bytes()
        )
        self.pin_path = self.root / "config/amd64-iso-kernel.json"
        self.write_pin({"architecture": "amd64", "cpu_target": "znver3"})
        self.bin_dir = Path(self.temp.name) / "bin"
        self.bin_dir.mkdir()
        clang = self.bin_dir / "clang-22"
        clang.write_text(
            "#!/bin/sh\n"
            "if [ -n \"${FAKE_CLANG_MARKER:-}\" ]; then : > \"$FAKE_CLANG_MARKER\"; fi\n"
            "if [ \"${FAKE_CLANG_EXIT:-0}\" != 0 ]; then exit \"$FAKE_CLANG_EXIT\"; fi\n"
            "printf '%s\\n' \"${FAKE_CLANG_OUTPUT:-}\"\n",
            encoding="utf-8",
        )
        clang.chmod(0o755)

    def tearDown(self):
        self.temp.cleanup()

    def write_pin(self, pin):
        self.pin_path.write_text(json.dumps(pin), encoding="utf-8")

    def run_builder(self, *args, output=TARGET_LINE, clang_exit=0, clang_marker=None):
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}:{env['PATH']}"
        env["FAKE_CLANG_OUTPUT"] = output
        env["FAKE_CLANG_EXIT"] = str(clang_exit)
        if clang_marker is not None:
            env["FAKE_CLANG_MARKER"] = str(clang_marker)
        return subprocess.run(
            ["bash", str(self.root / "build.sh"), *args],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_matching_native_target_reports_expected_and_detected(self):
        result = self.run_builder("--verify-cpu-target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cpu_target_expected=znver3", result.stdout)
        self.assertIn("cpu_target_detected=znver3", result.stdout)

    def test_mismatched_native_target_fails_closed(self):
        result = self.run_builder(
            "--verify-cpu-target",
            output=TARGET_LINE.replace("znver3", "znver2"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match pinned cpu_target", result.stderr)

    def test_clang_probe_failure_fails_closed(self):
        result = self.run_builder("--verify-cpu-target", clang_exit=17)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Clang failed to detect", result.stderr)

    def test_malformed_pin_fails_closed(self):
        self.write_pin({"architecture": "amd64", "cpu_target": "znver3 unsafe"})
        result = self.run_builder("--verify-cpu-target")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("valid cpu_target", result.stderr)

    def test_missing_or_ambiguous_clang_target_fails_closed(self):
        missing = self.run_builder("--verify-cpu-target", output="clang: no cc1 command")
        ambiguous = self.run_builder(
            "--verify-cpu-target",
            output=TARGET_LINE + "\n" + TARGET_LINE,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertNotEqual(ambiguous.returncode, 0)
        self.assertIn("missing, ambiguous, or malformed", missing.stderr)
        self.assertIn("missing, ambiguous, or malformed", ambiguous.stderr)

    def test_malformed_clang_target_output_fails_closed(self):
        unterminated = self.run_builder(
            "--verify-cpu-target",
            output=' "/clang" "-cc1" "-target-cpu" "znver3',
        )
        missing_value = self.run_builder(
            "--verify-cpu-target",
            output=' "/clang" "-cc1" "-target-cpu"',
        )
        self.assertNotEqual(unterminated.returncode, 0)
        self.assertNotEqual(missing_value.returncode, 0)
        self.assertIn("missing, ambiguous, or malformed", unterminated.stderr)
        self.assertIn("missing, ambiguous, or malformed", missing_value.stderr)

    def test_target_diagnostic_rejects_unknown_and_incompatible_arguments(self):
        unknown = self.run_builder("--verify-cpu-target", "--bogus")
        dry_run = self.run_builder("--verify-cpu-target", "--dry-run")
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("unsupported argument", unknown.stderr)
        self.assertNotEqual(dry_run.returncode, 0)
        self.assertIn("cannot be combined with --dry-run", dry_run.stderr)

    def test_arm64_dry_run_keeps_existing_dispatch(self):
        result = self.run_builder("--target", "sp121-arm64", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Target: sp121-arm64", result.stdout)
        self.assertIn("SP12 ARM64:", result.stdout)
        self.assertNotIn("cpu_target_expected", result.stdout)
        self.assertNotIn("cpu_target_detected", result.stdout)

    def test_arm64_target_rejects_cpu_guard_before_invoking_clang(self):
        marker = Path(self.temp.name) / "clang-was-called"
        result = self.run_builder(
            "--target", "sp121-arm64", "--verify-cpu-target", clang_marker=marker
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("applies only to b550i-amd64", result.stderr)
        self.assertFalse(marker.exists(), "ARM64 diagnostic unexpectedly invoked Clang")

    def test_resolved_config_guard_is_wired_after_final_olddefconfig(self):
        script = (REPO / "build.sh").read_text(encoding="utf-8")
        final_resolution = script.index('make -C "$source_dir" LLVM=-22 olddefconfig',
                                        script.index('merge_config.sh'))
        config_guard = script.index('verify_native_cpu_config "$source_dir/.config"')
        compilation = script.index('bindeb-pkg', config_guard)
        self.assertLess(final_resolution, config_guard)
        self.assertLess(config_guard, compilation)
        self.assertIn("CONFIG_X86_NATIVE_CPU=y", script)
        self.assertIn("# CONFIG_GENERIC_CPU is not set", script)


if __name__ == "__main__":
    unittest.main()
