# AMD64 repeat-media failure reproduction — 2026-11-15

**Run time:** 2026-11-15 21:25 MST

**Candidate:** 8,052,277,248 bytes, SHA-256
`d463a31aaa0d2fbce293e38bed360f9d50770dceee344bed716bbc1d71d238fa`

**Scope:** disposable QEMU reproduction of the live-media failure after
removing `autoinstall` from the GRUB kernel command line.

**Disposition:** This is a historical reproduction on the `d463a31…` image.
The dialog was caused by the selector's intentional fail-closed cancellation
path, and this run recorded zero target and sentinel writes. It does not
qualify repeat-media behavior on the current `908f7df…` candidate or resolve
the write extent/package state of the separate earlier writable re-entry.

## Result

The exact generic installer image still loaded its guarded disk-selection
command after booting without the `autoinstall` kernel argument. The selector
showed only `/dev/vda` (`psycachy-linux`) with the erase checkbox clear.
Pressing Escape canceled the selector and reproduced the generic dialog:

> A command in the autoinstall file failed to run during installation.

The technical-details log identifies the failing command as
`python3 /cdrom/psycachy/select-disk.py`. Subiquity reports that it returned
non-zero exit status 1. In the helper, canceling or leaving the disk
unselected raises `ValueError("disk selection was cancelled or empty")`, so
the non-zero result is the intended fail-closed cancellation path. No disk
was selected, no `ERASE` confirmation was entered, and no installation began.

Removing the kernel argument alone does not hide an autoinstall configuration
that remains at the root of the installation medium. Canonical's Subiquity
documentation says that the installer checks the installation-medium root
for `autoinstall.yaml` and supports an explicit
`subiquity.autoinstallpath` kernel parameter. The exact image had the
configuration mapped to `/autoinstall.yaml`, so Subiquity loaded it and ran
its early command even though `/proc/cmdline` contained no `autoinstall`.
See [Providing autoinstall configuration](https://canonical-subiquity.readthedocs-hosted.com/en/latest/tutorial/providing-autoinstall.html).

The fix moves the configuration to `/psycachy/autoinstall.yaml`, outside
Subiquity's automatic root-of-media lookup. The explicit guarded-install entry
adds both `autoinstall` and
`subiquity.autoinstallpath=/cdrom/psycachy/autoinstall.yaml`; Try/Rescue entries
add neither. The existing cancellation remains fail-closed; the regression
asserts that cancellation never writes storage configuration or activation
authorization.

## Guarded-entry path probe and correction

The first rebuilt guarded-menu candidate had SHA-256
`36804ac081ef102f84e66dddbfdc99575532c18905a6b97216933de7f23eac83`.
Its default Try/Rescue entry passed the live-boot check below, but the explicit
Install entry did not reach the disk selector. The live `/proc/cmdline`
contained `autoinstall subiquity.autoinstallpath=cdrom/psycachy/autoinstall.yaml`
and `/cdrom/psycachy/autoinstall.yaml` existed. The Subiquity log nevertheless
recorded `load_autoinstall_config only_early True file None`; no
`select-disk.py` or `offline-install.sh` process started.

The live Subiquity server's working directory was
`/snap/ubuntu-desktop-bootstrap/701/bin`. The relative `cdrom/...` value was
therefore resolved from the snap directory and did not identify the ISO file.
The helper now passes the absolute path
`subiquity.autoinstallpath=/cdrom/psycachy/autoinstall.yaml`. Focused GRUB and
disk-selection tests and the full static suite pass with this correction. The
2026-11-16 candidate (SHA-256
`908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`) contains
the corrected menu and passed its exact-hash default Try/Rescue boot to the
live desktop. A guarded install and repeat-media run against that exact hash
remain open.

The failed-path probe used the disposable VM target only. QEMU block statistics
showed zero target and sentinel write bytes and operations; the sentinel stayed
read-only, both QCOW checks passed, and `tests/iso-vm.sh verify-other` passed.
Screenshots and the block-statistics record are in the adjacent
`artifacts/amd64-guarded-rescue-20261115/` directory.

## Reproduction and safety evidence

- QEMU 11.0.3/KVM, Microsoft-signed OVMF, 2 vCPU, 4 GiB RAM, and `-nic none`.
- The candidate ISO and protected sentinel were attached read-only. The
  writable VM target was a fresh QCOW overlay over the retained installed
  fixture; the fixture itself was not modified.
- The manual GRUB boot commands were `linux /casper/vmlinuz --- quiet splash`
  and `initrd /casper/initrd`. The live command line had no `autoinstall`.
- The installed root was mounted as `ro,relatime,norecovery`. Its
  `dpkg --audit` produced no findings. The candidate image and headers were
  both installed at `7.3.1-1psycachy1`.
- QEMU target block statistics after cancellation and the read-only package
  audit recorded `linuxdisk wr_bytes=0` and `wr_operations=0`. The sentinel
  also recorded zero write bytes/operations; the ISO and sentinel were
  read-only at the device layer.
- After shutdown, `qemu-img check` passed, `qemu-img compare` reported that
  the overlay and backing target were identical, and `tests/iso-vm.sh
  verify-other` passed both sentinel checks.
- Local free space was 176,988,332,032 bytes (about 164.9 GiB), above the
  80 GiB reserve.

## Evidence files

The adjacent `artifacts/amd64-repeat-media-repro-20261115/` directory holds
the selector screen, failure dialog, technical-details log, live command
line/disk view, package-audit view, QEMU block-device summary, and write
counters. Its `SHA256SUMS` sidecar binds these compact records.

The report does not claim that the earlier writable retry had no writes; its
extent remains unknown. This fresh reproduction establishes that the
cancelled selector path fails before it writes to the installed target.
