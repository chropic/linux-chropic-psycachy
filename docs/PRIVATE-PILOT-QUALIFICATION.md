# Private pilot qualification ledger

**As of:** 2026-11-16 MST (includes SP12 final51 live-boot diagnostics)
**Baseline:** `bb3fc379862271bcfdd8715564990f1073b7df83`
**Scope:** private B550I AMD64 and SP12 ARM64 pilots. This ledger is the current
source of truth for their gates. The [ship checklist](SHIP-CHECKLIST.md)
continues to track the repository's full public-release decision; performance
trials and redistribution clearance remain deferred for this private scope.

The latest bounded compatibility and readiness work is recorded in the
[2026-11-14 execution report](archive/validation/bounded-refresh-and-readiness-20261114.md).
The current supervised continuation is recorded in the
[2026-11-15 continuation report](archive/validation/supervised-continuation-20261115.md),
with its adjacent [SHA-256 sidecar](archive/validation/supervised-continuation-20261115.sha256).
The corrected AMD64 lifecycle ISO and independent audit are recorded in the
[2026-11-15 prompt-fix report](archive/validation/amd64-lifecycle-iso-promptfix-20261115.md).
The current per-install signing and guarded Try/Rescue candidate are recorded
in the [2026-11-16 AMD64 report](archive/validation/amd64-perinstall-guarded-rescue-20261116.md).
The targeted generated-artifact cleanup is recorded in the
[2026-11-15 storage cleanup report](archive/validation/storage-cleanup-20261115.md).
The current cleanup and its measured free-space result are recorded in the
[2026-11-16 storage cleanup report](archive/validation/storage-cleanup-20261116.md).
The hash-linked keep set and repeatable retention policy are in the
[current artifact keep list](archive/validation/current-artifact-keep-list-20261116.md)
and [artifact retention instructions](ARTIFACT-RETENTION.md).
The latest native SP12 build and independent content audit are recorded in the
[combined-image report](archive/validation/sp12-combined-build-20261115.md).
The separately approved Ventoy replacement and full read-back checks are in
the [media write report](archive/validation/sp12-combined-ventoy-write-20261115.md).
The user's 2026-11-16 first one-time firmware attempt did not list Ventoy;
the later successful live boot and its limits are recorded in the
[SP12 boot report](archive/validation/sp12-firmware-boot-attempt-20261116.md)
and [private-pilot handoff](archive/validation/private-pilot-handoff-20261116.md).

Neither pilot is qualified for promotion or fresh internal installation.
The current AMD64 candidate is 8,052,277,248 bytes with SHA-256
`908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`; its
sidecar and independent content review passed. Its default Try/Rescue entry
reached the live desktop in a network-disabled, diskless QEMU run, and the
prior autoinstall failure dialog did not appear. Exact-hash install to a
disposable target, detached generic-fallback boot, package audit, and a
read-only repeat-media run also completed. Secure Boot was enabled, but the
VM's per-install kernel and module certificates were not enrolled. The
installer left `7.3.0-10-generic` as the default pending activation, and the
pinned candidate was not attempted. The current hash's activation lifecycle,
physical B550I behavior, Ventoy staging, and hardware checks remain open. The
prior `per-install-pin` image's MOK and timeout observations do not transfer
to this candidate. See the
[2026-11-16 AMD64 report](archive/validation/amd64-perinstall-guarded-rescue-20261116.md)
and [handoff](archive/validation/private-pilot-handoff-20261116.md).

The combined SP12 and existing AMD64 Ventoy images passed full destination
read-back hashes; no AMD64 replacement has been written to Ventoy. After an
initial firmware-menu attempt did not list Ventoy, the user later booted the
SP12 combined image to a live session. The supplied diagnostics report the
expected r2 kernel and DTB build ID and show the live-media mounts. They do
not include an in-session ISO hash, device-function checks, or installation
evidence. No physical installation target, Apple HDD, or internal disk was
reported written. The
earlier guarded write of live USB image
`e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36` remains
historical and does not qualify final51. Neither pilot has passed all
exact-hardware acceptance checks.

## Candidate identities

