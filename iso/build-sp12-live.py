#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build an experimental Ubuntu 26.10 live ISO with the maintained SP12 kernel.

Private machine support is optional and must be explicitly selected. No image
with that support may be published by this project. File hashes and provenance
are pinned in config/sp121-live-support.json; machine files stay outside Git.
"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import struct
import stat
import sys
import tarfile
import tempfile
import uuid
import zlib

ROOT = Path(__file__).resolve().parent.parent
BASE_PIN = ROOT / 'config/arm64-iso-base.json'
KERNEL_PIN = ROOT / 'config/arm64-iso-kernel.json'
SUPPORT_PIN = ROOT / 'config/sp121-live-support.json'
LAYER = 'minimal.standard.live.sp12.squashfs'
LIVE_DTB = '/casper/x1p42100-microsoft-sp12in.dtb'
MODULES = ['overlay', 'isofs', 'usb_storage', 'uas', 'xhci_plat_hcd',
           'phy_qcom_qmp_combo', 'phy_qcom_snps_femto_v2', 'ufs_qcom',
           'phy_qcom_qmp_ufs', 'pinctrl_x1e80100', 'gcc_x1e80100',
           'qnoc_x1e80100', 'qcom_rpmh_regulator', 'msm', 'panel_edp',
           'ath12k', 'ath12k_wifi7', 'snd_soc_x1e80100', 'qcom_q6v5_pas']

VERIFY_SPEC = importlib.util.spec_from_file_location(
    'verify_arm64_packages', ROOT / 'tools/verify-arm64-packages.py')
VERIFY_MODULE = importlib.util.module_from_spec(VERIFY_SPEC)
VERIFY_SPEC.loader.exec_module(VERIFY_MODULE)
verify_arm64_packages = VERIFY_MODULE.verify_arm64_packages
ISO_SPEC = importlib.util.spec_from_file_location('arm64_iso', ROOT / 'iso/arm64_iso.py')
ISO_MODULE = importlib.util.module_from_spec(ISO_SPEC)
ISO_SPEC.loader.exec_module(ISO_MODULE)


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_support_pin(path=SUPPORT_PIN):
    pin = load_json(path)
    if pin.get('schema_version') != 1 or pin.get('device') != 'sp121-arm64':
        raise ValueError('unsupported SP12 live support pin')
    commit = pin.get('support_source_commit', '')
    files = pin.get('machine_files')
    if not re.fullmatch(r'[0-9a-f]{40}', commit) or not isinstance(files, dict) or len(files) != 4:
        raise ValueError('SP12 live support pin must identify the source commit and four files')
    expected_files = {
        'usr/lib/firmware/ath12k/WCN7850/hw2.0/board.bin',
        'usr/lib/firmware/qcom/x1e80100/X1P42100-Microsoft-Surface-Pro-12in-tplg.bin',
        'usr/share/alsa/ucm2/Qualcomm/x1e80100/MICROSOFT-Surface-Pro-12in.conf',
        'usr/share/alsa/ucm2/Qualcomm/x1e80100/Surface12in-HiFi.conf',
    }
    if set(files) != expected_files:
        raise ValueError('SP12 live support pin must use the reviewed four-file allowlist')
    if pin.get('source_allowlist') != ['lib/firmware/qcom', 'usr/share/qcom']:
        raise ValueError('SP12 live support pin has an unexpected source checkout allowlist')
    if pin.get('redistribute_machine_files') is not False:
        raise ValueError('SP12 machine support files must remain local-only')
    sources = pin.get('support_sources', {})
    if sources.get('firmware_platform', {}).get('commit') != commit:
        raise ValueError('SP12 support source provenance does not match its checkout pin')
    for source in ('firmware_platform', 'audio_topology', 'wifi_board', 'alsa_ucm'):
        record = sources.get(source, {})
        if not re.fullmatch(r'[0-9a-f]{40}', record.get('commit', '')):
            raise ValueError('SP12 live support source has an invalid commit: ' + source)
    derived_outputs = {
        'audio_topology': (
            'usr/lib/firmware/qcom/x1e80100/X1P42100-Microsoft-Surface-Pro-12in-tplg.bin'),
        'wifi_board': 'usr/lib/firmware/ath12k/WCN7850/hw2.0/board.bin',
        'alsa_ucm': 'usr/share/alsa/ucm2/Qualcomm/x1e80100/Surface12in-HiFi.conf',
    }
    for source, relative in derived_outputs.items():
        if sources.get(source, {}).get('output_sha256') != files[relative]:
            raise ValueError('SP12 support source output does not match machine-file pin: ' + source)
    for relative, digest in files.items():
        if (Path(relative).is_absolute() or '..' in Path(relative).parts
                or not re.fullmatch(r'[0-9a-f]{64}', digest)):
            raise ValueError('SP12 live support pin contains an unsafe path or invalid hash')
    return pin


def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def output(*args):
    return subprocess.check_output([str(a) for a in args], text=True)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def grub_config(text, private_support=False, installer_enabled=False):
    lines = text.splitlines(keepends=True)
    matches = [index for index, line in enumerate(lines)
               if re.match(r'^\s*linux(?:efi)?\s+/casper/vmlinuz(?:\s|$)', line)]
    require(len(matches) == 1, 'Unexpected live kernel menu layout')
    index = matches[0]
    line = lines[index]
    require('---' in line, 'Live GRUB kernel command has no Ubuntu argument separator')
    before, after = line.split('---', 1)
    words = before.split()
    require(not any(word == 'autoinstall' or word.startswith('autoinstall=') for word in words),
            'Refusing an autoinstall live kernel command')
    words = [word for word in words if word != 'maybe-ubiquity']
    words.extend(['boot=casper', 'layerfs-path=' + LAYER, 'cma=128M', 'efi=noruntime'])
    require(words.count('boot=casper') == 1 and
            sum(word.startswith('layerfs-path=') for word in words) == 1,
            'Base live GRUB command already contains conflicting casper layer arguments')
    lines[index] = ' '.join(words) + ' ---' + after
    indentation = line[:len(line) - len(line.lstrip())]
    lines[index:index] = [indentation + 'insmod fdt\n',
                          indentation + 'devicetree ' + LIVE_DTB + '\n']
    label = ('Try SP12 Ubuntu 26.10 (private local live)' if private_support
             else 'Try SP12 Ubuntu 26.10 (experimental live)')
    result = ''.join(lines)
    require(result.count('Try or Install Ubuntu') == 1,
            'Expected exactly one Ubuntu live-session menu label')
    result = result.replace('Try or Install Ubuntu', label)
    require(not re.search(r'\bautoinstall(?:=\S+)?\b', result),
            'Autoinstall remains enabled in the SP12 live menu')
    require(result.count('devicetree ' + LIVE_DTB) == 1,
            'SP12 live menu does not select exactly one pinned DTB')
    return append_installer_menu(result) if installer_enabled else result


def append_installer_menu(text):
    """Add explicit installer and generic-QEMU entries without changing default."""
    require(text.count('Try SP12 Ubuntu 26.10') == 1,
            'Expected exactly one default SP12 Try entry before installer menus')
    install = (
        '\nmenuentry "Install SP12 (guarded)" {\n'
        '    insmod fdt\n'
        '    devicetree ' + LIVE_DTB + '\n'
        '    set gfxpayload=keep\n'
        '    linux /casper/vmlinuz boot=casper layerfs-path=' + LAYER +
        ' cma=128M efi=noruntime autoinstall --- quiet splash console=tty0\n'
        '    initrd /casper/initrd\n'
        '}\n'
        'menuentry "Install SP12 (generic QEMU diagnostic)" {\n'
        '    set gfxpayload=keep\n'
        '    linux /casper/qemu-vmlinuz boot=casper autoinstall --- quiet splash console=tty0\n'
        '    initrd /casper/qemu-initrd\n'
        '}\n'
    )
    result = text.rstrip() + '\n' + install
    require(result.count('menuentry "Install SP12 (guarded)"') == 1,
            'SP12 installer menu entry is missing or duplicated')
    require(result.count('devicetree ' + LIVE_DTB) == 2,
            'Install and Try entries must use the pinned SP12 DTB')
    generic = re.search(r'(?ms)menuentry "Install SP12 \(generic QEMU diagnostic\)"\s*\{([^}]*)\}',
                        result)
    require(generic is not None and 'devicetree' not in generic.group(1),
            'Generic QEMU diagnostic entry must not use the Surface DTB')
    require(re.search(r'(?ms)menuentry "Try SP12 Ubuntu 26\.10[^\"]*"\s*\{([^}]*)\}',
                      result).group(1).find('autoinstall') == -1,
            'Default SP12 Try entry must not enable autoinstall')
    require(re.search(r'(?ms)menuentry "Install SP12 \(guarded\)"\s*\{([^}]*)\}',
                      result).group(1).count('autoinstall') == 1,
            'Explicit SP12 installer entry must use the guarded autoinstall flow')
    return result


