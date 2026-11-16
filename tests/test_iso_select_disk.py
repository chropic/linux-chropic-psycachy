#!/usr/bin/env python3
"""Check disk-selection safety without accessing real disks."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("select_disk", ROOT / "iso/select-disk.py")
SELECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SELECT)


class DiskSelectionTest(unittest.TestCase):
    def test_filters_unsafe_disks(self):
        disks = [
            {"path": "/dev/good", "serial": "good-123", "ro": False, "mounted": False},
            {"path": "/dev/media", "serial": "media-1", "ro": False, "mounted": False},
            {"path": "/dev/mounted", "serial": "mount-1", "ro": False, "mounted": True},
            {"path": "/dev/read-only", "serial": "ro-1", "ro": True, "mounted": False},
            {"path": "/dev/duplicate-a", "serial": "same", "ro": False, "mounted": False},
            {"path": "/dev/duplicate-b", "serial": "same", "ro": True, "mounted": False},
            {"path": "/dev/wildcard", "serial": "bad*", "ro": False, "mounted": False},
            {"path": "/dev/no-serial", "serial": "", "ro": False, "mounted": False},
        ]
        self.assertEqual([disk["path"] for disk in SELECT.eligible_disks(disks, {"/dev/media"})],
                         ["/dev/good"])
        self.assertTrue(SELECT.mounted({"mountpoints": [None], "children": [{"mountpoints": ["/mnt"]}]}))
        self.assertFalse(SELECT.mounted({"mountpoints": [None], "children": []}))

    def test_confirmation_is_required(self):
        disk = {"path": "/dev/test", "model": "Test", "serial": "test-123", "size": 64000000000}
        for results in ([(1, "")], [(0, "")], [(0, "/dev/test"), (0, "NO")],
                        [(0, "/dev/test"), (1, "")]):
            with self.subTest(results=results), mock.patch.object(SELECT, "dialog", side_effect=results), \
                    mock.patch.object(SELECT, "select_activation_mode", return_value={
                        "schema_version": 1, "mode": "first-install", "disk_serial": "test-123",
                        "operator_confirmed_no_displaced_candidate_payload": True
                    }):
                with self.assertRaises(ValueError):
                    SELECT.choose_disk([], [disk], Path("pin.json"), Path("mode.json"))
        mode = {"schema_version": 1, "mode": "first-install", "disk_serial": "test-123",
                "operator_confirmed_no_displaced_candidate_payload": True}
        with mock.patch.object(SELECT, "dialog", side_effect=[(0, "/dev/test"), (0, "ERASE")]), \
                mock.patch.object(SELECT, "select_activation_mode", return_value=mode), \
                mock.patch.object(SELECT, "write_activation_mode") as write:
            self.assertEqual(SELECT.choose_disk([], [disk], Path("pin.json"), Path("mode.json")), disk)
            write.assert_called_once_with(Path("mode.json"), mode)

    def test_cancelling_disk_selection_never_records_activation_or_storage(self):
        disk = {"path": "/dev/test", "model": "Test", "serial": "test-123", "size": 64000000000}
        with mock.patch.object(SELECT, "dialog", return_value=(1, "")), \
                mock.patch.object(SELECT, "select_activation_mode") as choose_mode, \
                mock.patch.object(SELECT, "write_activation_mode") as write:
            with self.assertRaisesRegex(ValueError, "cancelled or empty"):
                SELECT.choose_disk([], [disk], Path("pin.json"), Path("mode.json"))
            choose_mode.assert_not_called()
            write.assert_not_called()

    def test_cancelling_mode_or_erase_never_records_activation(self):
        disk = {"path": "/dev/test", "model": "Test", "serial": "test-123", "size": 64000000000}
        with mock.patch.object(SELECT, "dialog", return_value=(1, "")), \
                mock.patch.object(SELECT, "write_activation_mode") as write:
            with self.assertRaisesRegex(ValueError, "explicit installation mode"):
                SELECT.select_activation_mode([], disk, Path("pin.json"), Path("."))
            write.assert_not_called()

        mode = {"schema_version": 1, "mode": "first-install", "disk_serial": "test-123",
                "operator_confirmed_no_displaced_candidate_payload": True}
        with mock.patch.object(SELECT, "dialog", side_effect=[(0, "/dev/test"), (1, "")]), \
                mock.patch.object(SELECT, "select_activation_mode", return_value=mode), \
                mock.patch.object(SELECT, "write_activation_mode") as write:
            with self.assertRaisesRegex(ValueError, "erasure was not confirmed"):
                SELECT.choose_disk([], [disk], Path("pin.json"), Path("mode.json"))
            write.assert_not_called()

    def test_mode_omission_fails_before_any_erase_decision_is_recorded(self):
        disk = {"path": "/dev/test", "model": "Test", "serial": "test-123", "size": 64000000000}
        with mock.patch.object(SELECT, "dialog", side_effect=[(0, "/dev/test"), (0, "ERASE")]), \
                mock.patch.object(SELECT, "write_activation_mode") as write:
            with self.assertRaisesRegex(ValueError, "explicit first-install/replacement"):
                SELECT.choose_disk([], [disk])
            write.assert_not_called()

    def test_mode_record_is_root_owned_private_and_not_overwritable(self):
        with tempfile.TemporaryDirectory() as directory:
            mode = Path(directory) / "run" / "activation-mode.json"
            mode.parent.mkdir()
            record = {"schema_version": 1, "mode": "first-install", "disk_serial": "disk-A",
                      "operator_confirmed_no_displaced_candidate_payload": True}
            with mock.patch.object(SELECT.os, "geteuid", return_value=0):
                SELECT.write_activation_mode(mode, record)
                self.assertEqual(mode.stat().st_mode & 0o777, 0o600)
                self.assertEqual(json.loads(mode.read_text()), record)
                with self.assertRaises(ValueError):
                    SELECT.write_activation_mode(mode, record)

    def test_replacement_mode_rejects_missing_backup_fields_and_bad_hash(self):
        disk = {"path": "/dev/test", "model": "Test", "serial": "test-123", "size": 64000000000}
        inputs = [(0, "replacement"), (0, "/missing/manifest.json"), (0, "bad"), (0, "backup-uuid")]
        with mock.patch.object(SELECT, "dialog", side_effect=inputs):
            with self.assertRaisesRegex(ValueError, "valid reviewed manifest hash"):
                SELECT.select_activation_mode([], disk, Path("pin.json"), Path("."))

    def test_unknown_media_ancestry_fails_closed(self):
        with mock.patch.object(SELECT, "command", side_effect=["/dev/loop0", "loop /dev/loop0", "loop"]):
            with self.assertRaisesRegex(ValueError, "installer media"):
                SELECT.discover()

    def test_discovers_cd_boot_and_rejects_mounted_partition(self):
        devices = {"blockdevices": [
            {"path": "/dev/vda", "type": "disk", "ro": False, "size": 100,
             "children": [{"mountpoints": ["/mnt/data"]}]},
            {"path": "/dev/vdb", "type": "disk", "ro": False, "size": 100,
             "children": [{"mountpoints": [None]}]},
        ]}
        results = ["/dev/sr0", "rom /dev/sr0", "rom", json.dumps(devices),
                   "ID_SERIAL=mounted-1", "ID_SERIAL=good-1"]
        with mock.patch.object(SELECT, "command", side_effect=results):
            self.assertEqual([disk["path"] for disk in SELECT.discover()], ["/dev/vdb"])

    def test_configuration_is_pinned_and_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "autoinstall.yaml"
            original = {"version": 1, "source": {"id": "ubuntu-desktop"},
                        "early-commands": [["true"]], "interactive-sections": ["*"]}
            config.write_text(yaml.safe_dump(original))
            SELECT.configure(config, "disk-123")
            result = yaml.safe_load(config.read_text())
            self.assertEqual(result["storage"]["layout"],
                             {"name": "direct", "match": {"serial": "disk-123"}})
            self.assertEqual(result["interactive-sections"], SELECT.INTERACTIVE)
            self.assertEqual(result["source"], original["source"])
            self.assertEqual(result["early-commands"], original["early-commands"])
            before = config.read_bytes()
            with self.assertRaises(ValueError):
                SELECT.configure(config, "disk*")
            self.assertEqual(config.read_bytes(), before)
            link = Path(directory) / "link.yaml"
            link.symlink_to(config)
            with self.assertRaises(ValueError):
                SELECT.configure(link, "disk-123")


if __name__ == "__main__":
    unittest.main()