| Artifact | Exact identity | Current evidence boundary |
| --- | --- | --- |
| Earlier reconstructed AMD64 installer (historical) | Binary retired 2026-11-15 after adjacent `SHA256SUMS` check; 8,052,146,176 bytes, SHA-256 `73610dc5848d48a9379177fce5af8bae43cd089a7f4223ec163fa6a96f55be9e` | Earlier checksum, signed Ubuntu base, pinned kernel package pair, local-only package closure, EFI/casper payload and UEFI record verification. Manifest and build log remain. It predates the integrated activation lifecycle. |
| AMD64 lifecycle pilot installer (pre-fix) | Local build copy retired 2026-11-15; SHA-256 `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`, 8,052,277,248 bytes | The exact full hash remains on the untouched Ventoy USB. Signed Ubuntu base, exact pinned kernel pair, 280 Ubuntu package hashes, UEFI record, unchanged base EFI/casper kernel, and selected embedded lifecycle files/config/pinned packages were previously verified. The independent review found the original out-of-band manifest omitted the included helper hash; the [supplement](../output/amd64-iso-lifecycle-20261114-build2/manifest-supplement.txt) binds the extracted helper hash to this ISO, and `iso/build.sh` now includes it in future manifests. A bounded network-disabled UEFI/KVM boot reached the guarded disk selector with only disposable serial `psycachy-linux` listed and left unselected. The embedded `activate.sh` has a blank-path promotion mismatch; the corrected source is now embedded in a separately audited local ISO; this pre-fix artifact remains ineligible for lifecycle qualification or promotion. No installation, activation, acknowledgement, promotion, rollback, or exact-hardware qualification ran; see the [boot record](archive/validation/amd64-lifecycle-iso-liveboot-20261114.md). |
| AMD64 lifecycle pilot installer (corrected prompt; parser failure) | Retired local binary after checksum verification; 8,052,277,248 bytes; SHA-256 `1406eefc1b559ec8363827521ed15e3ced7410873bf7f3d329140a2a1b286c85` | The corrected activation helper and all 282 repository payload hashes passed the independent content audit. Exact-hash KVM smoke reached the guarded selector. A later Secure Boot-enabled disposable install failed at `late-install.sh`: `dpkg-deb -f DEB Package Version` emitted labeled fields that the parser treated as bare values, so it did not identify the unique pinned NVIDIA driver/DKMS pair. The source parser fix is pushed as `d76342e`; four focused tests and `tests/static-check.sh` passed. The failed ISO's manifest, build log and checksum record remain; it was never staged on Ventoy. The new fixed candidate is separately identified below. See the [prompt-fix report](archive/validation/amd64-lifecycle-iso-promptfix-20261115.md). |
| AMD64 lifecycle pilot installer (NVIDIA parser fix) | Built and independently audited 2026-11-15; 8,052,277,248 bytes; SHA-256 `d463a31aaa0d2fbce293e38bed360f9d50770dceee344bed716bbc1d71d238fa` | Built from pushed source revision `d76342e` using the retained signed base, pinned kernel packages and offline repository. The adjacent SHA256SUMS passes. Independent review confirmed all 282 embedded package hashes/manifest records, the exact NVIDIA pair and version, embedded parser/source match, and signed-base EFI/casper kernel identity. The exact image completed a network-disabled first install on disposable `/dev/vda` (`psycachy-linux`) under the Microsoft-signed OVMF profile; after ISO ejection it booted from the installed disk through `shimx64.efi` to GDM. The prior parser failure did not recur in that first install. A later ISO re-entry relaunched the installer and showed an autoinstall command failure; after ejection, the existing disk still booted to GDM. QCOW integrity and the read-only sentinel passed, but the later run's target-write extent and package state were not audited. The selector-cancel reproduction and zero-write evidence are in the [repeat-media report](archive/validation/amd64-repeat-media-repro-20261115.md); the separate writable re-entry remains unaudited. The safe live-session path is in the [prompt-fix report](archive/validation/amd64-lifecycle-iso-promptfix-20261115.md). It remains unstaged on Ventoy and untested on physical hardware; guest Secure Boot/lockdown/module state and activation lifecycle remain open. |
| AMD64 current per-install guarded-rescue candidate | Built and independently audited 2026-11-16; 8,052,277,248 bytes; SHA-256 `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc` | All 36 build-manifest source hashes, 282 embedded repository hashes, 13 helpers, per-install pin, guarded GRUB menu, and signed-base payloads passed review. Exact-hash network-disabled QEMU install to disposable `/dev/vda` completed; the detached installed system reached GDM on Ubuntu fallback `7.3.0-10-generic`. `dpkg --audit` was empty and `apt-get check` passed. Exact-hash repeat-media boot selected default Try/Rescue and reached the language screen with the installed target and sentinel read-only and zero writes. Secure Boot was enabled, lockdown was `[integrity]`, and `module_sig_enforce=Y`; neither per-install owner key was enrolled. The installer kept the generic kernel as default pending activation, and the pinned candidate was not attempted. The read-only repeat run used a fresh disposable OVMF variables copy, so physical BootOrder is untested. Candidate lifecycle and hardware gates remain open; ISO is not staged on Ventoy. See the [2026-11-16 report](archive/validation/amd64-perinstall-guarded-rescue-20261116.md). |
| SP12 final51 installer | **Generic QEMU kernel/rootfs boot reached serial login prompt; physical installed-system boot open** | Signed base, embedded r2 pin/package pair, 120-package offline repository, retained Ubuntu live kernel/initrd, checksum and UEFI metadata verified. A 2026-11-14 detached COW follow-up confirmed that interactive, RAM-only GRUB commands can load the installed kernel/initrd/DTB; it did not record execution of the hidden zero-timeout default entry. The Surface-specific DTB fails against QEMU `virt` device addresses; omitting it let the same kernel/initrd reach the installed Ubuntu 26.10 serial login prompt under generic EFI/ACPI. No account login or authenticated session occurred; no network was used, and backing images and sentinel stayed unchanged. The follow-up demonstrates a QEMU platform mismatch but does not establish what happened in the original attempt-7 detached boot, whose vars file is missing. The separately confirmed physical live session does not close installed-system boot or installation gates. See the [detached-boot diagnosis](archive/validation/artifacts/sp12-attempt7-detached-kernel-diagnostic-20261114/report.md). |
| SP12 private final51 live image (not combined installer) | Built on `cs-sp12`, 4,810,534,912 bytes, SHA-256 `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47` | Its prior Ventoy read-back was verified. That USB file was replaced by the combined image under the approved 2026-11-15 checkpoint; the old exact image, sidecar, and buildinfo remain on SP12 for recovery. Its buildinfo has `installer_iso_sha256: null`; it verifies live media only and does not close installer integration. Its earlier QEMU run reached the private GRUB entry but not a live OS. It was not written to the Apple HDD. |
| SP12 final51 combined live/rescue/install image | Built natively on `cs-sp12` 2026-11-15; 5,500,940,288 bytes; SHA-256 `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27` | Builder validation and independent content audit passed pinned inputs, embedded payloads, guarded installer path, default Try/Rescue path, support manifest, GPT/UEFI metadata, and unchanged base installer payload. It is staged on Ventoy under its combined filename; the full destination checksum passed. Native boot, live device checks, and installed-system qualification remain open. See the [build report](archive/validation/sp12-combined-build-20261115.md) and [media write report](archive/validation/sp12-combined-ventoy-write-20261115.md). |
| Earlier private SP12 live USB | 4,810,289,152 bytes, SHA-256 `e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36` | The retained guarded write and one-time physical live-session/audio observations belong to this earlier image. They do not qualify final51; its exact runtime DTB was also unverified. |
| Earlier local private live test | ISO binaries retired 2026-11-15; SHA-256 `dfd9c3e081a002a8a9ad572750d4998da06255dd7a51cb223b5271f07b210523`, 4,810,289,152 bytes | The hash sidecar, build metadata, and test records remain. It is distinct from the earlier physical USB image and final51 live image. |
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
| AMD64 artifact identity | **Build/content review, exact-hash disposable install, detached fallback boot, and repeat-media Try/Rescue passed; lifecycle and physical checks open** | Current candidate is 8,052,277,248 bytes, SHA-256 `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`. Its sidecar, 36 source-manifest hashes, all 282 embedded repository hashes, 13 helpers, per-install pin, guarded GRUB menu, and signed-base EFI/casper/UEFI payloads passed review. Exact-hash installation completed on disposable `/dev/vda`, the installed fallback reached GDM, and repeat-media boot reached the live language screen with zero target/sentinel writes. Guest package checks passed. Neither per-install owner key was enrolled; the installer kept Ubuntu as the default pending activation, and the pinned candidate was not attempted. The re-entry used a fresh disposable OVMF vars copy. Lifecycle and physical checks remain open; image is not staged on Ventoy. See the [2026-11-16 report](archive/validation/amd64-perinstall-guarded-rescue-20261116.md). |
| AMD64 CPU target | **Pin target `znver3`; fail-closed guard integrated and reviewed** | Existing package metadata ties the ISO-pinned package hashes to Clang's effective `znver3` target on the Ryzen 7 5800X3D build host, and the pin declares `cpu_target: znver3`. The new guard probes the host Clang target against the pin, checks resolved native/generic CPU config, and preserves the legacy metadata line. Ten focused guard tests and the full static suite pass; an independent review approved the change. No kernel/package rebuild or Kbuild compiler-command evidence was produced by this guard-only change. Existing package bytes and pin are unchanged. See the [CPU-target audit](archive/validation/amd64-zen3-target-audit-20261114.md) and [continuation report](archive/validation/supervised-continuation-20261115.md). |
| AMD64 activation lifecycle | **Current-hash install and fallback boot passed; both per-install MOK keys are absent; activation lifecycle open** | The exact-hash installed guest reported Secure Boot enabled, lockdown `[integrity]`, and `module_sig_enforce=Y`. `sbverify` confirmed the candidate kernel signer, `modinfo` confirmed the NVIDIA DKMS module signer, and DKMS reported 615.71.09 installed for `7.3.1-psycachy`; `mokutil --test-key` reported both owner certificates not enrolled. The installer kept `7.3.0-10-generic` as the default pending activation, and the pinned candidate was not attempted. `dpkg --audit` was empty and `apt-get check` passed. Candidate boot, acknowledgement/refusal, promotion guard, timeout rollback, explicit rollback, replacement mode, tamper refusal, and saved-fallback recovery remain. The prior image's `PREPARE` and timeout results do not transfer. The unsigned root-controlled health attestation is an auditable workflow record, not independent cryptographic proof. |
| AMD64 Secure Boot and graphics | **Current fallback security state checked; per-install MOK trust absent; exact hardware open** | Current-hash guest state: Secure Boot enabled, lockdown `[integrity]`, `module_sig_enforce=Y`; both per-install kernel and DKMS module certificates were not enrolled. The candidate kernel is signed and DKMS modules were installed and signed, but candidate boot was not attempted because the installer kept Ubuntu as the default pending activation. The QEMU virtio-GPU VM has no RTX 4070, so NVIDIA module load, graphics acceleration, and suspend/resume are open. Enroll the keys generated by the physical B550I install through its MOK manager, then verify the exact candidate and NVIDIA hardware. |
| ARM64 final51 installer | **Interactive GRUB kernel/initrd execution confirmed in reconstructed COW; exact SP12 boot unresolved** | Attempt 7 completed installer and powered off after media ejection. The untouched no-media COW run displayed GRUB, then remained visually inactive; its serial silence was inconclusive because the installed entry uses `console=tty0`. A reconstructed follow-up used interactive, RAM-only GRUB commands and PL011 diagnostics; it did not prove execution of the hidden zero-timeout default entry. With the Surface DTB, the kernel identified the Surface Pro 12 model and failed against QEMU `virt` GIC/timer resources. Omitting that DTB reached the installed root's serial login prompt under generic EFI/ACPI; no account login occurred. The result demonstrates a reproducible emulator/platform mismatch but does not prove the original detached attempt failed at the same point. Physical SP12 boot, runtime DTB identity, and hardware checks remain open. See the [detached-boot diagnosis](archive/validation/artifacts/sp12-attempt7-detached-kernel-diagnostic-20261114/report.md) and [attempt-7 GRUB report](archive/validation/sp12-attempt7-grub-config-read-20261114.md). |
| CachyOS 7.3.4 refresh | **Deferred; existing 7.3.1/final51 retained** | The authenticated 7.3.4 source replay applies 50 of 51 entries. Entry 46 (`iris-context-bank-devices`) fails against `iris_probe.c` and overlaps upstream parent-device IOVA reservation with the downstream context-bank child-device design. The two-hour compatibility budget was not exhausted, but this is substantial safety-sensitive driver work; no full build or partial migration was started. See the [compatibility report](archive/validation/cachyos-7.3.4-compatibility-20261114.md) and [ordered replay](archive/validation/cachyos-7.3.4-ordered-replay-20261114.md). |
| SP12 final51 live startup | **Live startup confirmed; device matrix open** | On 2026-11-16 the user reported a live boot. The captured session reports kernel `7.3.1-psycachy-sp121-r2`, matching runtime DTB build ID `sha256:43e6fa05d5ee85e49bfc1d295f0ce77bcba55e1366b39f2cc6240d69783249d0`, read-only `/cdrom` and `/rofs`, and writable `/cow`. The media had previously passed a full Ventoy destination read-back at SHA-256 `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`; no in-session ISO hash was captured. Display/input, USB, wireless, Bluetooth, audio, camera, storage-health, suspend/resume, and read-only RPMB checks remain open. See the [boot report](archive/validation/sp12-firmware-boot-attempt-20261116.md) and [handoff](archive/validation/private-pilot-handoff-20261116.md). |
| ARM64 update lifecycle | **Exact-hash changed-release install, r2 media-free QEMU boot, selector/sync, rollback, and controlled dpkg recovery passed; abrupt-interruption/custom-loader limits remain** | On 2026-11-16, exact r2 image/header hashes installed as `7.3.1-1psycachy2`; dracut and kdump initramfs hooks completed, GRUB listed r2/r1/generic, `dpkg --audit` was empty, and offline `apt-get --no-download check` passed. A no-media/no-network QEMU `virt` boot reached login on `7.3.1-psycachy-sp121-r2`. `sp12-select-fallback` synchronized r1→r2 and r2→r1 in a disposable overlay; each ESP payload matched its source, `SP12BOOT` remained present, the ESP returned read-only, and the saved recovery manifest verified. Forty-eight focused process/unit simulations passed. A controlled `dpkg --unpack`→`dpkg --configure -a` recovery passed with clean audit and offline dependency check; abrupt termination during postinst/dracut and reboot through the custom SP12 EFI path remain untested. Physical SP12 behavior is unqualified. See the [2026-11-16 report](archive/validation/arm64-r2-update-qemu-20261116.md) and [evidence bundle](archive/validation/artifacts/arm64-r2-update-qemu-20261116/). |
| Restored-target boot | **Physical default boot passed within scope; generic-QEMU restored-root userspace control passed; automatic DTB/default boot open** | Retained physical records support restored default SP12 userspace with matching recovery payload hashes and a read-only ESP. A 2026-11-14 display-enabled COW run confirmed the disposable ESP loader reaches GRUB 2.14 and that its root's hidden default names kernel/initrd/DTB `7.3.0-10-generic`; a corrected-stub automatic probe remained serial-silent after UEFI BootNext and did not prove the default ran. A separate fresh-COW generic EFI/ACPI control manually loaded that kernel/initrd without a DTB, mounted the restored root, `/boot`, restored ESP (`C1D2-E253`), and `/mnt/sp12-data`, reached `getty.target` and `sp12-phase1-vm login:`, then shut down cleanly after QMP powerdown. No credentials were entered. All six COWs passed `qemu-img check`; retained source/backing/ESP/firmware/vars hashes passed. This proves generic QEMU restored-root userspace only; no in-guest `dpkg --audit` or payload comparison, automatic default-entry, Surface-DTB, or physical boot qualification was performed. See the [generic-control report](archive/validation/artifacts/sp12-restored-target-generic-control-20261114/report.md), prior [attempt report](archive/validation/artifacts/sp12-restored-target-cow-boot-20261114/boot-report.md) (SHA-256 `b6fd49ad455334173c0896dc50de60e3ecc6f48fa584de93fca21482ccb12208`), and [recovery reconciliation](archive/validation/sp12-recovery-reconciliation-20261114.md). |
| FAT/process interruption recovery | **48 focused mock/process simulations pass; sector-EIO and physical power-loss limits remain** | The 2026-11-16 focused run passed 48 tests across boot synchronization, candidate selection, recovery/restore, staged flush, payload promotion, marker, rotation/retry, FAT cleanup ownership, and sector-map parsing. Earlier FAT evidence includes exact-sector positive controls and one passing guest allocation-metadata EIO during staged payload flush. Other fault points remain incomplete or inconclusive; no software test establishes physical power-loss safety. See the [ARM64 update report](archive/validation/arm64-r2-update-qemu-20261116.md) and its focused-test transcript. |
| SP12 combined live/rescue/install ISO | **Built, audited, staged, read back, and booted to live session; device and install gates open** | The candidate is 5,500,940,288 bytes, SHA-256 `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`. Native validation passed the final51 kernel/modules/DTB, initramfs, live layer, guarded opt-in installer, unchanged base install layers, and physical ESP/NVRAM/mount-state checks. Independent content audit and full Ventoy destination read-back passed. The user-provided physical live-session diagnostics match the pinned kernel and DTB build ID; the capture has no in-session ISO hash. Device-function checks and external installation remain open. See the [boot report](archive/validation/sp12-firmware-boot-attempt-20261116.md), [build and audit report](archive/validation/sp12-combined-build-20261115.md), and [media write report](archive/validation/sp12-combined-ventoy-write-20261115.md). |
| Ventoy USB media | **SP12 combined and AMD64 pre-fix files fully read back; corrected AMD64 file not staged** | The UDisk serial `General_UDisk-0:0`, Ventoy UUID `4E21-0000`, holds the pre-fix AMD64 ISO SHA-256 `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c` (8,052,277,248 bytes) and combined SP12 ISO SHA-256 `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27` (5,500,940,288 bytes); both full destination read-backs returned `OK`. The prior SP12 live-only ISO was removed, with its recovery copy and metadata retained on SP12. The data partition has 2,138,603,520 bytes free; VTOYEFI and partition layout were unchanged. The corrected AMD64 image remains local and awaits its own supervised media checkpoint. The previously reported BootOrder discrepancy remains unresolved; no firmware change was made. See the [USB write record](archive/validation/artifacts/usb-ventoy-inventory-20261114/write-record.md) and [combined image write report](archive/validation/sp12-combined-ventoy-write-20261115.md). |
| AMD64 one-time media boot | **Earlier pre-fix physical boot user-reported; neither later candidate physically booted** | The user reported that the older pre-fix USB ISO reached the installer on the MSI MPG B550I Gaming Edge WiFi with a generic live kernel recalled as `7.3.0-9-generic`; this does not test the installed candidate's `znver3` kernel. The previous prompt-fix ISO (`1406eefc…`) passed insecure selector smoke but failed a Secure Boot-enabled disposable installation. The new parser-fix ISO (`d463a31a…`) independently passed content audit and reached the guarded disk selector in Secure Boot QEMU, showing only `/dev/vda` (`psycachy-linux`) unchecked. Neither later candidate has been written to Ventoy or physically booted. The 2026-11-14 USB write record and later BootOrder discrepancy remain recorded. |
| Physical B550I qualification | **No physical rehearsal started; exact-hash disposable install and fallback boot passed; hardware/lifecycle gates open** | The Apple HDD was reidentified read-only on 2026-11-15 by stable ID `/dev/disk/by-id/ata-APPLE_HDD_HTS545050A7E362_TNS519GY1G6JGG`, model `APPLE HDD HTS545050A7E362`, serial `TNS519GY1G6JGG`, and 465.8 GiB capacity; current path was `/dev/sda` and it was unmounted. Its observed contents remain an Ubuntu 26.10 ARM64 ISO signature, small ESP, and ext4 partition. The exact current ISO completed a disposable Secure Boot-profile install and detached boot to generic fallback; package and repeat-media checks passed. Its owner keys were not enrolled in the VM. Physical MOK enrollment, RTX 4070/NVIDIA, promotion, update, rollback, networking/audio/suspend, Ventoy staging, and device checks remain open. No Apple HDD or internal-disk write occurred; use a fresh serial-bound target checkpoint before rehearsal. |
| Physical SP12 qualification and fresh install | **Live startup passed; live-device matrix and separately checkpointed external install remain open** | The Apple HDD remains the sequential B550I/SP12 rehearsal target; no final51 image was reported written to it. The combined image is staged on Ventoy with a matching full destination read-back hash. After Ventoy was absent from the first one-time firmware menu, the user later reported a successful live boot with the expected kernel and DTB build ID. The in-session capture lacks an ISO hash and does not include the device matrix. External installation still requires the software gates, fresh target/artifact/serial checkpoint, and explicit approval; internal installation remains out of scope. See the [boot report](archive/validation/sp12-firmware-boot-attempt-20261116.md), [USB inventory](archive/validation/artifacts/usb-ventoy-inventory-20261114/inventory.md), [write record](archive/validation/artifacts/usb-ventoy-inventory-20261114/write-record.md), and [combined-image write report](archive/validation/sp12-combined-ventoy-write-20261115.md). |
| RPMB and protected data | **Physical gate open** | Physical exact-candidate registration/health checks remain read-only. RPMB provisioning/data writes and firmware trust changes are outside scope. Samsung BitLocker storage, Lexar BIOS media, and the attached Switch SD remain protected. |
| Storage and VM capacity | **80 GiB reserve maintained; 165 GiB free after disposable ARM64 VM cleanup** | The 2026-11-16 cleanup removed superseded ISO/package generations, completed VM captures, duplicate caches/build outputs, obsolete QEMU build outputs, and the disposable ARM64 update/recovery clones while preserving pinned inputs and repository evidence. The exact-hash AMD64 install/repeat-media and ARM64 update/boot/recovery overlays passed QCOW integrity checks; package ISO and protected sentinel write counters remained zero. See the [cleanup report](archive/validation/storage-cleanup-20261116.md), [AMD64 evidence bundle](archive/validation/artifacts/amd64-perinstall-guarded-rescue-20261116/), and [ARM64 update evidence](archive/validation/artifacts/arm64-r2-update-qemu-20261116/). |
| Public-release requirements | **Deferred** | Paired performance trials and redistribution/attribution clearance are outside this private-pilot scope. This ledger is not a public ship approval. |