def installer_autoinstall_config(text):
    """Require the installer ISO's interactive selector and target late command."""
    require(text.count('/cdrom/psycachy/select-disk.py') == 1
            and re.search(r'(?m)^early-commands:\s*$', text),
            'Installer ISO must use the guarded early disk selector')
    require(re.search(r"(?ms)^interactive-sections:\s*\n[ \t]+-[ \t]*['\"]?\*['\"]?[ \t]*\n",
                      text),
            'Installer ISO must keep all installer sections interactive')
    require(text.count('/cdrom/psycachy/install-arm64-target.sh') == 1
            and re.search(r'(?m)^late-commands:\s*$', text),
            'Installer ISO must use the guarded target late-install flow')
    require(not re.search(r'(?m)^storage\s*:', text),
            'Installer ISO must not bypass the explicit disk selector')
    lines = text.splitlines(keepends=True)
    matches = [index for index, line in enumerate(lines)
               if re.fullmatch(r"[ \t]*-[ \t]*\[bash,[ \t]*/cdrom/psycachy/install-arm64-target\.sh\][ \t]*(?:\n)?",
                               line)]
    require(len(matches) == 1, 'Installer late-install command layout is ambiguous')
    require(text.count('/cdrom/psycachy/install-private-support.sh') == 0,
            'Installer config already contains the SP12 support late command')
    lines.insert(matches[0] + 1,
                 '  - [bash, /cdrom/psycachy/install-private-support.sh]\n')
    return ''.join(lines)


def private_support_manifest(support_files):
    """Serialize the exact target support tree copied from validated inputs."""
    lines = []
    for relative, digest in sorted(support_files.items()):
        path = Path(relative)
        require(not path.is_absolute() and '..' not in path.parts
                and path.as_posix() == relative
                and '\t' not in relative and '\n' not in relative
                and re.fullmatch(r'[0-9a-f]{64}', digest) is not None,
                'Private target support manifest contains an unsafe path or hash')
        lines.append(f'{digest}\t{relative}')
    require(lines, 'Private target support manifest is empty')
    return '\n'.join(lines) + '\n'


def collect_source_support(extracted, support_pin):
    """Hash the commit-pinned source trees using their target installation paths."""
    root = Path(extracted).resolve(strict=True)
    result = {}
    for source_tree in support_pin['source_allowlist']:
        source_root = root / source_tree
        require(source_root.is_dir() and not source_root.is_symlink(),
                'Pinned source support tree is missing or unsafe: ' + source_tree)
        for current, directories, files in os.walk(source_root, followlinks=False):
            current_path = Path(current)
            for dirname in directories:
                candidate = current_path / dirname
                require(not candidate.is_symlink()
                        and candidate.resolve(strict=True).is_relative_to(root),
                        'Pinned source support tree contains an unsafe directory symlink')
            for filename in files:
                candidate = current_path / filename
                relative = candidate.relative_to(root).as_posix()
                resolved = candidate.resolve(strict=True)
                require(resolved.is_relative_to(root) and resolved.is_file(),
                        'Pinned source support tree contains a non-file or escaping link: '
                        + relative)
                target_relative = 'usr/' + relative if relative.startswith('lib/') else relative
                require(target_relative not in result,
                        'Pinned source support trees have a target path collision: ' + target_relative)
                result[target_relative] = sha(resolved)
    return result


def private_support_install_script(support_files):
    """Create a late command installing the generated path/hash manifest."""
    manifest = private_support_manifest(support_files)
    manifest_hash = hashlib.sha256(manifest.encode()).hexdigest()
    lines = [
        '#!/usr/bin/env bash',
        'set -Eeuo pipefail',
        'IFS=$\'\\n\\t\'',
        'target=/target',
        'media=/cdrom/psycachy/private-support',
        'die() { echo "SP12 private support install: $*" >&2; exit 1; }',
        '[[ -d $target/etc && -d $media ]] || die "target or private support files are missing"',
        'pin=/cdrom/psycachy/config/arm64-iso-kernel.json',
        'identity_tool=/cdrom/psycachy/iso/kernel_identity.py',
        'identity_args=()',
        'if [[ -f /cdrom/psycachy/config/arm64-kernel-identity.json ]]; then',
        '  identity_args=(--identity /cdrom/psycachy/config/arm64-kernel-identity.json)',
        'fi',
        'release=$(python3 "$identity_tool" "${identity_args[@]}" --artifact-pin "$pin" --field kernel_release)',
        '[[ -n $release ]] || die "cannot resolve the pinned kernel release"',
        'manifest=$media/SHA256SUMS',
        f'expected_manifest_hash={manifest_hash}',
        '[[ -f $manifest && ! -L $manifest ]] || die "support manifest is missing or unsafe"',
        'manifest_hash=$(sha256sum "$manifest" | awk \'{print $1}\')',
        '[[ $manifest_hash == "$expected_manifest_hash" ]] || die "support manifest hash differs"',
        "while IFS=$'\\t' read -r expected relative; do",
        '  [[ -n $expected && -n $relative && $relative != /* && $relative != *..* ]] || die "unsafe support manifest row"',
        '  source=$media/$relative',
        '  destination=$target/$relative',
        '  [[ -f $source && ! -L $source ]] || die "missing regular support source: $relative"',
        '  source_resolved=$(realpath -e "$source")',
        '  [[ $source_resolved == "$media"/* ]] || die "support source escapes media: $relative"',
        '  source_hash=$(sha256sum "$source" | awk \'{print $1}\')',
        '  [[ $source_hash == "$expected" ]] || die "support source hash differs: $relative"',
        '  mkdir -p -- "$(dirname "$destination")"',
        '  [[ ! -L $destination ]] || die "refusing support destination symlink: $relative"',
        '  resolved=$(realpath -m "$destination")',
        '  [[ $resolved == "$target"/* ]] || die "support destination escapes target: $relative"',
        '  install -m 0644 -- "$source" "$destination"',
        '  target_hash=$(sha256sum "$destination" | awk \'{print $1}\')',
        '  [[ $target_hash == "$expected" ]] || die "installed support hash differs: $relative"',
        'done < "$manifest"',
    ]
    lines.extend([
        'curtin in-target --target="$target" -- update-initramfs -u -k "$release"',
        'initrd=$target/boot/initrd.img-$release',
        'esp_initrd=$target/boot/efi/sp12/initrd.img',
        '[[ -s $initrd && ! -L $initrd ]] || die "regenerated target initramfs is missing"',
        '[[ -f $esp_initrd && ! -L $esp_initrd ]] || die "SP12 ESP initramfs is missing after update"',
        'cmp -s -- "$initrd" "$esp_initrd" || die "SP12 ESP initramfs was not synchronized"',
        'audit=$(dpkg --root="$target" --audit)',
        '[[ -z $audit ]] || die "target dpkg audit is not clean: $audit"',
        'echo "Installed and hash-verified SP12 support manifest; regenerated and synchronized $release initramfs."',
        '',
    ])
    return '\n'.join(lines)


def validate_installer_checksum(installer_iso, expected_sha256):
    require(isinstance(expected_sha256, str)
            and re.fullmatch(r'[0-9a-f]{64}', expected_sha256) is not None,
            'Installer ISO requires an exact lowercase SHA-256 checksum')
    path = Path(installer_iso)
    require(path.is_file() and not path.is_symlink(),
            'Installer ISO must be a regular non-symlink file')
    actual = sha(path)
    require(actual == expected_sha256, 'Installer ISO hash differs from the supplied checksum')
    return actual


