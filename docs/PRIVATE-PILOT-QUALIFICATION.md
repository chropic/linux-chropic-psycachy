# Private pilot qualification ledger

**As of:** 2026-11-15 03:16 UTC / 2026-11-14 20:16 MST
**Baseline:** `bb3fc379862271bcfdd8715564990f1073b7df83`
**Scope:** private B550I AMD64 and SP12 ARM64 pilots. This ledger is the current
source of truth for their gates. The [ship checklist](SHIP-CHECKLIST.md)
continues to track the repository's full public-release decision; performance
trials and redistribution clearance remain deferred for this private scope.

The latest bounded compatibility and readiness work is recorded in the
[2026-11-14 execution report](archive/validation/bounded-refresh-and-readiness-20261114.md).

Neither pilot is qualified for promotion or fresh internal installation. The
only physical write in this qualification pass was the user-authorized,
file-level replacement of two ISO files on the Ventoy USB, with full
destination read-back hashes recorded in the [USB write record](archive/validation/artifacts/usb-ventoy-inventory-20261114/write-record.md).
No installation-target, Apple HDD, or internal-disk write occurred. The earlier
guarded write of the distinct live USB image
`e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36` is
historical; its physical-session results do not qualify final51. No candidate
has passed all exact-hardware acceptance checks.

## Candidate identities

| Artifact | Exact identity | Current evidence boundary |
| --- | --- | --- |
| Earlier reconstructed AMD64 installer (historical) | `output/amd64-iso-reconstructed-20261113/psycachy-ubuntu-26.10-desktop-amd64.iso`, 8,052,146,176 bytes, SHA-256 `73610dc5848d48a9379177fce5af8bae43cd089a7f4223ec163fa6a96f55be9e` | Earlier checksum, signed Ubuntu base, pinned kernel package pair, local-only package closure, EFI/casper payload and UEFI record verification. It predates the integrated activation lifecycle. |
| AMD64 lifecycle pilot installer | `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso`, 8,052,277,248 bytes, SHA-256 `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c` | `SHA256SUMS` passes; signed Ubuntu base, exact pinned kernel pair, 280 Ubuntu package hashes, UEFI record, unchanged base EFI/casper kernel, and selected embedded lifecycle files/config/pinned packages were verified. The independent review found the original out-of-band manifest omitted the included helper hash; the [supplement](../output/amd64-iso-lifecycle-20261114-build2/manifest-supplement.txt) binds the extracted helper hash to this ISO, and `iso/build.sh` now includes it in future manifests. A bounded network-disabled UEFI/KVM boot reached the guarded disk selector, with only disposable serial `psycachy-linux` listed and left unselected. No installation, activation, acknowledgement, promotion, rollback, Secure Boot, or hardware qualification ran; see the [boot record](archive/validation/amd64-lifecycle-iso-liveboot-20261114.md). |
| SP12 final51 installer | **Generic QEMU kernel/rootfs boot reached serial login prompt; SP12 hardware boot open** | Signed base, embedded r2 pin/package pair, 120-package offline repository, retained Ubuntu live kernel/initrd, checksum and UEFI metadata verified. A 2026-11-14 detached COW follow-up confirmed that interactive, RAM-only GRUB commands can load the installed kernel/initrd/DTB; it did not record execution of the hidden zero-timeout default entry. The Surface-specific DTB fails against QEMU `virt` device addresses; omitting it let the same kernel/initrd reach the installed Ubuntu 26.10 serial login prompt under generic EFI/ACPI. No account login or authenticated session occurred; no network was used, and backing images and sentinel stayed unchanged. The follow-up demonstrates a QEMU platform mismatch but does not establish what happened in the original attempt-7 detached boot, whose vars file is missing. This is not physical SP12 qualification. See the [detached-boot diagnosis](archive/validation/artifacts/sp12-attempt7-detached-kernel-diagnostic-20261114/report.md). |
| SP12 private final51 live image | Built on `cs-sp12` under `/var/tmp`, 4,810,534,912 bytes, SHA-256 `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47` | Native build validation passed against the final51 pin and local-only support files. Its QEMU run reached the private GRUB entry but not a live OS. It was not written to the Apple HDD. |
| Earlier private SP12 live USB | 4,810,289,152 bytes, SHA-256 `e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36` | The retained guarded write and one-time physical live-session/audio observations belong to this earlier image. They do not qualify final51; its exact runtime DTB was also unverified. |
| Earlier local private live test | `output/.unattended-luna-20261111210910Z/qemu-hosting/sp12-live-build-20261112/sp12-ubuntu-26.10-arm64-live-private.iso`, SHA-256 `dfd9c3e081a002a8a9ad572750d4998da06255dd7a51cb223b5271f07b210523` | Historical pre-final51 image. Keep separate from both the earlier USB image and final51 live image. |
| Older installer generations | ARM64 v4 ISO SHA-256 `7669c1bcfeccffb9b86af2958ae5607cac9dc5b55b3fa77e467b304f7143af27`; final37 ISO SHA-256 `f990d6308f9342dd5208ebe18c4ce5e9cb876ca418048e887d4894982841c037` | Retained history/fallbacks only. Their tests do not transfer to final51. |