## Remaining gates before private-pilot shipment

The build and content-audit gates are complete for the current candidates, but
neither ISO is ready for supported installation. The checks below close the
remaining private-pilot gates; physical writes still require a fresh
artifact/hash/device-serial checkpoint and explicit approval.

### AMD64 B550I candidate

- [x] Freshly install exact current hash
  `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc` on a
  new 64 GiB disposable `/dev/vda` (`psycachy-linux`). The installer completed
  after explicit first-install and erase prompts. At completion the target
  had 17,259,126,272 QEMU write bytes and the read-only sentinel had zero.
  The detached installed disk reached GDM on generic fallback
  `7.3.0-10-generic`; package audit and post-boot `apt-get check` passed. Both
  QCOWs and the sentinel hash/pattern passed. A live-session reboot attempt
  displayed an init-kill kernel panic; the installed disk subsequently booted
  after explicitly selecting it. See the [exact-hash report](archive/validation/amd64-perinstall-guarded-rescue-20261116.md)
  and [evidence bundle](archive/validation/artifacts/amd64-perinstall-guarded-rescue-20261116/).
- [x] Repeat-media against the exact installed candidate. The same ISO
  defaulted to Try/Rescue and reached the Ubuntu language screen with the
  installed target and sentinel read-only; both had zero writes and no
  autoinstall failure appeared. The repeat VM used a fresh disposable OVMF
  variables copy, so physical BootOrder remains open.