@contextmanager
def private_installer_snapshot(installer_iso, expected_sha256, parent=None,
                               expected_size=None):
    """Make a private stable ISO snapshot while hashing exactly the copied bytes."""
    require(isinstance(expected_sha256, str)
            and re.fullmatch(r'[0-9a-f]{64}', expected_sha256) is not None,
            'Installer ISO requires an exact lowercase SHA-256 checksum')
    source_path = Path(installer_iso)
    source_lstat = source_path.lstat()
    require(stat.S_ISREG(source_lstat.st_mode),
            'Installer ISO source must be a regular non-symlink file')
    temporary = tempfile.TemporaryDirectory(prefix='.sp12-installer-snapshot.', dir=parent)
    try:
        temporary_path = Path(temporary.name)
        os.chmod(temporary_path, 0o700)
        snapshot_path = temporary_path / 'installer.iso'
        source_fd = os.open(source_path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        destination_fd = None
        try:
            source_before = os.fstat(source_fd)
            require(stat.S_ISREG(source_before.st_mode)
                    and (source_before.st_dev, source_before.st_ino) ==
                    (source_lstat.st_dev, source_lstat.st_ino),
                    'Installer ISO source changed during safe open')
            require(expected_size is None or source_before.st_size == expected_size,
                    'Installer ISO source size changed before snapshot')
            destination_fd = os.open(
                snapshot_path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o600)
            digest = hashlib.sha256()
            copied = 0
            while True:
                block = os.read(source_fd, 1024 * 1024)
                if not block:
                    break
                require(expected_size is None or copied + len(block) <= expected_size,
                        'Installer ISO source grew beyond its checked size')
                digest.update(block)
                copied += len(block)
                view = memoryview(block)
                while view:
                    written = os.write(destination_fd, view)
                    require(written > 0, 'Short write while copying installer ISO snapshot')
                    view = view[written:]
            os.fsync(destination_fd)
            destination_stat = os.fstat(destination_fd)
            source_after = os.fstat(source_fd)
            source_path_after = source_path.lstat()
            require(stat.S_ISREG(destination_stat.st_mode)
                    and stat.S_IMODE(destination_stat.st_mode) == 0o600
                    and destination_stat.st_size == copied,
                    'Installer ISO snapshot is not the expected regular private file')
            source_identity_before = (source_before.st_dev, source_before.st_ino,
                                      source_before.st_size, source_before.st_mtime_ns,
                                      source_before.st_ctime_ns)
            source_identity_after = (source_after.st_dev, source_after.st_ino,
                                     source_after.st_size, source_after.st_mtime_ns,
                                     source_after.st_ctime_ns)
            require(stat.S_ISREG(source_after.st_mode)
                    and source_identity_after == source_identity_before
                    and (expected_size is None or copied == expected_size)
                    and stat.S_ISREG(source_path_after.st_mode)
                    and (source_path_after.st_dev, source_path_after.st_ino) ==
                    (source_after.st_dev, source_after.st_ino),
                    'Installer ISO source changed while being snapshotted')
        finally:
            os.close(source_fd)
            if destination_fd is not None:
                os.close(destination_fd)
        directory_fd = os.open(temporary_path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        snapshot_stat = snapshot_path.lstat()
        require(stat.S_ISREG(snapshot_stat.st_mode)
                and stat.S_IMODE(snapshot_stat.st_mode) == 0o600
                and (snapshot_stat.st_dev, snapshot_stat.st_ino) ==
                (destination_stat.st_dev, destination_stat.st_ino),
                'Installer ISO snapshot path no longer identifies its private regular file')
        actual = digest.hexdigest()
        require(actual == expected_sha256,
                'Installer ISO snapshot hash differs from the supplied checksum')
        yield snapshot_path, actual
    finally:
        temporary.cleanup()


def validate_installer_payload(installer_root, autoinstall_path, selected_pin,
                               installer_iso_sha256):
    """Verify the embedded installer pin, package pair, and guarded flow."""
    root = Path(installer_root)
    pin_path = root / 'config/arm64-iso-kernel.json'
    manifest_path = root / 'kernel-bundle/bundle-manifest.json'
    bundle_sums_path = root / 'kernel-bundle/SHA256SUMS'
    verification_path = root / 'kernel-bundle/package-verification.json'
    repository_sums_path = root / 'repository/SHA256SUMS'
    for path in (pin_path, manifest_path, bundle_sums_path, verification_path,
                 repository_sums_path):
        require(path.is_file() and not path.is_symlink(),
                'Installer ISO is missing a regular pinned metadata file: ' + str(path.relative_to(root)))
    embedded_pin = ISO_MODULE.validate_pin_pair(load_json(pin_path))
    require(embedded_pin == selected_pin,
            'Installer ISO kernel pin differs from the selected kernel pin')
    pin_digest = sha(pin_path)
    manifest = load_json(manifest_path)
    require(manifest.get('schema') == 1 and manifest.get('target') == 'sp121-arm64'
            and manifest.get('status') == 'verified-target-installer-bundle',
            'Installer bundle manifest has an unsupported identity or status')
    require(manifest.get('kernel_pin_sha256') == pin_digest,
            'Installer bundle manifest does not match its embedded kernel pin')
    for field, pin_field in (('kernel_release', 'kernel_release'),
                             ('package_version', 'debian_version'),
                             ('architecture', 'architecture'),
                             ('dtb_path', 'dtb_path'), ('dtb_sha256', 'dtb_sha256')):
        require(manifest.get(field) == selected_pin[pin_field],
                'Installer bundle manifest differs from selected pin: ' + field)
    packages = {item['name']: item for item in selected_pin['packages']}
    aliases = {
        'linux-image.deb': next(item for item in packages.values()
                                if item['name'].startswith('linux-image-')),
        'linux-headers.deb': next(item for item in packages.values()
                                  if item['name'].startswith('linux-headers-')),
    }
    require(manifest.get('files') == {name: item['sha256'] for name, item in aliases.items()},
            'Installer bundle package hashes differ from selected pin')
    bundle_sums = ISO_MODULE.parse_sha256sums(bundle_sums_path)
    repo_sums = ISO_MODULE.parse_sha256sums(repository_sums_path)
    package_report = load_json(verification_path)
    require(package_report.get('status') == 'verified-package-structure'
            and package_report.get('kernel_release') == selected_pin['kernel_release']
            and package_report.get('package_version') == selected_pin['debian_version']
            and package_report.get('architecture') == selected_pin['architecture'],
            'Installer package verification identity differs from selected pin')
    for alias, item in aliases.items():
        package = root / 'kernel-bundle' / alias
        repo_package = root / 'repository' / item['filename']
        require(package.is_file() and not package.is_symlink()
                and sha(package) == item['sha256'],
                'Installer kernel bundle package differs from selected pin: ' + alias)
        require(repo_package.is_file() and not repo_package.is_symlink()
                and sha(repo_package) == item['sha256'],
                'Installer repository package differs from selected pin: ' + item['filename'])
        require(bundle_sums.get(alias) == item['sha256']
                and repo_sums.get(item['filename']) == item['sha256'],
                'Installer package checksum index differs from selected pin: ' + alias)
        control = output('dpkg-deb', '-f', package, 'Package', 'Version', 'Architecture')
        fields = {}
        for line in control.splitlines():
            key, value = line.split(': ', 1)
            fields[key] = value
        require(fields.get('Package') == item['name']
                and fields.get('Version') == selected_pin['debian_version']
                and fields.get('Architecture') == selected_pin['architecture'],
                'Installer package metadata differs from selected pin: ' + alias)
        repository_control = output('dpkg-deb', '-f', repo_package,
                                    'Package', 'Version', 'Architecture')
        require(repository_control == control,
                'Installer repository package metadata differs from kernel bundle: ' + alias)
    image = next(item for item in packages.values() if item['name'].startswith('linux-image-'))
    headers = next(item for item in packages.values() if item['name'].startswith('linux-headers-'))
    require(package_report.get('image_package', {}).get('sha256') == image['sha256']
            and package_report.get('headers_package', {}).get('sha256') == headers['sha256'],
            'Installer package-verification record differs from selected package pair')
    require(package_report.get('dtb', {}).get('path') == selected_pin['dtb_path']
            and package_report.get('dtb', {}).get('sha256') == selected_pin['dtb_sha256'],
            'Installer DTB verification record differs from selected pin')
    guarded_config = installer_autoinstall_config(
        Path(autoinstall_path).read_text(encoding='utf-8'))
    return {
        'iso_sha256': installer_iso_sha256,
        'kernel_pin_sha256': pin_digest,
        'kernel_release': selected_pin['kernel_release'],
        'package_version': selected_pin['debian_version'],
        'package_hashes': {item['filename']: item['sha256']
                           for item in selected_pin['packages']},
        'autoinstall_sha256': hashlib.sha256(guarded_config.encode()).hexdigest(),
    }


def extract_installer_validation_files(installer_iso, destination, xorriso, selected_pin):
    """Extract only the metadata and pinned package pair needed for preflight."""
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    paths = [
        '/autoinstall.yaml',
        '/psycachy/config/arm64-iso-kernel.json',
        '/psycachy/kernel-bundle/bundle-manifest.json',
        '/psycachy/kernel-bundle/SHA256SUMS',
        '/psycachy/kernel-bundle/package-verification.json',
        '/psycachy/kernel-bundle/linux-image.deb',
        '/psycachy/kernel-bundle/linux-headers.deb',
        '/psycachy/repository/SHA256SUMS',
    ]
    for item in selected_pin['packages']:
        paths.append('/psycachy/repository/' + item['filename'])
    arguments = [xorriso, '-osirrox', 'on', '-indev', installer_iso]
    for source in paths:
        relative = Path(source.lstrip('/'))
        output_path = root / relative
        output_path.parent.mkdir(parents=True, exist_ok=True)
        arguments.extend(['-extract', source, output_path])
    arguments.append('-end')
    run(*arguments, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return root / 'psycachy', root / 'autoinstall.yaml'


def extract_installer_payload(installer_iso, destination, xorriso):
    """Extract the already validated installer tree for inclusion in the live ISO."""
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    psycachy = root / 'psycachy'
    config = root / 'autoinstall.yaml'
    run(xorriso, '-osirrox', 'on', '-indev', installer_iso,
        '-extract', '/psycachy', psycachy,
        '-extract', '/autoinstall.yaml', config, '-end',
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    require((psycachy / 'config/arm64-iso-kernel.json').is_file()
            and config.is_file(), 'Installer payload extraction was incomplete')
    return psycachy, config


def esp_digest(image):
    with image.open('rb') as stream:
        stream.seek(512)
        header = bytearray(stream.read(512))
        require(header[:8] == b'EFI PART', 'Missing GPT header')
        size, crc = struct.unpack_from('<II', header, 12)
        require(92 <= size <= 512, 'Invalid GPT header size')
        struct.pack_into('<I', header, 16, 0)
        require(zlib.crc32(header[:size]) == crc, 'GPT header CRC mismatch')
        lba = struct.unpack_from('<Q', header, 72)[0]
        count, entry_size, crc = struct.unpack_from('<III', header, 80)
        require(count <= 4096 and 128 <= entry_size <= 1024, 'Invalid GPT table geometry')
        stream.seek(lba * 512)
        entries = stream.read(count * entry_size)
        require(zlib.crc32(entries) == crc, 'GPT table CRC mismatch')
        hashes = []
        for n in range(count):
            entry = entries[n * entry_size:(n + 1) * entry_size]
            if uuid.UUID(bytes_le=entry[:16]) != uuid.UUID('c12a7328-f81f-11d2-ba4b-00a0c93ec93b'):
                continue
            first, last = struct.unpack_from('<QQ', entry, 32)
            require(first <= last and (last + 1) * 512 <= image.stat().st_size, 'ESP outside image')
            stream.seek(first * 512)
            hashes.append(hashlib.sha256(stream.read((last - first + 1) * 512)).hexdigest())
        require(len(hashes) == 1, 'Expected exactly one ESP')
        return hashes[0]


def validate_esp_mount(mount):
    fields = mount.strip().split()
    require(len(fields) == 4 and fields[1] == '/boot/efi',
            'Physical ESP is not mounted exactly at /boot/efi')
    require(fields[2] in {'vfat', 'fat', 'fat32'},
            'Physical ESP mount is not FAT formatted')
    require('ro' in fields[3].split(','),
            'Physical ESP must be mounted read-only during the build')
    return mount


def snapshot():
    mount = validate_esp_mount(output(
        'findmnt', '-n', '-o', 'SOURCE,TARGET,FSTYPE,OPTIONS',
        '--mountpoint', '/boot/efi'))
    files = sorted(p for p in Path('/boot/efi').rglob('*') if p.is_file())
    require(files, 'Physical ESP is unavailable for comparison')
    return {'esp': {str(p): sha(p) for p in files},
            'nvram': output('efibootmgr', '-v'),
            'mount': mount}


def cleanup_mounts(mounts, before):
    errors = []
    for destination in reversed(mounts):
        # Chroot initramfs hooks can create nested mounts below /sys.
        # Every destination is a mount we created inside the private scratch tree.
        result = subprocess.run(['umount', '--recursive', str(destination)])
        if result.returncode:
            errors.append(str(destination))
    # Always compare physical state, even when an unmount failed.
    require(snapshot() == before, 'Physical-device comparison failed')
    require(not errors, 'Unmount failed: ' + ', '.join(errors))


def publish_outputs(partial, final, buildinfo_source, owner):
    """Publish a validated ISO and sidecars only after cleanup has succeeded."""
    checksum = Path(str(final) + '.sha256')
    sidecar = Path(str(final) + '.buildinfo.json')
    require(partial.is_file() and not partial.is_symlink(),
            'Validated partial ISO is missing or unsafe')
    require(not any(path.exists() or path.is_symlink() for path in (final, checksum, sidecar)),
            'Refusing to overwrite a live-image output')
    digest = sha(partial)
    uid, gid = owner
    os.chmod(partial, 0o644)
    os.chown(partial, uid, gid)
    temporaries = []
    published = []
    try:
        for suffix, writer in (
                ('.sha256.tmp', lambda path: path.write_text(
                    f'{digest}  {final.name}\n', encoding='ascii')),
                ('.buildinfo.json.tmp', lambda path: shutil.copyfile(buildinfo_source, path))):
            fd, name = tempfile.mkstemp(prefix='.' + final.name + '.', suffix=suffix,
                                        dir=final.parent)
            os.close(fd)
            temporary = Path(name)
            temporaries.append(temporary)
            writer(temporary)
            os.chmod(temporary, 0o644)
            os.chown(temporary, uid, gid)
        os.link(partial, final)
        published.append(final)
        os.link(temporaries[0], checksum)
        published.append(checksum)
        os.link(temporaries[1], sidecar)
        published.append(sidecar)
        partial.unlink()
    except Exception:
        for path in reversed(published):
            path.unlink(missing_ok=True)
        raise
    finally:
        for path in temporaries:
            path.unlink(missing_ok=True)
    return digest


def parse_build_metadata(path):
    metadata = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        # build-metadata.txt also records compiler diagnostics; only its
        # machine-readable key=value rows participate in pin checks.
        if not re.fullmatch(r'[a-z][a-z0-9_]*', key):
            continue
        if key in metadata:
            raise ValueError('Kernel build metadata has a repeated key')
        metadata[key] = value
    return metadata


def validate_build_metadata(metadata, pin):
    expected = {
        'source_sha256': pin['source_archive_sha256'],
        'source_tree_sha256': pin['source_tree_sha256'],
        'config_sha256': pin['resolved_config_sha256'],
        'policy_fragment_sha256': pin['policy_fragment_sha256'],
        'kconfig_resolved_config_sha256': pin['resolved_config_sha256'],
    }
    for field, value in expected.items():
        require(metadata.get(field) == value,
                'Kernel build metadata differs from pin: ' + field)
    require(metadata.get('cpu_target', '').startswith('arm64;'),
            'Kernel build metadata is not for the SP12 ARM64 target')
    return metadata


def validate_kernel_inputs(package_dir, package_verification, build_metadata,
                           module_signing_certificate, kernel_pin_path=KERNEL_PIN):
    pin = ISO_MODULE.validate_pin_pair(load_json(kernel_pin_path))
    package_dir = Path(package_dir)
    expected_packages = {item['filename']: item for item in pin['packages']}
    actual_packages = {path.name for path in package_dir.glob('*.deb')}
    require(actual_packages == set(expected_packages),
            'Kernel package directory must contain exactly the pinned image and headers pair')
    for filename, item in expected_packages.items():
        require(sha(package_dir / filename) == item['sha256'],
                'Kernel package hash differs from pin: ' + filename)
    certificate = Path(module_signing_certificate)
    require(certificate.is_file() and not certificate.is_symlink(),
            'Module signing certificate must be a regular file')
    require(sha(certificate) == pin['module_signing_certificate_sha256'],
            'Module signing certificate differs from the kernel pin')
    report = verify_arm64_packages(
        package_dir,
        expected_release=pin['kernel_release'],
        expected_dtb=pin['dtb_path'],
        expected_version=pin['debian_version'],
        expected_dtb_build_id=pin.get('dtb_build_id'),
    )
    recorded_report = load_json(package_verification)
    require(recorded_report == report,
            'Package verification manifest does not match the supplied package pair')
    metadata = validate_build_metadata(parse_build_metadata(build_metadata), pin)
    return pin, report, metadata


def verify_kernel_tree(package_root, pin, package_report):
    release = pin['kernel_release']
    kernel_image = Path(package_root) / 'boot' / ('vmlinuz-' + release)
    require(kernel_image.is_file() and not kernel_image.is_symlink(),
            'Pinned kernel package is missing its regular kernel image')
    require(sha(kernel_image) == pin['kernel_payload_sha256'],
            'Kernel image payload differs from the pinned kernel payload hash')
    dtb_relative = Path('usr/lib/linux-image-' + release) / pin['dtb_path']
    dtb = Path(package_root) / dtb_relative
    if not dtb.is_file():
        dtb = Path(package_root) / 'boot' / ('dtbs-' + release) / pin['dtb_path']
        dtb_relative = Path('boot') / ('dtbs-' + release) / pin['dtb_path']
    require(dtb.is_file() and not dtb.is_symlink() and sha(dtb) == pin['dtb_sha256'],
            'SP12 DTB is missing or differs from the pinned DTB hash')
    modules = Path(package_root) / 'lib/modules' / release
    if not modules.is_dir():
        modules = Path(package_root) / 'usr/lib/modules' / release
    require(modules.is_dir(), 'Pinned kernel package is missing its matching module tree')
    require(package_report['dtb']['sha256'] == pin['dtb_sha256'],
            'Package verification manifest DTB differs from pin')
    return kernel_image, dtb, modules


def validate_private_support(support_source, machine_root, support_pin=None):
    support_pin = support_pin or load_support_pin()
    support = Path(support_source).resolve(strict=True)
    root = Path(machine_root).resolve(strict=True)
    require(output('git', '-C', support, 'rev-parse', 'HEAD').strip() ==
            support_pin['support_source_commit'],
            'Unexpected SP12 private support checkout revision')
    checked = {}
    for relative, expected in support_pin['machine_files'].items():
        candidate = root / relative
        resolved = candidate.resolve(strict=True)
        require(resolved.is_relative_to(root), 'Private support file escapes machine root: ' + relative)
        require(candidate.is_file() and not candidate.is_symlink(),
                'Private support file is not a regular file: ' + relative)
        require(sha(candidate) == expected, 'Private support file differs from pin: ' + relative)
        checked[relative] = expected
    return support_pin, checked


def resolve_support_inputs(enabled, support_source, machine_root):
    if not enabled:
        return None, {}
    return validate_private_support(support_source, machine_root)


def preflight_tools(xorriso, private_support):
    required = {
        'gpgv', 'dpkg-deb', 'mount', 'umount', 'md5sum', 'depmod',
        'chroot', 'unmkinitramfs', 'lsinitramfs', 'modinfo', 'modprobe',
        'mksquashfs', 'unsquashfs', 'sgdisk', 'grub-file', 'efibootmgr',
        'findmnt',
    }
    if private_support:
        required.add('git')
    missing = sorted(tool for tool in required if shutil.which(tool) is None)
    if shutil.which(str(xorriso)) is None:
        missing.append(str(xorriso))
    require(not missing, 'Missing required build tools: ' + ', '.join(sorted(set(missing))))


def build(args):
    preflight_tools(args.xorriso, args.private_machine_support)
    original = args.iso.resolve(strict=True)
    requested_final = args.output.absolute()
    require(not requested_final.exists() and not requested_final.is_symlink(),
            'Refusing to overwrite output')
    final = requested_final.parent.resolve(strict=True) / requested_final.name
    require(final.suffix.lower() == '.iso', 'Output path must end in .iso')
    require(final.parent.is_dir(), 'Output directory must exist')
    base_pin = ISO_MODULE.verify_base_iso(
        original, args.checksums, args.signature, args.keyring, BASE_PIN)
    package_dir = args.kernel_packages.resolve(strict=True)
    package_verification = args.package_verification.resolve(strict=True)
    build_metadata_path = args.build_metadata.resolve(strict=True)
    module_signing_certificate = args.module_signing_certificate.resolve(strict=True)
    kernel_pin, package_report, metadata = validate_kernel_inputs(
        package_dir, package_verification, build_metadata_path,
        module_signing_certificate, args.kernel_pin)
    support_pin, checked_support = resolve_support_inputs(
        args.private_machine_support, args.support_source, args.machine_root)

    installer_iso = None
    installer_info = None
    installer_size = None
    if args.installer_iso is None:
        require(args.installer_iso_sha256 is None,
                '--installer-iso-sha256 requires --installer-iso')
    else:
        require(args.installer_iso_sha256 is not None,
                '--installer-iso requires --installer-iso-sha256')
        require(args.private_machine_support,
                '--installer-iso requires --private-machine-support')
        require(args.installer_iso.is_file() and not args.installer_iso.is_symlink(),
                'Installer ISO must be a regular non-symlink file')
        installer_iso = args.installer_iso.resolve(strict=True)
        installer_size = installer_iso.stat().st_size
        if args.apply:
            require(shutil.disk_usage(final.parent).free > 24 * 1024**3 + installer_size,
                    'Need the 24 GiB builder reserve plus the installer ISO snapshot space')
        with private_installer_snapshot(
                installer_iso, args.installer_iso_sha256,
                parent=final.parent if args.apply else None,
                expected_size=installer_size) as (snapshot_iso, snapshot_digest):
            with tempfile.TemporaryDirectory(prefix='sp12-installer-verify.') as temporary:
                installer_root, installer_config = extract_installer_validation_files(
                    snapshot_iso, temporary, args.xorriso, kernel_pin)
                installer_info = validate_installer_payload(
                    installer_root, installer_config, kernel_pin, snapshot_digest)

    release = kernel_pin['kernel_release']
    if not args.apply:
        print('DRY RUN: signed Ubuntu 26.10 ARM64 base:', base_pin['sha256'])
        print('Pinned SP12 kernel release:', release)
        print('Pinned kernel package pair verified:', package_report['image_package']['sha256'])
        print('Private machine support:', args.private_machine_support)
        if installer_info:
            print('Guarded installer ISO verified:', installer_info['iso_sha256'])
            print('Installer kernel release:', installer_info['kernel_release'])
        print('Base ISO:', original)
        print('Output:', final)
        print('No mounts or output files created. Add --apply to build.')
        return

    require(os.geteuid() == 0 and os.uname().machine == 'aarch64',
            'Native ARM64 root required')
    require(Path('/proc/self/ns/mnt').readlink() != Path('/proc/1/ns/mnt').readlink(),
            'Private mount namespace required')
    require(Path('/proc/self/ns/net').readlink() != Path('/proc/1/ns/net').readlink(),
            'Private network namespace required')
    partial = final.with_suffix('.iso.partial')
    sidecar = Path(str(final) + '.buildinfo.json')
    for path in [partial, Path(str(final) + '.sha256'), sidecar]:
        require(not path.exists() and not path.is_symlink(), 'Refusing to overwrite ' + str(path))
    scratch_reserve = 24 * 1024**3
    if installer_iso:
        scratch_reserve += installer_size
    require(shutil.disk_usage(final.parent).free > scratch_reserve,
            'Need the 24 GiB builder reserve plus the installer ISO snapshot space')

    before = snapshot()
    work = Path(tempfile.mkdtemp(prefix='sp12-live-build.', dir=final.parent))
    mounts = []
    validated = False

    def mount(destination, *mount_args):
        destination.mkdir(parents=True, exist_ok=True)
        run('mount', *mount_args, destination)
        mounts.append(destination)

    try:
        print('Scratch directory:', work, flush=True)
        xorriso = args.xorriso
        tree = work / 'original'
        with (work / 'extract.log').open('w') as log:
            run(xorriso, '-osirrox', 'on', '-indev', original, '-extract', '/', tree,
                stdout=log, stderr=subprocess.STDOUT)
        run('md5sum', '--quiet', '-c', 'md5sum.txt', cwd=tree)
        fdt_module = tree / 'boot/grub/arm64-efi/fdt.mod'
        require(fdt_module.is_file() and not fdt_module.is_symlink(),
                'Base ISO GRUB FDT module is missing')
        require(not (tree / 'casper' / LAYER).exists(),
                'Base ISO already contains the SP12 live layer')
        require(not (tree / 'casper/qemu-vmlinuz').exists()
                and not (tree / 'casper/qemu-initrd').exists(),
                'Base ISO already contains generic QEMU diagnostic payload names')
        if installer_iso:
            require(not (tree / 'autoinstall.yaml').exists()
                    and not (tree / 'psycachy').exists(),
                    'Base ISO already contains guarded installer payload paths')

        image_item = next(item for item in kernel_pin['packages']
                          if item['name'].startswith('linux-image-'))
        image_package = package_dir / image_item['filename']
        kernel = work / 'kernel-package'
        run('dpkg-deb', '-x', image_package, kernel)
        kernel_image, package_dtb, package_modules = verify_kernel_tree(
            kernel, kernel_pin, package_report)

        stage = work / 'stage'
        (stage / 'usr/lib/modules').mkdir(parents=True)
        (stage / 'lib').symlink_to('usr/lib')
        stage_boot = stage / 'boot'
        stage_boot.mkdir()
        shutil.copy2(kernel_image, stage_boot / kernel_image.name)
        module_destination = stage / 'usr/lib/modules' / release
        shutil.copytree(package_modules, module_destination, symlinks=True)
        dtb_destination = (stage / 'usr/lib' / ('linux-image-' + release)
                           / kernel_pin['dtb_path'])
        dtb_destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package_dtb, dtb_destination)
        require(sha(stage_boot / kernel_image.name) == kernel_pin['kernel_payload_sha256'],
                'Staged kernel image differs from pin')
        require(sha(dtb_destination) == kernel_pin['dtb_sha256'],
                'Staged SP12 DTB differs from pin')

        target_support = dict(checked_support)
        if args.private_machine_support:
            # The source archive and four machine files are a narrow, local-only allowlist.
            support = args.support_source.resolve(strict=True)
            archive = work / 'private-platform.tar'
            for relative in support_pin['source_allowlist']:
                run('git', '-C', support, 'cat-file', '-e',
                    support_pin['support_source_commit'] + ':' + relative)
            archive_paths = support_pin['source_allowlist']
            run('git', '-C', support, 'archive', '--format=tar',
                '--output=' + str(archive), support_pin['support_source_commit'], *archive_paths)
            extracted = work / 'private-platform'
            with tarfile.open(archive) as bundle:
                bundle.extractall(extracted, filter='data')
            source_support = collect_source_support(extracted, support_pin)
            for target_relative, expected in source_support.items():
                source_relative = (target_relative[8:] if target_relative.startswith('usr/lib/')
                                   else target_relative)
                if target_relative.startswith('usr/lib/'):
                    source_relative = 'lib/' + source_relative
                source = extracted / source_relative
                require(sha(source) == expected,
                        'Pinned source support file changed during extraction: ' + source_relative)
                require(target_relative not in target_support
                        or target_support[target_relative] == expected,
                        'Pinned source support collides with a machine file: ' + target_relative)
                target_support[target_relative] = expected
            for relative in support_pin['source_allowlist']:
                source = extracted / relative
                destination = stage / relative
                if relative.startswith('lib/'):
                    destination = stage / 'usr' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, destination, dirs_exist_ok=True, symlinks=False)
            for relative, expected in checked_support.items():
                source = Path(args.machine_root).resolve(strict=True) / relative
                destination = stage / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                destination.chmod(0o644)
                require(sha(destination) == expected,
                        'Copied private support file differs from pin: ' + relative)

        installer_payload = None
        installer_config = None
        if installer_iso:
            payload_root = work / 'installer-payload'
            require(shutil.disk_usage(final.parent).free >
                    24 * 1024**3 + installer_size,
                    'Need the 24 GiB builder reserve plus the installer ISO snapshot space')
            with private_installer_snapshot(
                    installer_iso, args.installer_iso_sha256, parent=work,
                    expected_size=installer_size) as (
                        snapshot_iso, snapshot_digest):
                require(snapshot_digest == installer_info['iso_sha256'],
                        'Installer ISO changed after preflight')
                installer_payload, installer_config = extract_installer_payload(
                    snapshot_iso, payload_root, args.xorriso)
                verified_installer = validate_installer_payload(
                    installer_payload, installer_config, kernel_pin, snapshot_digest)
                require(verified_installer == installer_info,
                        'Installer payload changed between preflight and extraction')
            for relative, expected in target_support.items():
                if relative in checked_support:
                    source = Path(args.machine_root).resolve(strict=True) / relative
                else:
                    source_relative = ('lib/' + relative[8:]
                                       if relative.startswith('usr/lib/') else relative)
                    source = extracted / source_relative
                destination = installer_payload / 'private-support' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                destination.chmod(0o644)
                require(sha(destination) == expected,
                        'Installer target support payload differs from pin: ' + relative)
            manifest_path = installer_payload / 'private-support' / 'SHA256SUMS'
            manifest_path.write_text(private_support_manifest(target_support), encoding='utf-8')
            manifest_path.chmod(0o644)
            support_installer = installer_payload / 'install-private-support.sh'
            support_installer.write_text(
                private_support_install_script(target_support), encoding='utf-8')
            support_installer.chmod(0o755)
            installer_config.write_text(
                installer_autoinstall_config(installer_config.read_text(encoding='utf-8')),
                encoding='utf-8')
        run('depmod', '-b', stage, release)

        layers = []
        for name in ['minimal', 'minimal.standard', 'minimal.standard.live']:
            layer = work / name
            mount(layer, '-t', 'squashfs', '-o', 'loop,ro,nodev,nosuid',
                  tree / ('casper/' + name + '.squashfs'))
            layers.append(layer)
        root = work / 'root'
        upper, overlay_work = work / 'upper', work / 'overlay-work'
        upper.mkdir()
        overlay_work.mkdir()
        lower = ':'.join(str(path) for path in [stage] + list(reversed(layers)))
        mount(root, '-t', 'overlay', '-o',
              f'lowerdir={lower},upperdir={upper},workdir={overlay_work}', 'overlay')
        require('VERSION_ID="26.10"' in (root / 'etc/os-release').read_text(),
                'Wrong live root version')

        # The chroot receives no physical block devices; sysfs is read-only.
        mount(root / 'dev', '-t', 'tmpfs', '-o', 'nosuid,mode=755', 'tmpfs')
        for name in ['null', 'zero', 'random', 'urandom']:
            (root / 'dev' / name).touch()
            run('mount', '--bind', '/dev/' + name, root / 'dev' / name)
            mounts.append(root / 'dev' / name)
        mount(root / 'proc', '-t', 'proc', '-o', 'nosuid,nodev,noexec', 'proc')
        mount(root / 'sys', '--bind', '/sys')
        run('mount', '-o', 'remount,bind,ro,nosuid,nodev,noexec', root / 'sys')
        generated = work / 'generated'
        generated.mkdir()
        mount(root / 'tmp/sp12-live-build', '--bind', generated)

        (root / 'etc/initramfs-tools/conf.d/sp12-live').write_text(
            'MODULES=most\nCOMPRESS=zstd\nBOOT=casper\n')
        with (root / 'etc/initramfs-tools/modules').open('a') as stream:
            stream.write('\n# SP12 live boot and hardware dependencies\n' + '\n'.join(MODULES) + '\n')
        old_initrd = work / 'original-initrd'
        run('unmkinitramfs', tree / 'casper/initrd', old_initrd)
        old_uuid_files = list(old_initrd.rglob('conf/uuid.conf'))
        require(len(old_uuid_files) == 1, 'Expected one casper media UUID')
        media_uuid = old_uuid_files[0].read_text().strip()
        require(re.fullmatch(r'[0-9a-f-]{36}', media_uuid) is not None,
                'Unexpected original casper UUID')
        hook = root / 'etc/initramfs-tools/hooks/zzzz-sp12-live'
        hook.write_text('#!/bin/sh\nset -eu\n'
                        'if [ "${1:-}" = prereqs ]; then exit 0; fi\n'
                        'mkdir -p "$DESTDIR/conf/conf.d"\n'
                        f"printf '%s\\n' '{media_uuid}' > \"$DESTDIR/conf/uuid.conf\"\n"
                        f"printf '%s\\n' 'LAYERFS_PATH={LAYER}' > \"$DESTDIR/conf/conf.d/default-layer.conf\"\n"
                        "printf '%s\\n' 'BOOT=casper' > \"$DESTDIR/conf/conf.d/default-boot-to-casper.conf\"\n")
        hook.chmod(0o755)
        print('Generating casper initramfs with the pinned SP12 modules...', flush=True)
        with (work / 'mkinitramfs.log').open('w') as log:
            run('chroot', root, '/usr/sbin/mkinitramfs', '-o',
                '/tmp/sp12-live-build/initrd', release, stdout=log,
                stderr=subprocess.STDOUT,
                env={**os.environ, 'LC_ALL': 'C', 'SYSTEMD_OFFLINE': '1'})

        listing = output('lsinitramfs', generated / 'initrd')
        initrd_names = {name.removeprefix('./').removeprefix('usr/').rstrip('/')
                        for name in listing.splitlines()}
        initrd_releases = {name.split('/')[2] for name in initrd_names
                           if name.startswith('lib/modules/') and len(name.split('/')) > 2}
        require(initrd_releases == {release},
                'Wrong initramfs module release set: ' + str(initrd_releases))
        require('scripts/casper' in initrd_names and
                'scripts/casper-bottom/25adduser' in initrd_names,
                'Missing casper live-session scripts')
        for module in MODULES:
            vermagic = output('modinfo', '-b', stage, '-k', release,
                              '-F', 'vermagic', module).split()[0]
            require(vermagic == release, 'Wrong module vermagic: ' + module)
            dependencies = output('modprobe', '-d', stage, '-S', release,
                                  '--show-depends', module)
            for line in dependencies.splitlines():
                if line.startswith('insmod '):
                    path = Path(line.split()[1])
                    relative = (str(path.relative_to(stage)) if path.is_relative_to(stage)
                                else str(path).lstrip('/'))
                    require(relative.removeprefix('usr/') in initrd_names,
                            'Missing initramfs dependency: ' + relative)

        initrd_tree = work / 'new-initrd'
        run('unmkinitramfs', generated / 'initrd', initrd_tree)
        uuid_files = list(initrd_tree.rglob('conf/uuid.conf'))
        require(len(uuid_files) == 1 and uuid_files[0].read_text().strip() == media_uuid,
                'Casper UUID mismatch')
        layer_configs = list(initrd_tree.rglob('conf/conf.d/default-layer.conf'))
        require(len(layer_configs) == 1 and LAYER in layer_configs[0].read_text(),
                'Wrong initramfs default layer')

        overlay = generated / LAYER
        run('mksquashfs', stage, overlay, '-noappend', '-comp', 'zstd',
            '-processors', '4', '-no-progress')
        overlay_manifest = {
            str(path.relative_to(stage)): sha(path)
            for path in sorted(stage.rglob('*')) if path.is_file() and not path.is_symlink()
        }
        (generated / 'sp12-live-overlay-manifest.json').write_text(
            json.dumps(overlay_manifest, indent=2) + '\n')
        if installer_iso:
            shutil.copy2(tree / 'casper/vmlinuz', tree / 'casper/qemu-vmlinuz')
            shutil.copy2(tree / 'casper/initrd', tree / 'casper/qemu-initrd')
        grub_text = grub_config((tree / 'boot/grub/grub.cfg').read_text(),
                                args.private_machine_support,
                                installer_enabled=bool(installer_iso))
        (generated / 'grub.cfg').write_text(grub_text)
        info = {
            'schema_version': 1,
            'status': ('private-local-testing-only-do-not-publish' if args.private_machine_support
                       else 'experimental-live-no-private-machine-support'),
            'distribution': ('private-local-testing-only-do-not-publish'
                             if args.private_machine_support else 'experimental-test-only'),
            'base_iso_sha256': base_pin['sha256'],
            'base_pin_sha256': sha(BASE_PIN),
            'kernel_pin_sha256': sha(args.kernel_pin),
            'kernel_release': release,
            'kernel_payload_sha256': kernel_pin['kernel_payload_sha256'],
            'image_package_sha256': package_report['image_package']['sha256'],
            'headers_package_sha256': package_report['headers_package']['sha256'],
            'package_verification_sha256': sha(package_verification),
            'build_metadata_sha256': sha(build_metadata_path),
            'source_archive_sha256': metadata['source_sha256'],
            'source_tree_sha256': metadata['source_tree_sha256'],
            'resolved_config_sha256': metadata['config_sha256'],
            'policy_fragment_sha256': metadata['policy_fragment_sha256'],
            'module_signing_certificate_sha256': kernel_pin['module_signing_certificate_sha256'],
            'dtb_path': kernel_pin['dtb_path'],
            'dtb_sha256': kernel_pin['dtb_sha256'],
            'module_names': MODULES,
            'initrd_sha256': sha(generated / 'initrd'),
            'live_layer': LAYER,
            'live_layer_sha256': sha(overlay),
            'live_layer_manifest_sha256': sha(generated / 'sp12-live-overlay-manifest.json'),
            'grub_fdt_module_sha256': sha(fdt_module),
            'live_grub_sha256': sha(generated / 'grub.cfg'),
            'private_machine_support': bool(args.private_machine_support),
            'private_support_source_commit': (support_pin['support_source_commit']
                                              if support_pin else None),
            'private_support_sources': (support_pin['support_sources'] if support_pin else None),
            'private_support_file_hashes': checked_support,
            'installer_iso_sha256': (installer_info['iso_sha256'] if installer_info else None),
            'installer_kernel_pin_sha256': (installer_info['kernel_pin_sha256']
                                            if installer_info else None),
            'installer_kernel_release': (installer_info['kernel_release']
                                         if installer_info else None),
            'installer_package_hashes': (installer_info['package_hashes']
                                         if installer_info else None),
            'installer_autoinstall_sha256': (sha(installer_config)
                                            if installer_config else None),
            'target_support_manifest_sha256': (
                hashlib.sha256(private_support_manifest(target_support).encode()).hexdigest()
                if installer_iso else None),
            'script_sha256': sha(__file__),
        }
        (generated / 'sp12-live-buildinfo.json').write_text(
            json.dumps(info, indent=2) + '\n')

        replacements = {
            'casper/vmlinuz': stage_boot / kernel_image.name,
            'casper/initrd': generated / 'initrd',
            'casper/x1p42100-microsoft-sp12in.dtb': dtb_destination,
            'casper/' + LAYER: overlay,
            'boot/grub/grub.cfg': generated / 'grub.cfg',
            'sp12-live-buildinfo.json': generated / 'sp12-live-buildinfo.json',
            'sp12-live-overlay-manifest.json': generated / 'sp12-live-overlay-manifest.json',
            'sp12-live-build-script.py': Path(__file__),
        }
        if installer_iso:
            replacements['casper/qemu-vmlinuz'] = tree / 'casper/qemu-vmlinuz'
            replacements['casper/qemu-initrd'] = tree / 'casper/qemu-initrd'
            replacements['autoinstall.yaml'] = installer_config
            for path in sorted(installer_payload.rglob('*')):
                if path.is_symlink():
                    require(False, 'Installer payload contains an unexpected symlink: ' +
                            str(path.relative_to(installer_payload)))
                if path.is_file():
                    relative = Path('psycachy') / path.relative_to(installer_payload)
                    replacements[str(relative)] = path
        md5_rows = []
        for line in (tree / 'md5sum.txt').read_text().splitlines():
            match = re.fullmatch(r'([0-9a-fA-F]{32})  (.+)', line)
            require(match is not None, 'Base md5sum.txt contains a malformed row')
            relative = match.group(2).removeprefix('*').removeprefix('./')
            if relative not in replacements:
                md5_rows.append(line)
        for name, path in replacements.items():
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'md5').hexdigest()
            md5_rows.append(f'{digest}  ./{name}')
        (generated / 'md5sum.txt').write_text('\n'.join(md5_rows) + '\n')
        replacements['md5sum.txt'] = generated / 'md5sum.txt'

        xorriso_args = [xorriso, '-indev', original, '-outdev', partial,
                        '-boot_image', 'any', 'replay']
        for name, path in replacements.items():
            xorriso_args.extend(['-update', path, '/' + name])
        xorriso_args.extend(['-padding', '0', '-commit'])
        with (work / 'xorriso.log').open('w') as log:
            run(*xorriso_args, stdout=log, stderr=subprocess.STDOUT)
        layout = subprocess.check_output(
            [str(xorriso), '-indev', str(partial), '-report_system_area', 'plain'],
            stderr=subprocess.STDOUT, text=True)
        sectors = re.search(r'^ISO image size/512\s*:\s*(\d+)', layout, re.M)
        require(sectors is not None, 'Cannot determine hybrid ISO size')
        os.truncate(partial, int(sectors[1]) * 512)
        run('sgdisk', '-v', partial)
        require(esp_digest(partial) == esp_digest(original), 'ISO EFI partition changed')

        audit = work / 'audit'
        with (work / 'audit-extract.log').open('w') as log:
            run(xorriso, '-osirrox', 'on', '-indev', partial, '-extract', '/', audit,
                stdout=log, stderr=subprocess.STDOUT)
        run('md5sum', '--quiet', '-c', 'md5sum.txt', cwd=audit)
        audit_grub = (audit / 'boot/grub/grub.cfg').read_text()
        require(audit_grub == grub_text
                and audit_grub.count('insmod fdt') == (2 if installer_iso else 1)
                and audit_grub.count('devicetree ' + LIVE_DTB) ==
                (2 if installer_iso else 1),
                'Audited live GRUB config enables autoinstall or differs from the generated config')
        try_menu = re.search(r'(?ms)menuentry "Try SP12 Ubuntu 26\.10[^\"]*"\s*\{([^}]*)\}',
                             audit_grub)
        require(try_menu is not None and 'autoinstall' not in try_menu.group(1),
                'Default SP12 Try entry must not enable autoinstall')
        if installer_iso:
            install_menu = re.search(
                r'(?ms)menuentry "Install SP12 \(guarded\)"\s*\{([^}]*)\}', audit_grub)
            generic_menu = re.search(
                r'(?ms)menuentry "Install SP12 \(generic QEMU diagnostic\)"\s*\{([^}]*)\}',
                audit_grub)
            require(install_menu is not None and install_menu.group(1).count('autoinstall') == 1
                    and install_menu.group(1).count('devicetree ' + LIVE_DTB) == 1,
                    'Guarded installer entry does not select the pinned kernel and DTB')
            require(generic_menu is not None
                    and generic_menu.group(1).count('autoinstall') == 1
                    and 'devicetree' not in generic_menu.group(1)
                    and '/casper/qemu-vmlinuz' in generic_menu.group(1)
                    and '/casper/qemu-initrd' in generic_menu.group(1),
                    'Generic QEMU installer diagnostic must use the guarded payload without Surface DTB')
            require((audit / 'autoinstall.yaml').read_bytes() == installer_config.read_bytes(),
                    'Guarded autoinstall selector/late-install config changed in the final ISO')
        audit_fdt_module = audit / 'boot/grub/arm64-efi/fdt.mod'
        require(audit_fdt_module.is_file() and not audit_fdt_module.is_symlink()
                and sha(audit_fdt_module) == sha(fdt_module),
                'GRUB FDT module is missing or changed in the final ISO')
        for image in audit.rglob('*'):
            if image.is_file() and image.suffix.lower() == '.efi':
                run('grub-file', '--is-arm64-efi', image)
        for name, path in replacements.items():
            require(sha(audit / name) == sha(path), 'ISO replacement mismatch: ' + name)
        for name in ['minimal.squashfs', 'minimal.standard.squashfs',
                     'minimal.standard.live.squashfs', 'install-sources.yaml']:
            require(sha(audit / 'casper' / name) == sha(tree / 'casper' / name),
                    'Base install layer changed: ' + name)
        for relative, expected in checked_support.items():
            data = subprocess.check_output(
                ['unsquashfs', '-cat', str(audit / 'casper' / LAYER), relative])
            require(hashlib.sha256(data).hexdigest() == expected,
                    'Private support payload differs in live layer: ' + relative)
            if installer_iso:
                target_support_file = audit / 'psycachy/private-support' / relative
                require(target_support_file.is_file() and not target_support_file.is_symlink()
                        and sha(target_support_file) == expected,
                        'Private target support payload differs in final ISO: ' + relative)
        if installer_iso:
            require(sha(audit / 'psycachy/install-private-support.sh') ==
                    sha(installer_payload / 'install-private-support.sh'),
                    'Private target support installer changed in final ISO')
            expected_manifest = private_support_manifest(target_support).encode()
            manifest = audit / 'psycachy/private-support/SHA256SUMS'
            require(manifest.is_file() and not manifest.is_symlink()
                    and manifest.read_bytes() == expected_manifest,
                    'Private target support manifest changed in final ISO')
            for relative, expected in target_support.items():
                target_support_file = audit / 'psycachy/private-support' / relative
                require(target_support_file.is_file() and not target_support_file.is_symlink()
                        and sha(target_support_file) == expected,
                        'Private target support file changed in final ISO: ' + relative)
        require(snapshot() == before, 'Physical ESP/NVRAM/mount state changed')

        sha(partial)
        validated = True
    finally:
        cleanup_mounts(mounts, before)
        print('Build evidence retained:', work, 'validated=' + str(validated), flush=True)

    digest = publish_outputs(
        partial, final, generated / 'sp12-live-buildinfo.json',
        (original.stat().st_uid, original.stat().st_gid))
    print('PASS: pinned base, package manifest, kernel/modules/DTB, initramfs and live layer',
          flush=True)
    print('PASS: non-autoinstall live GRUB entry and unchanged base install layers', flush=True)
    print('PASS: physical ESP, NVRAM and ESP mount state unchanged', flush=True)
    print('EXPERIMENTAL TEST IMAGE:', final, flush=True)
    print('SHA256:', digest, flush=True)
    print('Live Wi-Fi/audio and suspend remain unverified until physical boot.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', type=Path, required=True,
                        help='Canonical-signed Ubuntu 26.10 ARM64 Desktop base ISO')
    parser.add_argument('--checksums', type=Path, required=True, help='Canonical SHA256SUMS file')
    parser.add_argument('--signature', type=Path, required=True, help='Signature for SHA256SUMS')
    parser.add_argument('--keyring', type=Path, default=Path('/usr/share/keyrings/ubuntu-cdimage-keyring.gpg'))
    parser.add_argument('--kernel-packages', type=Path, required=True,
                        help='Directory containing exactly the pinned image and headers .debs')
    parser.add_argument('--package-verification', type=Path, required=True,
                        help='package-verification.json emitted by the pinned build')
    parser.add_argument('--build-metadata', type=Path, required=True,
                        help='build-metadata.txt emitted by the pinned build')
    parser.add_argument('--module-signing-certificate', type=Path, required=True,
                        help='Public module-signing X.509 certificate emitted by the pinned build')
    parser.add_argument('--kernel-pin', type=Path, default=KERNEL_PIN,
                        help='ARM64 kernel artifact pin; defaults to the active pin')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--xorriso', default='xorriso')
    parser.add_argument('--private-machine-support', action='store_true')
    parser.add_argument('--support-source', type=Path, default=Path('/opt/surface-pro-12-linux'))
    parser.add_argument('--machine-root', type=Path, default=Path('/'),
                        help='Root containing the four verified local support files')
    parser.add_argument('--installer-iso', type=Path,
                        help='Exact pinned SP12 installer ISO to embed for the guarded Install entry')
    parser.add_argument('--installer-iso-sha256',
                        help='Required exact lowercase SHA-256 for --installer-iso')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        build(args)
    except (OSError, ValueError, RuntimeError, KeyError,
            subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
