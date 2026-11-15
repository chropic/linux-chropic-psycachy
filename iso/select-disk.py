#!/usr/bin/env python3
"""Require an explicit, confirmed disk before Subiquity configures storage."""
from collections import Counter
import json
import importlib.util
import os
from pathlib import Path
import pwd
import re
import stat
import subprocess
import tempfile
import time

import yaml

SERIAL = re.compile(r"[A-Za-z0-9_.:+-]{1,128}\Z")
INTERACTIVE = ["locale", "keyboard", "identity", "timezone"]
MODE_FILE = Path("/run/psycachy/activation-mode.json")


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def mounted(device):
    return any(device.get("mountpoints") or []) or any(
        mounted(child) for child in device.get("children", [])
    )


def eligible_disks(disks, media_disks):
    counts = Counter(disk.get("serial", "") for disk in disks)
    return [disk for disk in disks if not disk.get("ro") and not disk.get("mounted")
            and disk["path"] not in media_disks and SERIAL.fullmatch(disk.get("serial", ""))
            and counts[disk["serial"]] == 1]


def discover():
    source = command("findmnt", "-n", "-o", "SOURCE", "--target", "/cdrom").split("[")[0]
    parents = command("lsblk", "-s", "-n", "-r", "-p", "-o", "TYPE,NAME", source)
    media = {line.split()[1] for line in parents.splitlines() if line.startswith("disk ")}
    if not media and command("lsblk", "-n", "-d", "-o", "TYPE", source) != "rom":
        raise ValueError("cannot identify the installer media disk")
    devices = json.loads(command("lsblk", "-b", "-J", "--tree", "-o", "PATH,TYPE,SIZE,MODEL,RO,MOUNTPOINTS"))
    disks = []
    for device in devices["blockdevices"]:
        if device.get("type") != "disk" or not device.get("path"):
            continue
        properties = command("udevadm", "info", "-q", "property", "-n", device["path"])
        serial = next((line[10:] for line in properties.splitlines() if line.startswith("ID_SERIAL=")), "")
        disks.append({"path": device["path"], "serial": serial, "size": device.get("size") or 0,
                      "model": device.get("model") or "Disk", "ro": device.get("ro"),
                      "mounted": mounted(device)})
    return eligible_disks(disks, media)


def desktop_command():
    account = pwd.getpwnam("ubuntu")
    runtime = Path(f"/run/user/{account.pw_uid}")
    for _ in range(30):
        sockets = sorted(p for p in runtime.glob("wayland-*") if stat.S_ISSOCK(p.stat().st_mode))
        if sockets:
            return ["runuser", "-u", "ubuntu", "--", "env", f"XDG_RUNTIME_DIR={runtime}",
                    f"WAYLAND_DISPLAY={sockets[0].name}",
                    f"DBUS_SESSION_BUS_ADDRESS=unix:path={runtime}/bus"]
        authority = runtime / "gdm/Xauthority"
        if authority.is_file() and Path("/tmp/.X11-unix/X0").exists():
            return ["runuser", "-u", "ubuntu", "--", "env", f"XDG_RUNTIME_DIR={runtime}",
                    "DISPLAY=:0", f"XAUTHORITY={authority}",
                    f"DBUS_SESSION_BUS_ADDRESS=unix:path={runtime}/bus"]
        time.sleep(1)
    raise ValueError("the live graphical session is unavailable")