- [x] Classify the selector-cancel dialog on the prior `d463a31a…` image: it
  is the intended fail-closed response when no disk is selected, and the
  reproduction recorded zero target/sentinel writes. See the [reproduction
  report](archive/validation/amd64-repeat-media-repro-20261115.md). This does
  not replace the exact-hash repeat-media result above.
- [x] Audit the exact-hash current install's target and repeat-media state:
  installer completion write extent, `dpkg --audit`, `apt-get check`, QCOW
  integrity, and sentinel checksum/pattern are recorded. The older
  `d463a31a…` artifact's writable ISO re-entry remains a historical audit gap;
  that ISO is retired and its result does not transfer to this candidate.
- [ ] Run the exact current candidate's activation lifecycle: preparation
  and boot, acknowledgement, promotion, userspace-timeout rollback, explicit
  rollback from acknowledged state, replacement mode, tamper refusals, and
  recovery of the saved generic fallback. Preserve candidate and backup
  identities and collect package-health evidence. Promotion must refuse
  incomplete NVIDIA/hardware attestation in generic QEMU; actual promotion
  belongs in the physical B550I rehearsal.
- [x] Record installed-guest Secure Boot, lockdown, `module.sig_enforce`,
  candidate kernel/module signer, MOK enrollment, DKMS, and package state.
  Secure Boot and signature enforcement were active; neither owner key was
  enrolled, and the installer kept Ubuntu as the default pending activation.
  The pinned candidate was not attempted. See the evidence bundle.