The hash-linked baseline reconciliation and file manifest are archived at
[baseline report](archive/validation/private-pilot-baseline-20261114.md) and
[manifest](archive/validation/private-pilot-baseline-20261114-manifest.txt).
Their SHA-256 values are `52122ef868d2e3acd2441bb588f649ed4502ad130933019551fbe05b6132d5a0`
and `f77e85dbca4b6764ebd52a563f75ec3499073a2fe0002e7043988fb85b57b74a`,
respectively.

## Gate status

| Gate | Status | Evidence and remaining condition |
| --- | --- | --- |
| AMD64 artifact identity | **Verified** | The lifecycle candidate checksum and `SHA256SUMS` match. The signed base, exact kernel package pair, authenticated Ubuntu package closure, UEFI/EFI checks, and selected embedded payload audit pass; see the [ISO build record](archive/validation/amd64-lifecycle-iso-build-20261114.md). |
| AMD64 CPU target | **Zen 3 (`znver3`) verified for the ISO-pinned candidate** | The saved package build metadata ties the ISO-pinned package hashes to Clang's effective `znver3` target on a Ryzen 7 5800X3D host, and the pin declares `cpu_target: znver3`. The build still uses `-march=native` without failing closed against that pin. The current running B550I kernel config hash differs from the ISO-pinned config; see the [CPU-target audit](archive/validation/amd64-zen3-target-audit-20261114.md). |
| AMD64 activation lifecycle | **Implementation integrated; candidate ISO built/reviewed; lifecycle qualification open** | The reviewed lifecycle routes the launcher through prepare, one-boot candidate trial, acknowledgement, explicit promotion, and rollback. First-install and replacement modes are bound to the selected disk serial; replacement revalidates the exact backup on a separately serial-identified disk. The fallback remains saved through acknowledgement. Main-workspace focused tests pass (38 helper, 8 selector, 1 late-installer); shell/Python syntax and static checks pass (71 recorded configuration changes; root-only `mokutil` check skipped). A bounded no-network UEFI/KVM smoke booted the ISO through the live desktop to the guarded disk selector, then stopped without choosing a disk or `ERASE`; target/sentinel QCOW checks passed. The [implementation record](archive/validation/amd64-activation-lifecycle-20261114.md), [ISO build record](archive/validation/amd64-lifecycle-iso-build-20261114.md), [boot record](archive/validation/amd64-lifecycle-iso-liveboot-20261114.md), and independent reviews retain details. The local health attestation is a root-controlled workflow record, not cryptographic proof of independent review. No install, activation, acknowledgement, promotion, or rollback was run. B550I Secure Boot, GPU/runtime, and physical gates remain open. |
| AMD64 Secure Boot and graphics | **Partially verified; candidate open** | B550I baseline: Secure Boot enabled, RTX 4070 detected on the existing generic kernel, lockdown `integrity`, and `module.sig_enforce=Y`. These are not exact-candidate results. Candidate NVIDIA signatures, runtime trust, graphics/video and suspend/resume remain unqualified. |
| ARM64 final51 installer | **Interactive GRUB kernel/initrd execution confirmed in reconstructed COW; exact SP12 boot unresolved** | Attempt 7 completed installer and powered off after media ejection. The untouched no-media COW run displayed GRUB, then remained visually inactive; its serial silence was inconclusive because the installed entry uses `console=tty0`. A reconstructed follow-up used interactive, RAM-only GRUB commands and PL011 diagnostics; it did not prove execution of the hidden zero-timeout default entry. With the Surface DTB, the kernel identified the Surface Pro 12 model and failed against QEMU `virt` GIC/timer resources. Omitting that DTB reached the installed root's serial login prompt under generic EFI/ACPI; no account login occurred. The result demonstrates a reproducible emulator/platform mismatch but does not prove the original detached attempt failed at the same point. Physical SP12 boot, runtime DTB identity, and hardware checks remain open. See the [detached-boot diagnosis](archive/validation/artifacts/sp12-attempt7-detached-kernel-diagnostic-20261114/report.md) and [attempt-7 GRUB report](archive/validation/sp12-attempt7-grub-config-read-20261114.md). |
| CachyOS 7.3.4 refresh | **Deferred; existing 7.3.1/final51 retained** | The authenticated 7.3.4 source replay applies 50 of 51 entries. Entry 46 (`iris-context-bank-devices`) fails against `iris_probe.c` and overlaps upstream parent-device IOVA reservation with the downstream context-bank child-device design. The two-hour compatibility budget was not exhausted, but this is substantial safety-sensitive driver work; no full build or partial migration was started. See the [compatibility report](archive/validation/cachyos-7.3.4-compatibility-20261114.md) and [ordered replay](archive/validation/cachyos-7.3.4-ordered-replay-20261114.md). |
| SP12 final51 live startup | **Not qualified** | The exact private image reached its GRUB entry under generic ARM64 TCG but did not reach a live OS. The older physical live USB hash is not a substitute. Native final51 SP12 boot and required device/function checks remain open. |
| ARM64 update lifecycle | **Open; changed-release attempt incomplete and independently reviewed** | The r2 reproducer attached the exact image and headers package pair to a fresh target COW, but stopped at `luna-arm64 login:` because no explicitly authorized guest credential or retained seed was available. No `dpkg` transition or hook ran, and clean guest shutdown was not confirmed; the COW passed `qemu-img check`, and retained backing/input hashes were unchanged. Independent review verified the 33-file output manifest and all pre/post input hashes. This attempt neither reproduces nor clears the update gap. See the [incomplete attempt report](archive/validation/artifacts/arm64-update-reproducer-20261114/report.md), [independent review](archive/validation/artifacts/arm64-update-reproducer-20261114/independent-review.md), and retained output manifest. An authorized disposable login/seed is required before repeating. |
| Restored-target boot | **Physical default boot passed within scope; generic-QEMU restored-root userspace control passed; automatic DTB/default boot open** | Retained physical records support restored default SP12 userspace with matching recovery payload hashes and a read-only ESP. A 2026-11-14 display-enabled COW run confirmed the disposable ESP loader reaches GRUB 2.14 and that its root's hidden default names kernel/initrd/DTB `7.3.0-10-generic`; a corrected-stub automatic probe remained serial-silent after UEFI BootNext and did not prove the default ran. A separate fresh-COW generic EFI/ACPI control manually loaded that kernel/initrd without a DTB, mounted the restored root, `/boot`, restored ESP (`C1D2-E253`), and `/mnt/sp12-data`, reached `getty.target` and `sp12-phase1-vm login:`, then shut down cleanly after QMP powerdown. No credentials were entered. All six COWs passed `qemu-img check`; retained source/backing/ESP/firmware/vars hashes passed. This proves generic QEMU restored-root userspace only; no in-guest `dpkg --audit` or payload comparison, automatic default-entry, Surface-DTB, or physical boot qualification was performed. See the [generic-control report](archive/validation/artifacts/sp12-restored-target-generic-control-20261114/report.md), prior [attempt report](archive/validation/artifacts/sp12-restored-target-cow-boot-20261114/boot-report.md) (SHA-256 `b6fd49ad455334173c0896dc50de60e3ecc6f48fa584de93fca21482ccb12208`), and [recovery reconciliation](archive/validation/sp12-recovery-reconciliation-20261114.md). |
| FAT/process interruption recovery | **Partial, simulation scope only** | Retained process-kill, mock flush, rotation, marker and payload-promotion cases support their named assertions. Historical sector EIO attempts missed the intended allocation/directory/data sectors and remain failed/inconclusive. Physical power-loss safety is unproven. |
| SP12 combined live/rescue/install ISO | **Built; native live startup and hardware qualification open** | The final51 image built on `cs-sp12` is 4,810,534,912 bytes with SHA-256 `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47`. Its QEMU run reached the private GRUB entry but not a live OS. Exact support checkout `ea0f07e66beea95898d96fbeb6daa472f4735af3` and four matching machine files are now preserved locally under `phase0-work/private-inputs/`. The remote `/` had 18,877,718,528 bytes free at the latest read-only check, below the 24 GiB minimum plus base-ISO snapshot/output needs; no new image was built. The earlier authorized Tailscale SSH identity check succeeded without a key bypass. |
| Ventoy USB media | **Both candidate ISOs staged and full read-back checksums verified; AMD64 installer boot user-reported** | On the user-approved USB (`General_UDisk-0:0`, Ventoy UUID `4E21-0000`), the AMD64 lifecycle ISO is 8,052,277,248 bytes with SHA-256 `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`; final51 SP12 is 4,810,534,912 bytes with SHA-256 `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47`. Each was hashed from the destination after writing. The user reported booting the AMD64 ISO to the installer with its generic live kernel (approximately `7.3.0-9-generic`); no exact uname log or selector-state record was retained. Ventoy remains intact with 2,828,926,976 bytes free. SP12 boot and independent rescue qualification remain open. UEFI BootOrder was restored to its captured original value. See the [write record](archive/validation/artifacts/usb-ventoy-inventory-20261114/write-record.md). |
| AMD64 one-time media boot | **Installer boot user-reported; exact live kernel and selector state not captured** | The user reported that the approved USB ISO reached the installer on the MSI MPG B550I Gaming Edge WiFi and showed a generic live kernel, recalled as `7.3.0-9-generic`. This does not verify the installed candidate kernel's `znver3` target. No disk selection, installation, or erase was authorized. Firmware BootOrder was restored to the original `0000,0002,0004` after an extra UDisk entry appeared; see the [USB write record](archive/validation/artifacts/usb-ventoy-inventory-20261114/write-record.md). |
| Physical B550I qualification | **Installer boot reported; external target reidentified; installation checkpoint held by user** | Apple HDD `TNS519GY1G6JGG` is attached at stable ID `/dev/disk/by-id/ata-APPLE_HDD_HTS545050A7E362_TNS519GY1G6JGG`, currently `/dev/sdc`, 465.8 GiB. It is unmounted and has an ISO9660 `Ubuntu 26.10 arm64` signature, a 6 MiB ESP, and a 461.3 GiB ext4 partition. User-reported installer boot confirms the AMD64 USB path only; no installed candidate boot or installation-target write is recorded. The raw ISO prefix was not rehashed during this pass, though the previous direct-I/O read-back record and exact remote source remain available. A serial-bound external-install checkpoint was presented; the user chose to hold for now. Do not write until the user resumes and approves a fresh supervised checkpoint. External install/boot, candidate Secure Boot, NVIDIA DKMS/runtime, update, fallback, and device checks remain open. |
| Physical SP12 qualification and fresh install | **Not started for final51** | The Apple HDD is attached as the user-authorized sequential target for B550I and later SP12 rehearsal; no final51 image was written to it. The approved Ventoy USB contains AMD64 lifecycle and final51 SP12 ISOs with matching full destination read-back hashes. The user-reported AMD64 boot does not prove SP12 image bootability, so independent SP12 rescue qualification remains open. No external installation or internal erase occurred. See the [USB inventory](archive/validation/artifacts/usb-ventoy-inventory-20261114/inventory.md) and [write record](archive/validation/artifacts/usb-ventoy-inventory-20261114/write-record.md). |
| RPMB and protected data | **Physical gate open** | Physical exact-candidate registration/health checks remain read-only. RPMB provisioning/data writes and firmware trust changes are outside scope. Samsung BitLocker storage, Lexar BIOS media, and the attached Switch SD remain protected. |
| Storage headroom | **Below target; local AMD64 VM and remote SP12 rebuild remain capacity-blocked** | At 2026-11-14 17:57 MST, local `/` and `/var/tmp` had 88,315,269,120 bytes free with the authenticated 7.3.4 scratch trees still present. This is 2,415,923,200 bytes above the 80 GiB reserve and 40,533,749,760 bytes below the 120 GiB target. A prior AMD64 installer target used 12,715,630,592 bytes; that allocation would cross the reserve. The SP12 remote had 18,877,718,528 bytes free at 00:06 UTC, below the native builder's 24 GiB minimum plus snapshot and output. Do not start heavy work that crosses the reserve. |
| Public-release requirements | **Deferred** | Paired performance trials and redistribution/attribution clearance are outside this private-pilot scope. This ledger is not a public ship approval. |

