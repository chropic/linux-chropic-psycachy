#!/usr/bin/env bash
# Run inside the newly installed target, with its offline repository staged.
set -Eeuo pipefail
IFS=$'\n\t'
export DEBIAN_FRONTEND=noninteractive
die() { echo "PsyCachy installation: $*" >&2; exit 1; }
(( EUID == 0 )) || die 'run as root'
(( $# == 1 )) || die "usage: $0 OFFLINE_REPOSITORY"
[[ ${PSYCACHY_INSTALLER_TARGET:-} == 1 && -f /var/lib/psycachy/installer-target ]] || \
  die 'run only through the installer target handoff'
repo=$(realpath -- "$1")
[[ -f $repo/Packages && -f $repo/SHA256SUMS ]] || die 'offline repository is incomplete'
helper=/usr/local/lib/psycachy/psycachy-secureboot.sh
override=/usr/local/lib/psycachy/configure-nvidia-dkms.sh
activate=/usr/local/lib/psycachy/activate.sh
launcher=/usr/local/lib/psycachy/activate-launcher.sh
desktop=/usr/local/lib/psycachy/psycachy-activation.desktop
trial=/usr/local/sbin/phase2-kernel-trial
preinst=/usr/local/lib/psycachy/kernel-preinst
postinst=/usr/local/lib/psycachy/kernel-postinst
[[ -f $helper && -f $override && -f $activate && -x $launcher && -f $desktop && -f $preinst && -f $postinst && -x $trial ]] || die 'PsyCachy helpers are missing'
(cd "$repo" && sha256sum --check --strict SHA256SUMS)
mode_file=/var/lib/psycachy/activation-mode.json
[[ -f $mode_file && ! -L $mode_file && $(stat -c '%u:%a' "$mode_file") == 0:600 ]] || \
  die 'the verified pre-erase activation-mode record is missing or unsafe'
python3 - "$mode_file" "$repo" /var/lib/psycachy/amd64-kernel-pin.json <<'PY'
import json, re, subprocess, sys
from pathlib import Path
record = json.load(open(sys.argv[1], encoding="utf-8"))
if record.get("schema_version") != 1 or record.get("mode") not in {"first-install", "replacement"}:
    raise SystemExit("missing or unknown activation mode")
pin = json.load(open(sys.argv[3], encoding="utf-8"))
if record["mode"] == "first-install":
    if record.get("operator_confirmed_no_displaced_candidate_payload") is not True or "backup" in record:
        raise SystemExit("invalid first-install activation mode")
elif not isinstance(record.get("backup"), dict):
    raise SystemExit("replacement activation mode has no verified backup record")
packages = pin.get("packages")
if pin.get("architecture") != "amd64" or not isinstance(packages, list) or len(packages) != 2:
    raise SystemExit("the embedded AMD64 kernel pin is invalid")
root = Path(sys.argv[2])
for item in packages:
    filename = item.get("filename", "")
    if Path(filename).name != filename or not filename.endswith(".deb"):
        raise SystemExit("unsafe pinned package filename")
    package = root / filename
    if not package.is_file() or package.is_symlink():
        raise SystemExit(f"pinned package is absent from the installer repository: {filename}")
    actual = subprocess.check_output(["sha256sum", str(package)], text=True).split()[0]
    if actual != item.get("sha256"):
        raise SystemExit(f"pinned package hash mismatch: {filename}")
PY
candidate_release=$(python3 -c 'import json; print(json.load(open("/var/lib/psycachy/amd64-kernel-pin.json"))["kernel_release"])')
[[ $candidate_release =~ ^[A-Za-z0-9.+_-]+-psycachy$ ]] || die 'pinned candidate release is invalid'

sources=$(mktemp /run/psycachy-sources.XXXXXXXX)
preferences=$(mktemp /run/psycachy-preferences.XXXXXXXX)
trap 'rm -f -- "$sources" "$preferences"' EXIT
printf 'deb [trusted=yes] file:%s ./\n' "$repo" > "$sources"
while IFS=$'\t' read -r package version; do
  [[ $package == linux-* ]] && continue
  printf 'Package: %s\nPin: version %s\nPin-Priority: 1001\n\n' "$package" "$version" >> "$preferences"
done < <(dpkg-query -W -f='${Package}\t${Version}\n')
apt_opts=(-o "Dir::Etc::sourcelist=$sources" -o Dir::Etc::sourceparts=-
  -o "Dir::Etc::preferences=$preferences" -o Dir::Etc::preferencesparts=-)
apt-get "${apt_opts[@]}" update
# The offline closure is resolved against the pinned package archive, while the
# Desktop base can contain newer revisions of shared compiler libraries. Keep
# already-installed packages at their base-image versions; install missing
# dependencies from the local archive and upgrade the kernel metapackages.
apt-get "${apt_opts[@]}" -y --no-install-recommends install \
  linux-generic linux-headers-generic linux-generic-hwe-26.04 \
  linux-headers-generic-hwe-26.04 \
  clang-22 llvm-22 lld-22 dkms mokutil sbsigntool openssl keyutils xterm

# Keep the newest Ubuntu generic kernel supplied by the pinned offline package
# repository as fallback. Its version follows the ISO's 26.10 package set.
fallback_image=$(find /boot -maxdepth 1 -type f -name 'vmlinuz-*-generic' -printf '%f\n' | sort -V | tail -n 1)
[[ $fallback_image == vmlinuz-*-generic ]] || die 'no Ubuntu generic fallback kernel is installed'
fallback=${fallback_image#vmlinuz-}
[[ -f /boot/initrd.img-$fallback ]] || die "missing initramfs for Ubuntu fallback $fallback"
printf '%s\n' "$fallback" > /var/lib/psycachy/fallback-release
chmod 600 /var/lib/psycachy/fallback-release
# The installer does not always regenerate the target GRUB menu after the
# fallback kernel package is added. Rebuild it before checking that entry.
update-grub
uuid=$(grub-probe --target=fs_uuid /)
[[ $uuid =~ ^[A-Za-z0-9-]+$ ]] || die 'could not determine the root filesystem UUID'
submenu="gnulinux-advanced-$uuid"
entry="gnulinux-$fallback-advanced-$uuid"
grep -Fq "$submenu" /boot/grub/grub.cfg || die 'Ubuntu GRUB submenu is missing'
grep -Fq "$entry" /boot/grub/grub.cfg || die 'Ubuntu fallback GRUB entry is missing'
conf=/etc/default/grub.d/99-psycachy.cfg
[[ ! -e $conf && ! -L $conf ]] || die "$conf already exists"
install -d -m 755 /etc/default/grub.d
cat > "$conf" <<'EOF'
GRUB_DEFAULT=saved
GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=10
EOF
grub-set-default "$submenu>$entry"
update-grub
grub-editenv list | grep -Fxq "saved_entry=$submenu>$entry" || die 'could not save Ubuntu fallback'

# Keys belong to this installation and are generated before any DKMS builds.
bash "$helper" init
bash "$helper" configure-dkms
bash "$override"
mapfile -t nvidia_packages < <(python3 - "$repo" /var/lib/psycachy/nvidia-package-identity.json <<'PY'
from pathlib import Path
import re
import subprocess
import sys
import hashlib
import json
import os

records = {}
for deb in Path(sys.argv[1]).glob("*.deb"):
    result = subprocess.run(["dpkg-deb", "-f", str(deb), "Package", "Version"],
                            check=True, capture_output=True, text=True)
    fields = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition(": ")
        if separator:
            fields[key] = value
    package, version = fields.get("Package"), fields.get("Version")
    if not package or not version:
        continue
    if re.fullmatch(r"nvidia-(?:driver|dkms)-[A-Za-z0-9.+-]+-open", package):
        if package in records:
            raise SystemExit(f"offline repository contains duplicate NVIDIA package: {package}")
        with deb.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        records[package] = {"version": version, "filename": deb.name,
                            "sha256": digest}
drivers = [name for name in records if name.startswith("nvidia-driver-")]
dkms = [name for name in records if name.startswith("nvidia-dkms-")]
pairs = [(driver, module) for driver in drivers for module in dkms
         if driver.removeprefix("nvidia-driver-") == module.removeprefix("nvidia-dkms-")
         and records[driver]["version"] == records[module]["version"]]
if len(pairs) != 1:
    raise SystemExit("offline repository must identify one matching NVIDIA driver/DKMS pair")
identity = {"schema_version": 1, "architecture": "amd64",
            "packages": [{"name": name, **records[name]} for name in sorted(pairs[0])]}
identity_path = Path(sys.argv[2])
identity_path.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
os.chmod(identity_path, 0o600)
print(*pairs[0], sep="\n")
PY
)
(( ${#nvidia_packages[@]} == 2 )) || die 'offline repository has no unique NVIDIA package pair'
apt-get "${apt_opts[@]}" -y --no-install-recommends install \
  "${nvidia_packages[@]}" \
  "linux-headers-$candidate_release" "linux-image-$candidate_release"
bash "$helper" sign-installed "$candidate_release"
# The target's package hooks can skip GRUB regeneration in the installer
# chroot. Generate entries after all kernels are installed, before activation.
update-grub
grep -Fq "'gnulinux-$candidate_release-advanced-$uuid'" /boot/grub/grub.cfg || \
  die 'PsyCachy GRUB entry is missing after update-grub'
grep -Fq "'$entry'" /boot/grub/grub.cfg || die 'Ubuntu fallback GRUB entry is missing after update-grub'
grub-editenv list | grep -Fxq "saved_entry=$submenu>$entry" || die 'Ubuntu fallback changed during installation'
kernels=("$candidate_release")
for image in /boot/vmlinuz-*-generic; do
  [[ -f $image ]] || continue
  kernels+=("${image#/boot/vmlinuz-}")
done
(( ${#kernels[@]} > 1 )) || die 'no Ubuntu fallback kernel is installed'
for kernel in "${kernels[@]}"; do
  dkms status -m nvidia -k "$kernel" | grep -q ': installed' || \
    die "NVIDIA DKMS is not installed for $kernel"
  while IFS= read -r module; do
    [[ -n $module ]] || continue
    [[ $(modinfo -k "$kernel" -F sig_id "$module") == PKCS#7 ]] || \
      die "NVIDIA module $module has no PKCS#7 signature for $kernel"
    module_path=$(modinfo -k "$kernel" -n "$module")
    [[ -f $module_path && ! -L $module_path ]] || die "NVIDIA module payload is missing for $kernel: $module"
  done < <(python3 - /var/lib/psycachy/amd64-kernel-pin.json <<'PY'
import json, sys
pin = json.load(open(sys.argv[1], encoding="utf-8"))
for module in pin.get("secure_boot", {}).get("required_module_signers", {}):
    print(module)
PY
)
done
[[ -z $(dpkg --audit) ]] || die 'dpkg reports unfinished package operations'
install -d -m 700 /var/lib/psycachy/candidate-packages
mapfile -t candidate_files < <(python3 - /var/lib/psycachy/amd64-kernel-pin.json <<'PY'
import json, sys
pin = json.load(open(sys.argv[1], encoding="utf-8"))
for item in pin["packages"]:
    print(item["filename"])
PY
)
(( ${#candidate_files[@]} == 2 )) || die 'the pinned kernel package pair is incomplete'
for package in "${candidate_files[@]}"; do
  [[ -f $repo/$package && ! -L $repo/$package ]] || die "pinned package is missing: $package"
  install -m 600 "$repo/$package" /var/lib/psycachy/candidate-packages/
done
install -d -m 755 /var/lib/psycachy
install -D -m 644 "$desktop" /usr/share/applications/psycachy-activation.desktop
install -D -m 644 "$desktop" /etc/xdg/autostart/psycachy-activation.desktop
install -D -m 755 "$preinst" /etc/kernel/preinst.d/psycachy-fallback
install -D -m 755 "$postinst" /etc/kernel/postinst.d/zzzz-psycachy-sign
printf '%s\n' "$candidate_release" > /var/lib/psycachy/pending-kernel
touch /var/lib/psycachy/installer-packages-ready
echo 'PsyCachy packages installed. Ubuntu remains the default pending activation.'