- [ ] On the physical B550I install, enroll its per-install kernel and DKMS
  certificates in MOK; boot the exact pinned candidate and verify RTX
  4070/NVIDIA module loading, graphics, networking, audio, suspend/resume,
  update, and fallback behavior. Do not reuse keys from the disposable VM.
- [ ] Investigate the observed Try/Rescue live-session reboot panic
  (`Attempted to kill init! exitcode=0x0000000b`) and confirm reboot or
  shutdown behavior on the attended hardware rehearsal.
- [ ] After software gates and the return window, stage the current ISO hash
  `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc` on
  Ventoy using its own file-level checkpoint and full read-back hash. Then
  one-time boot that exact image on the B550I without changing persistent
  firmware order. Verify Secure Boot, RTX 4070/NVIDIA, graphics, networking,
  audio, suspend/resume, update, and fallback behavior. Any external install
  must use an approved serial-identified disposable target; keep internal and
  protected disks out of the harness.

### ARM64 SP12 combined candidate

- [ ] Boot the staged combined hash
  `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27` once
  on native SP12. Preserve firmware order and use only the Try/Rescue entry.
  Confirm the live session reaches userspace and reports the pinned final51
  kernel, initramfs, modules, and runtime DTB/build ID.
- [ ] Qualify live hardware behavior on SP12: display/input, USB, Wi-Fi,
  Bluetooth, audio, camera, storage health, and suspend/resume. Run the
  exact-candidate RPMB registration/health checks read-only; do not provision
  keys or write RPMB data.