def dialog(base, args):
    process = subprocess.Popen(base + ["zenity"] + args, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, _ = process.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        try:
            subprocess.run(base + ["notify-send", "--urgency=critical", "Disk selection required",
                                   "If the selection dialog is hidden, press Alt+Tab."],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass
        stdout, _ = process.communicate()
    return process.returncode, stdout.strip()


def configure(config, serial):
    if not SERIAL.fullmatch(serial) or not config.is_file() or config.is_symlink():
        raise ValueError("unsafe disk serial or autoinstall configuration")
    document = yaml.safe_load(config.read_text())
    if not isinstance(document, dict):
        raise ValueError("invalid autoinstall configuration")
    section = document.get("autoinstall", document)
    if not isinstance(section, dict) or section.get("version") != 1:
        raise ValueError("unexpected autoinstall version")
    section["interactive-sections"] = INTERACTIVE
    section["storage"] = {"layout": {"name": "direct", "match": {"serial": serial}}}
    with tempfile.NamedTemporaryFile("w", dir=config.parent, delete=False) as output:
        try:
            yaml.safe_dump(document, output, sort_keys=False)
            output.flush()
            os.fsync(output.fileno())
            os.chmod(output.name, stat.S_IMODE(config.stat().st_mode))
            os.replace(output.name, config)
        finally:
            if os.path.exists(output.name):
                os.unlink(output.name)


def select_activation_mode(base, disk, pin_path, backup_root):
    result, mode = dialog(base, ["--list", "--radiolist", "--modal", "--width=850", "--height=320",
        "--title=Choose installation mode",
        "--text=First-install means no prior PsyCachy candidate payload is displaced. Replacement requires a verified independent backup.",
        "--column=Select", "--column=Mode", "--column=Requirement", "--print-column=2",
        "TRUE", "first-install", "No prior PsyCachy candidate payload is displaced",
        "FALSE", "replacement", "Verified archive, manifest, hash, and backup volume"])
    if result != 0 or mode not in {"first-install", "replacement"}:
        raise ValueError("an explicit installation mode is required")
    if mode == "first-install":
        result, answer = dialog(base, ["--entry", "--modal", "--width=800", "--title=Confirm first install",
            "Use only when no prior PsyCachy candidate payload is displaced. This does not preserve other disk contents. Type FIRST-INSTALL."])
        if result != 0 or answer != "FIRST-INSTALL":
            raise ValueError("first-install mode was not explicitly confirmed")
        return {"schema_version": 1, "mode": mode, "disk_serial": disk["serial"],
                "operator_confirmed_no_displaced_candidate_payload": True}

    result, manifest = dialog(base, ["--file-selection", "--modal", "--title=Select verified displaced-payload manifest"])
    if result != 0 or not manifest:
        raise ValueError("replacement requires the actual displaced-payload manifest")
    result, digest = dialog(base, ["--entry", "--modal", "--title=Reviewed manifest SHA-256",
                                   "Enter the independently reviewed manifest SHA-256."])
    if result != 0 or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("replacement requires a valid reviewed manifest hash")
    result, volume = dialog(base, ["--entry", "--modal", "--title=Independent backup volume UUID",
                                   "Enter the reviewed UUID of the independent backup volume."])
    if result != 0 or not volume.strip():
        raise ValueError("replacement requires the independent backup-volume UUID")
    spec = importlib.util.spec_from_file_location("phase2_kernel_trial", backup_root / "phase2-kernel-trial.py")
    if spec is None or spec.loader is None:
        raise ValueError("the pinned backup verifier is unavailable")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    pin = verifier.read_pin(pin_path)
    try:
        verified = verifier.verify_displaced_backup(Path(manifest), pin,
            expected_manifest_sha256=digest, approved_volume_id=volume.strip(),
            target_disk_serial=disk["serial"])
    except verifier.TrialError as error:
        raise ValueError(f"replacement backup verification failed: {error}") from error
    return {"schema_version": 1, "mode": mode, "disk_serial": disk["serial"],
            "backup": {"manifest_path": str(Path(manifest).resolve()),
                       "manifest_sha256": digest, "volume_id": volume.strip(),
                       "verified_archive_sha256": verified["archive_sha256"],
                       "backup_disk_serial": verified["backup_disk_serial"]}}


def write_activation_mode(path, record):
    if (os.geteuid() != 0 or path.is_symlink() or path.exists()
            or path.parent.is_symlink()):
        raise ValueError("activation mode path is unsafe or already exists")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    if path.parent.is_symlink():
        raise ValueError("activation mode directory is unsafe")
    fd, temporary = tempfile.mkstemp(prefix=".activation-mode.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(record, output, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def choose_disk(base, disks, pin_path=None, mode_path=MODE_FILE):
    items = []
    for disk in disks:
        items.extend(["FALSE", disk["path"], disk["model"], disk["serial"],
                      f"{disk['size'] / 1_000_000_000:.1f} GB"])
    result, choice = dialog(base, ["--list", "--radiolist", "--modal", "--width=850", "--height=430",
        "--title=Select the dedicated Linux disk", "--text=Select one disk. Its contents will be erased.",
        "--column=Select", "--column=Device", "--column=Model", "--column=Serial", "--column=Size",
        "--print-column=2"] + items)
    selected = next((disk for disk in disks if disk["path"] == choice), None)
    if result != 0 or selected is None:
        raise ValueError("disk selection was cancelled or empty")
    mode_record = None
    if pin_path is not None:
        mode_record = select_activation_mode(base, selected, pin_path, pin_path.parent)
    result, answer = dialog(base, ["--entry", "--modal", "--width=650", "--title=Confirm disk erasure",
        f"--text=All data on {selected['path']} ({selected['serial']}) will be erased. Type ERASE to continue."])
    if result != 0 or answer != "ERASE":
        raise ValueError("disk erasure was not confirmed")
    if mode_record is None:
        raise ValueError("an explicit first-install/replacement decision is required before erasure")
    write_activation_mode(mode_path, mode_record)
    return selected


def main():
    if os.geteuid() != 0 or not Path("/sys/firmware/efi").is_dir():
        raise ValueError("root and UEFI boot are required")
    subprocess.run(["udevadm", "settle", "--timeout=15"], check=True)
    disks = discover()
    if not disks:
        raise ValueError("no unmounted disk with a unique stable serial was found")
    base = desktop_command()
    # The installer opens its loading window during early commands.
    time.sleep(5)
    selected = choose_disk(base, disks, Path("/cdrom/psycachy/helpers/amd64-kernel-pin.json"))
    if not any(disk["path"] == selected["path"] and disk["serial"] == selected["serial"] for disk in discover()):
        raise ValueError("the selected disk changed or became unavailable")
    configure(Path("/autoinstall.yaml"), selected["serial"])
    print("PsyCachy disk selection confirmed.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, yaml.YAMLError) as error:
        raise SystemExit(f"PsyCachy disk selection: {error}") from error
