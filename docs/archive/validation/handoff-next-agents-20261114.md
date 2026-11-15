# Continuation handoff for agents — 2026-11-14

## Current stop point

The user asked to stop for tonight. They declined the proposed destructive
B550I external-install checkpoint with “hold off for now.” The Apple HDD is
unchanged. Do not reboot, select an install target, type `ERASE`, write media,
or begin an internal install until the user resumes and approves a fresh,
serial-bound supervised checkpoint.

The user authorized replacing both ISO files on the separate Ventoy USB. Both
destination files passed complete read-back SHA-256 checks. They later reported
booting the AMD64 ISO into the installer with a live generic kernel recalled
as `7.3.0-9-generic`; no exact uname output or selector screenshot was
retained. The live generic kernel is not the installed candidate kernel. The
pinned AMD64 kernel is already Zen 3 (`znver3`); do not change the target to
`amd64-v3`. A future build should fail closed if `-march=native` resolves to a
target different from the pin.

## Candidate and media identities

- AMD64 lifecycle ISO:
  `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso`,
  8,052,277,248 bytes, SHA-256
  `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`.
- SP12 final51 live ISO on `cs-sp12`:
  `/var/tmp/sp12-r2-final51-build/output/private-sp12-r2-final51.iso`,
  4,810,534,912 bytes, SHA-256
  `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47`.
- USB identity at staging: `/dev/disk/by-id/usb-General_UDisk-0:0`,
  reported serial `General_UDisk-0:0`, Ventoy UUID `4E21-0000`. The filesystem
  and partition table remain intact; post-metadata free space was
  2,828,926,976 bytes. The user-reported AMD64 boot does not qualify SP12 boot.
- Firmware `BootOrder` was restored to its pre-boot sequence `0000,0002,0004`.
  `Boot0005` for General UDisk remains stored outside `BootOrder`; Lexar rescue
  serial `AA8AGLJAH1RZABDT` remains protected.

## Hardware state and write boundaries

- B550I: MSI MPG B550I Gaming Edge WiFi (MS-7C92), Ryzen 7 5800X3D.
- Apple HDD: stable ID
  `/dev/disk/by-id/ata-APPLE_HDD_HTS545050A7E362_TNS519GY1G6JGG`, currently
  `/dev/sdc`, 465.8 GiB. It is unmounted and not in use. `lsblk` shows whole-
  device ISO9660 `Ubuntu 26.10 arm64`, ESP UUID `98A7-CC63`, and ext4 UUID
  `bb78f7c8-7c47-4bb4-89fe-e40432e0ca44` (461.3 GiB). The previous read-only
  inspection of that ext4 filesystem found only `lost+found`.
- The current raw ISO prefix was not rehashed because unprivileged block reads
  were denied; a privileged `fdisk -l` query was cancelled while waiting for
  local authentication. The prior 2026-11-12 direct-I/O read-back record
  identifies image SHA-256
  `e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36`, and
  the exact corrected source still exists on `cs-sp12` at
  `/var/tmp/sp12-live-output-20261112/sp12-ubuntu-26.10-arm64-live-private-fdt-fix.iso`.
  The same-size local ISO is a different pre-fix image (`dfd9c3e…`); do not
  substitute it. The exact pre-erase checkpoint and the user's hold are in the
  [USB write record](artifacts/usb-ventoy-inventory-20261114/write-record.md).
- Internal Seagate FireCuda Linux disk `7VP015DH`, Samsung BitLocker disk
  `S7KHNJ0WA06121F`, the Lexar BIOS-rescue USB, and internal system disks remain
  protected. Recovery for an external B550I attempt is to power off, remove
  the Apple HDD, and boot the original Ubuntu entry.
- No Apple HDD install, final51 HDD write, SP12 internal erase, or RPMB write
  occurred. The user has already backed up personal data; do not start a new
  personal-data backup project.

## Validation and blockers

- 7.3.4 archive authenticity passed, but ordered SP12 replay failed at patch
  46, `iris-context-bank-devices`, where the upstream Iris parent IOVA
  reservation conflicts with the downstream child-device design. Keep the
  authenticated 7.3.1/final51 candidate; do not build from the incomplete 7.3.4
  tree. See the [compatibility report](cachyos-7.3.4-compatibility-20261114.md).
- AMD64 pinned kernel package hashes are tied to Clang's effective `znver3`
  target on a Ryzen 7 5800X3D build host. The architecture migration is not
  needed; the reproducibility guard is open. See the
  [Zen 3 audit](amd64-zen3-target-audit-20261114.md).
- Focused regressions and `bash tests/static-check.sh` passed before the
  documentation-only updates. The local hash manifest checks out. `git diff
  --check` passes for source, tests, and current top-level docs; archived
  Markdown reports retain deliberate hard-break spaces, and raw console logs
  are kept local.
- The disposable AMD64 lifecycle VM gate remains open: `qemu-system-x86_64`
  is not installed, and local free space is 86,828,273,664 bytes, only about
  0.9 GiB above the 80 GiB reserve. Do not cross the reserve. The last SP12
  builder host had 18,877,718,528 bytes free at 2026-11-15 00:06 UTC, below its
  24 GiB minimum plus snapshot/output needs.
- The ARM64 changed-release VM attempt stopped at a login prompt because no
  authorized disposable credential or seed was available. No package
  transition ran. The SP12 final51 native live boot, external installation,
  device checks, and installed audio reconciliation remain open.

## Next-agent sequence

1. Recheck `docs/PRIVATE-PILOT-QUALIFICATION.md` and this handoff. Preserve
   the current dirty baseline; the original HEAD is
   `bb3fc379862271bcfdd8715564990f1073b7df83`, with its tracked and untracked
   snapshot under `.agents/wave-a/baseline-preservation/`.
2. Do not `git add .`. The public GitHub repository must not receive local
   private inputs, support blobs, signing keys, seeds, ISO/QCOW images, VM
   firmware state, screenshots, `.agents/`, `phase0-work/`,
   `sp121-reference/`, or the stray untracked `-`. The requested push is
   limited to reviewed source, tests, documentation, text reports, and ISO
   checksum sidecars; binary qualification evidence remains local.
3. When resources allow, install/enable `qemu-system-x86_64` and complete the
   AMD64 disposable first-install/replacement, trial, acknowledgement,
   promotion, timeout rollback, explicit rollback, Secure Boot, and fallback
   sequence while preserving the reserve. Re-run focused regressions and the
   static suite for any code change.
4. Obtain an explicitly authorized disposable ARM64 credential/seed and enough
   remote capacity before resuming the changed-release VM. Qualify the SP12
   final51 live ISO natively before treating the USB as independent SP12
   rescue media.
5. After the user resumes, reidentify the Apple HDD by stable ID, model,
   serial, capacity, contents, mount state, and active users. Present a fresh
   exact external-install checkpoint before any write. Qualify B550I first;
   archive its evidence before reusing the HDD for the SP12 external rehearsal.
   Keep the internal SP12 erase last, after every software/live/rescue gate and
   independent review passes.

## References

- [Current qualification ledger](../../PRIVATE-PILOT-QUALIFICATION.md)
- [Dated execution report](bounded-refresh-and-readiness-20261114.md)
- [USB write record](artifacts/usb-ventoy-inventory-20261114/write-record.md)
- [CachyOS 7.3.4 compatibility](cachyos-7.3.4-compatibility-20261114.md)
- [AMD64 Zen 3 target audit](amd64-zen3-target-audit-20261114.md)