- [ ] Install only to an approved serial-identified external/disposable
  target, remove the media, and boot the installed system. Verify the final51
  kernel/DTB, boot-sync payloads on the ESP and fallback, package health,
  recovery checksums, and protected-disk sentinel.
- [ ] Complete a changed-package update and rollback trial. The prior attempt
  stopped at a login prompt before `dpkg`, hooks, dracut, or boot-payload sync;
  an authorized disposable login/seed and sufficient measured space are
  prerequisites. Verify update, reboot, fallback, and rollback results.

### Shared release closeout

- [ ] Resolve or explicitly accept the remaining FAT/recovery interruption
  gaps and document the limits of simulated power-loss coverage.
- [ ] Freeze each final ISO, package, kernel, DTB, config, source, and manifest
  identity; archive the final checksums and all hardware/lifecycle evidence.
- [ ] Keep the 7.3.1/final51 SP12 base unless the 7.3.4 Iris patch-46 replay
  incompatibility is separately resolved and the candidate is rebuilt and
  requalified.

These are private-pilot gates. Public release additionally requires decisions
for all six Phase 2 scenarios on both targets (at least three interleaved
baseline/candidate pairs per scenario, with at least 10% lower whole-system
energy where measurable, completion time no more than 10% longer, and p95
response latency no more than 5% worse). New storage errors, watchdog events,
failed resume, or functional regressions reject a result. Redistribution and
attribution clearance is also required. SP12 whole-system energy remains
unavailable under the approved measurement setup.