## Current dependencies and order

1. The exact AMD64 lifecycle ISO reached its guarded installer selector under
   network-disabled UEFI/KVM; no disk was chosen or erased. Run the disposable
   install/trial/acknowledgement/promotion/rollback sequence after measured
   storage can preserve the 80 GiB reserve. The previous install used
   12,715,630,592 bytes; current headroom cannot repeat that allocation while
   preserving the reserve. Then run exact-candidate B550I Secure Boot, NVIDIA,
   update, and fallback gates. QEMU results do not replace physical B550I
   qualification.
2. The ARM64 changed-release attempt remains incomplete. The user confirmed no
   authorized disposable login or retained seed is available, so repeating it
   depends on one being explicitly supplied. The first attempt and review are
   archived under `archive/validation/artifacts/arm64-update-reproducer-20261114/`.
3. The exact support checkout and four machine files are now preserved locally
   under `phase0-work/private-inputs/sp12-r2-live-support-recovery-20261113/`
   and match their pins. Stage them on `cs-sp12` after remote free space reaches
   at least the 24 GiB builder minimum plus the installer snapshot and output
   margin; current free space is 18,877,718,528 bytes. Then build, audit the
   complete output, and freeze its checksum.
4. Rebuild other affected candidates only when measured storage can preserve
   the 80 GiB reserve; freeze new checksums before requalification.
5. The Apple HDD was identified as `APPLE HDD HTS545050A7E362`, serial
   `TNS519GY1G6JGG`; its existing filesystem was checked read-only and
   unmounted. The user authorized its sequential use as the B550I external
   target and later SP12 rehearsal. The serial-bound external-install
   checkpoint was held at the user's request; leave it unchanged until they
   resume. It has reappeared at stable ID
   `/dev/disk/by-id/ata-APPLE_HDD_HTS545050A7E362_TNS519GY1G6JGG` (currently
   `/dev/sdc`) and is unmounted; use its model and serial at the installer
   checkpoint, not a stale kernel device name. Complete each physical write only at its
   supervised checkpoint. The separate Ventoy USB now holds the AMD64
   lifecycle and final51 SP12 ISOs, with read-back checksums verified. The
   AMD64 ISO has a user-reported installer boot; SP12 has not been
   boot-tested, so an independently bootable rescue path is not yet
   established. Use its supervised one-time firmware checkpoint before
   relying on it for rescue. Keep both systems' internal disks out of
   installation harnesses.

Keep private signing keys outside media and repository artifacts. Do not mark
either pilot complete until its exact candidate passes the required software,
recovery, hardware and restore gates.
