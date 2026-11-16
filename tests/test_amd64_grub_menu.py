#!/usr/bin/env python3
"""Exercise the signed-base AMD64 Try/Rescue and guarded-install menu."""
import importlib.util
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("amd64_grub", ROOT / "iso/amd64_grub.py")
GRUB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GRUB)


BASE = """set timeout=30

loadfont unicode

set menu_color_normal=white/black
set menu_color_highlight=black/light-gray

menuentry \"Try or Install Ubuntu\" {
    set gfxpayload=keep
    linux  /casper/vmlinuz --- quiet splash
    initrd /casper/initrd
}
menuentry \"Ubuntu (safe graphics)\" {
    set gfxpayload=keep
    linux  /casper/vmlinuz nomodeset --- quiet splash
    initrd /casper/initrd
}
grub_platform
if [ \"$grub_platform\" = \"efi\" ]; then
menuentry 'Boot from next volume' {
    exit 1
}
menuentry 'UEFI Firmware Settings' {
    fwsetup
}
fi
"""


class Amd64GrubMenuTests(unittest.TestCase):
    def test_live_rescue_is_default_and_only_install_entry_loads_autoinstall(self):
        result = GRUB.build_menu(BASE)
        self.assertIn("set default=0\n", result)
        entries = GRUB._entries(result)
        self.assertEqual(entries[0][0], GRUB.TRY_TITLE)
        live = GRUB._only_entry(entries, GRUB.TRY_TITLE)[3]
        installer = GRUB._only_entry(entries, GRUB.INSTALL_TITLE)[3]
        safe = GRUB._only_entry(entries, GRUB.SAFE_TITLE)[3]
        self.assertIn("linux  /casper/vmlinuz --- quiet splash", live)
        self.assertNotIn("autoinstall", " ".join(GRUB._kernel_lines(live)))
        self.assertIn("linux  /casper/vmlinuz autoinstall " + GRUB.AUTOINSTALL_PATH + " --- quiet splash", installer)
        self.assertIn("initrd /casper/initrd", installer)
        self.assertIn("linux  /casper/vmlinuz nomodeset --- quiet splash", safe)
        self.assertNotIn("autoinstall", " ".join(GRUB._kernel_lines(safe)))
        self.assertEqual(sum(GRUB._has_autoinstall(line) for _, _, _, block in entries
                             for line in GRUB._kernel_lines(block)), 1)

    def test_refuses_duplicate_or_missing_base_entries(self):
        with self.assertRaisesRegex(GRUB.GrubMenuError, "exactly one"):
            GRUB.build_menu(BASE.replace("menuentry \"Ubuntu (safe graphics)\"", "menuentry \"Try or Install Ubuntu\""))
        with self.assertRaisesRegex(GRUB.GrubMenuError, "exactly one"):
            GRUB.build_menu(BASE.replace("menuentry \"Ubuntu (safe graphics)\"", "menuentry \"Safe graphics\""))

    def test_refuses_ambiguous_separator_and_preexisting_autoinstall(self):
        with self.assertRaisesRegex(GRUB.GrubMenuError, "exactly one ---"):
            GRUB.build_menu(BASE.replace("/casper/vmlinuz ---", "/casper/vmlinuz quiet"))
        with self.assertRaisesRegex(GRUB.GrubMenuError, "already load autoinstall"):
            GRUB.build_menu(BASE.replace("/casper/vmlinuz ---", "/casper/vmlinuz autoinstall ---", 1))

    def test_refuses_unbalanced_entries_and_existing_default(self):
        with self.assertRaisesRegex(GRUB.GrubMenuError, "unbalanced"):
            GRUB.build_menu(BASE.replace("    initrd /casper/initrd\n}", "    initrd /casper/initrd\n", 1))
        with self.assertRaisesRegex(GRUB.GrubMenuError, "already defines a default"):
            GRUB.build_menu(BASE.replace("set timeout=30", "set timeout=30\nset default=1"))

    def test_iso_builder_stores_config_under_psycachy_not_media_root(self):
        build = (ROOT / "iso/build.sh").read_text(encoding="utf-8")
        self.assertEqual(GRUB.AUTOINSTALL_PATH,
                         "subiquity.autoinstallpath=/cdrom/psycachy/autoinstall.yaml")
        self.assertIn('install -m 644 "$root/iso/autoinstall.yaml" "$work/payload/autoinstall.yaml"', build)
        self.assertNotIn('"$root/iso/autoinstall.yaml" /autoinstall.yaml', build)
        self.assertIn('"$work/payload" /psycachy', build)

    def test_cli_replaces_read_only_xorriso_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "grub.cfg"
            config.write_text(BASE, encoding="utf-8")
            config.chmod(0o444)
            result = subprocess.run([sys.executable, str(ROOT / "iso/amd64_grub.py"), str(config)],
                                    text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(stat.S_IMODE(config.stat().st_mode), 0o444)
            self.assertIn("set default=0", config.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