## Current dependencies and order

1. The current AMD64 candidate is 8,052,277,248 bytes, SHA-256
   `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`.
   Its sidecar, 36 source-manifest hashes, 282 embedded repository hashes,
   13 helpers, per-install certificate binding, guarded Try/Rescue menu, and
   signed-base boot payloads passed independent review. Exact-hash install to
   disposable `/dev/vda`, detached boot to the generic `7.3.0-10-generic`
   fallback, `dpkg --audit`, `apt-get check`, candidate signature inspection,
   and a read-only exact-hash Try/Rescue re-entry passed. Both per-install
   owner keys were not enrolled; the installer left the generic fallback as
   default pending activation, and the pinned candidate was not attempted. A live
   Try/Rescue reboot attempt displayed an init-kill kernel panic; the
   installed disk subsequently booted to GDM after explicit disk selection.
   Candidate lifecycle, physical BootOrder/MOK/NVIDIA, Ventoy staging, and
   B550I hardware checks remain open; the ISO is not staged on Ventoy. The
   exact run and limits are in the [AMD64 report](archive/validation/amd64-perinstall-guarded-rescue-20261116.md)
   and [evidence bundle](archive/validation/artifacts/amd64-perinstall-guarded-rescue-20261116/).
   At closeout `/` had 164.47 GiB free; see the [cleanup report](archive/validation/storage-cleanup-20261116.md)
   for the retention work and prior measurement. QEMU does not replace
   physical qualification.
