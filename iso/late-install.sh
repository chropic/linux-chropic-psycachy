#!/usr/bin/env bash
# Called by Subiquity after installing Ubuntu, before it reboots.
set -Eeuo pipefail
IFS=$'\n\t'
target=/target
media=/cdrom/psycachy
die() { echo "PsyCachy installer: $*" >&2; exit 1; }
[[ -d $target/etc && -d $media/repo && -d $media/helpers ]] || die 'target or installer files are missing'
mountpoint -q "$target/boot/efi" || die 'the target EFI partition is not mounted'
rootdev=$(findmnt -n -o SOURCE -T "$target")
efidev=$(findmnt -n -o SOURCE -T "$target/boot/efi")
rootdev=${rootdev%%\[*}
efidev=${efidev%%\[*}
disk_for() {
  lsblk -s -n -r -p -o TYPE,NAME "$1" | awk '$1 == "disk" {print $2}' | sort -u
}
rootdisk=$(disk_for "$rootdev")
efidisk=$(disk_for "$efidev")
[[ -n $rootdisk && $rootdisk == "$efidisk" && $rootdisk != *$'\n'* ]] || \
  die 'the root filesystem and EFI partition must be on the same dedicated disk'
mode_file=${PSYCACHY_ACTIVATION_MODE_FILE:-/run/psycachy/activation-mode.json}
[[ -f $mode_file && ! -L $mode_file && $(stat -c '%u:%a' "$mode_file") == 0:600 ]] || \
  die 'the root-owned pre-erase activation-mode decision is missing or unsafe'
disk_serial=$(udevadm info -q property -n "$rootdisk" | sed -n 's/^ID_SERIAL=//p')
[[ -n $disk_serial && $disk_serial != *$'\n'* ]] || die 'cannot identify the selected target disk serial'
python3 - "$mode_file" "$disk_serial" <<'PY'
import json, re, sys
record = json.load(open(sys.argv[1], encoding="utf-8"))
if record.get("schema_version") != 1 or record.get("disk_serial") != sys.argv[2]:
    raise SystemExit("activation mode does not match the selected target disk serial")
if record.get("mode") == "first-install":
    if record.get("operator_confirmed_no_displaced_candidate_payload") is not True or "backup" in record:
        raise SystemExit("first-install mode lacks its explicit no-displaced-candidate confirmation")
elif record.get("mode") == "replacement":
    backup = record.get("backup")
    if not isinstance(backup, dict) or set(backup) != {
        "manifest_path", "manifest_sha256", "volume_id", "verified_archive_sha256", "backup_disk_serial"
    }:
        raise SystemExit("replacement mode lacks verified backup evidence")
    if not re.fullmatch(r"[0-9a-f]{64}", backup["manifest_sha256"]):
        raise SystemExit("replacement manifest hash is malformed")
    if not re.fullmatch(r"[A-Za-z0-9_.:+-]{1,128}", backup["backup_disk_serial"]):
        raise SystemExit("replacement backup disk identity is malformed")
    if backup["backup_disk_serial"] == sys.argv[2]:
        raise SystemExit("replacement backup is on the disk being erased")
else:
    raise SystemExit("activation mode is absent or unknown")
PY
install -d -m 755 "$target/var/lib/psycachy"
install -m 600 "$mode_file" "$target/var/lib/psycachy/activation-mode.json"
desktop_network="$target/etc/netplan/01-network-manager-all.yaml"
if [[ ! -f $desktop_network || -L $desktop_network ]] || \
  ! grep -Eq '^[[:space:]]*renderer:[[:space:]]*NetworkManager[[:space:]]*$' "$desktop_network"; then
  die 'Ubuntu Desktop NetworkManager configuration is missing'
fi

install -d -m 755 "$target/usr/local/lib/psycachy" "$target/var/cache/psycachy/repo" \
  "$target/var/lib/psycachy" "$target/usr/local/sbin"
cp -a -- "$media/repo/." "$target/var/cache/psycachy/repo/"
for helper in install-target.sh psycachy-secureboot.sh configure-nvidia-dkms.sh \
  activate.sh activate-launcher.sh kernel-preinst kernel-postinst \
  phase2-kernel-trial.py; do
  install -m 755 "$media/helpers/$helper" "$target/usr/local/lib/psycachy/$helper"
done
install -m 755 "$media/helpers/phase2-kernel-trial.py" "$target/usr/local/sbin/phase2-kernel-trial"
install -m 644 "$media/helpers/amd64-kernel-pin.json" "$target/var/lib/psycachy/amd64-kernel-pin.json"
install -m 644 "$media/helpers/psycachy-activation.desktop" "$target/usr/local/lib/psycachy/psycachy-activation.desktop"
install -d -m 755 "$target/var/log"
log="$target/var/log/psycachy-installer.log"
[[ ! -L $log && ( ! -e $log || -f $log ) ]] || die 'invalid installer log path'
(umask 077; touch -- "$log")
chmod 600 "$log"
printf '\n--- PsyCachy installer attempt ---\n' >> "$log"
touch "$target/var/lib/psycachy/installer-target"
trap 'rm -f -- "$target/var/lib/psycachy/installer-target"' EXIT
curtin in-target -- env PSYCACHY_INSTALLER_TARGET=1 /bin/bash /usr/local/lib/psycachy/install-target.sh /var/cache/psycachy/repo \
  2>&1 | tee -a "$log"
# The offline live session causes Subiquity to write a link-local-only
# Ethernet profile. Restore the Desktop default before the installed boot.
rm -f -- "$target/etc/netplan/00-installer-config.yaml"
rm -rf -- "$target/var/cache/psycachy/repo"