2. The 2026-11-16 ARM64 changed-release run passed exact-hash package install,
   completed dracut/kdump/GRUB hooks, media-free r2 boot through Ubuntu
   shim/GRUB, r1↔r2 SP12 payload selection/rollback, and controlled recovery
   from an unpacked dpkg state on disposable QEMU storage. Forty-eight
   focused process/unit simulations passed. Abrupt termination during a
   postinst/dracut hook and boot through the custom SP12 fallback EFI path
   remain open; physical SP12 boot is not inferred. See the [update report](archive/validation/arm64-r2-update-qemu-20261116.md).
3. The combined SP12 image is built, independently content-audited, staged on
   Ventoy, and passed a full destination read-back. The user later booted to a
   live session with the expected kernel and DTB identity after an initial
   firmware-menu attempt did not list Ventoy. Next, complete the live-device
   and read-only RPMB checks, transfer evidence with verified hashes, and
   finish software gates before any separately checkpointed external install.
   Do not change persistent firmware order or select the installer entry
   during live qualification.
4. Rebuild other affected candidates only when measured storage can preserve
   the 80 GiB reserve; freeze new checksums before requalification.
5. The Apple HDD target was reidentified read-only on 2026-11-15 by model,
   serial, capacity, stable ID, contents, and mount state; it is currently
   `/dev/sda` but future paths may differ. A local console runbook is ready,
   but the corrected candidate's boot/lifecycle and remaining software gates mean no fresh write checkpoint
   is active. The user authorized sequential B550I then SP12 rehearsal use;
   each physical write still requires its own artifact/hash/serial/partition
   checkpoint and explicit approval. A prior read-only inventory recorded a
   Ventoy BootOrder entry on the B550I; it does not establish SP12's firmware
   state. The first 2026-11-16 SP12 one-time menu did not list Ventoy, but the
   user later reported a live boot with the expected kernel and DTB build ID.
   No persistent firmware change is reported. The live boot does not establish
   the full device matrix or an independent recovery path. Keep both systems'
   internal disks out of installation harnesses.

Keep private signing keys outside media and repository artifacts. Do not mark
either pilot complete until its exact candidate passes the required software,
recovery, hardware and restore gates.
