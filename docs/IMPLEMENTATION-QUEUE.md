# Implementation queue

This file tracks code changes that are not yet implemented or whose need is
conditional on reproducing a failure. Validation-only work belongs in the
[ship checklist](SHIP-CHECKLIST.md). Do not make changes to device boot policy
or recovery-panel files from this queue without the approvals and rollback
conditions stated below.

Current private-pilot gate status is maintained in the
[qualification ledger](PRIVATE-PILOT-QUALIFICATION.md). This queue records code
work only; artifact and hardware qualification evidence stays in the ledger
and ship checklist.

The 2026-11-16 storage reclamation and SP12 live-boot diagnostics are
validation-only; their current boundaries are in the [cleanup report](archive/validation/storage-cleanup-20261116.md),
[boot report](archive/validation/sp12-firmware-boot-attempt-20261116.md),
[private-pilot handoff](archive/validation/private-pilot-handoff-20261116.md),
and [ship checklist](SHIP-CHECKLIST.md). The observed kernel and DTB match the
final51 pins; no source change follows from this boot result.

## Active or conditional code work

### I-5: Integrate AMD64 activation with the kernel-trial state machine

**State:** Lifecycle implementation, NVIDIA package-pair parsing, and the
fail-closed blank-attestation-path fix are integrated. The current candidate
was built and independently audited on 2026-11-16:
`output/amd64-iso-lifecycle-20261116-perinstall-guarded-rescue/psycachy-ubuntu-26.10-desktop-amd64.iso`,
8,052,277,248 bytes, SHA-256
`908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`. Review
matched all 36 source-manifest entries, 282 repository hashes, 13 embedded
helpers, per-install pin, guarded Try/Rescue menu, signed-base EFI/casper
payloads, and UEFI boot image. The exact-hash default Try/Rescue path reached
the Ubuntu live desktop in a network-disabled, diskless VM. It has not yet
been freshly installed, re-entered as repeat media, or run through the
lifecycle. See the
[2026-11-16 report](archive/validation/amd64-perinstall-guarded-rescue-20261116.md).

Source checks passed: 40 phase2 trial tests, 6 GRUB-menu tests, 10
disk-selector tests, and `tests/static-check.sh` (the root-only `mokutil`
probe was skipped). A separate prior-image run on the `per-install-pin` ISO
(SHA-256
`3c8d488be56c0b94e3a535c6fd3cfed9b84c55d65a41fc15056be43ffe1abb36`)
confirmed Secure Boot and both MOK enrollments, then `PREPARE` scheduled a
one-shot trial. The helper recorded `timed_out` because required `nvidia` was
not loaded, and the guest was on the `7.3.0-10-generic` fallback. That VM had
no NVIDIA device, did not demonstrate candidate runtime, and did not perform
acknowledgement or promotion. Its results do not transfer to the current ISO.

The implementation provides `prepare -> candidate boot -> acknowledge ->
promote`, explicit first-install/replacement records, fallback preservation,
package/signing identity separation, runtime module signature/trust checks,
and rollback from acknowledged or promoted state. The health attestation is
unsigned and root-controlled, so it is an auditable workflow record rather
than cryptographic proof of independent approval. The timeout is a userspace
guard and cannot recover pre-userspace hangs. Remaining work is validation on
the exact current ISO and target hardware; see the
[qualification ledger](PRIVATE-PILOT-QUALIFICATION.md) and
[ship checklist](SHIP-CHECKLIST.md).

### I-6: Reproduce ARM64 changed-release boot-payload updates

**State:** Partial; the 2026-11-16 disposable QEMU run completed exact-hash r2
package installation, dracut/kdump/GRUB hooks, clean `dpkg --audit`, offline
`apt-get --no-download check`, a media-free r2 boot through Ubuntu shim/GRUB,
and the SP12 selector/sync round trip r1→r2→r1. The ESP kernel, initramfs,
and DTB matched each selected source; the marker and read-only remount were
verified, and the recovery manifest passed. Forty-eight focused process/unit
simulations passed across boot sync, fallback selection, recovery/restore,
flush/promotion/marker/rotation faults, FAT cleanup ownership, and sector-map
parsing. A controlled dpkg recovery also passed: after `dpkg --unpack` left the
r2 image and headers unconfigured, `dpkg --configure -a` completed hooks,
initramfs generation, GRUB regeneration, and boot synchronization; final audit
and offline dependency checks passed. See the [2026-11-16 report](archive/validation/arm64-r2-update-qemu-20261116.md)
and [evidence bundle](archive/validation/artifacts/arm64-r2-update-qemu-20261116/).

The first 2026-11-14 attempt remains correctly classified incomplete; it had
no authenticated shell and no dpkg transition. The later run does not close
recovery after forcibly stopping QEMU or killing dpkg during postinst/dracut,
a reboot through the custom SP12 fallback EFI path after synchronization, or
physical SP12 qualification. The process tests use temporary fixtures and do
not establish physical power-loss safety. No code gap was demonstrated by the
successful changed-release run; make no implementation change unless a new
reproducer shows one.

**Done when:** a reviewed disposable sequence proves changed-release package
hooks, media-free candidate boot, matched kernel/module/DTB/initramfs ESP
selection, return to the prior payload, recovery from an unpacked but
unconfigured package state, and the limits of abrupt-interruption,
physical-loader, and power-loss scope without changing retained VM bases.

### I-7: Add opt-in installer payload to the private SP12 live builder

**State:** Builder integrated and independently reviewed; the combined private
image is built and its contents independently audited. Native runtime and
physical qualification remain open. The builder accepts the
separate generic ARM64 offline installer payload with an exact SHA-256,
selected-kernel pin checks, guarded install entries, target-support copying,
initramfs regeneration, and final audit checks. The Try/Rescue entry remains
the default and has no autoinstall command.

The reviewed patch SHA-256 is
`99380ea7052f33043570435acc25771c3c3a053d2f5d234a8c4debd6ebe557cf`. The
[integration record](archive/validation/sp12-installer-integration-20261114.md)
and [independent review](archive/validation/artifacts/sp12-installer-integration-20261114/independent-review.md)
retain the integration evidence. The combined image was built natively on
`cs-sp12` from the exact final51 package pair, signed Ubuntu base, installer
ISO, and pinned private support inputs. The builder reported
`validated=True`; 16 focused builder tests and the main-workspace static
suite pass. Independent review passed the complete output content audit.
The image is 5,500,940,288 bytes with SHA-256
`56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`.
Its default Try/Rescue entry has no autoinstall command, the explicit
installer path is guarded, and generic diagnostics remain separate. The
build and audit report is
[here](archive/validation/sp12-combined-build-20261115.md).
The user-approved file-level Ventoy replacement and full read-back of the
combined and protected AMD64 ISOs passed; see the
[media write report](archive/validation/sp12-combined-ventoy-write-20261115.md).

The four source worktrees and dirty source state remain; only generated
Kbuild files and six uninstalled debug-symbol package archives were removed
after review and checksum verification. The signed base, local private
support inputs, active package archives, and old live-only recovery image are
retained. The user ran the guarded cleanup for seven exact SP12 staging and
scratch trees; the remote root now has 223,941,722,112 bytes free. The
combined image is on Ventoy with both destination read-back checks passed.
The user later reported a physical live boot whose captured kernel and DTB
build ID match the final51 pins; the capture has no in-session ISO hash. The
live-device matrix, external install, and installed-system qualification
remain open.

**Done when:** menu/payload pins and target support hashes verify, unattended
installation is not possible from the default entry, generic diagnostic and
guarded installer paths pass focused tests, and the rebuilt private image has
frozen checksums. These software, content-audit, and media-staging checks now
pass. The user has confirmed native live startup with matching kernel/DTB
identity; device/rescue checks and installed-system qualification remain.

### I-8: Fail closed on the AMD64 native CPU target

**State:** Implemented and independently reviewed on the continuation branch;
integrated source/tests pass focused and static checks. The AMD64 builder now
compares Clang's effective `-march=native` target with the existing pin's
`cpu_target` before compilation, validates resolved native/generic CPU Kconfig
selection, and records expected/detected values while retaining the prior
metadata line. Tests cover match, mismatch, malformed/missing/ambiguous Clang
output, malformed pin data, rejection outside AMD64, unchanged ARM64 dry-run
dispatch, and option validation.

No kernel/package rebuild or Kbuild command evidence was produced by this
guard-only change. Existing authenticated package bytes and the pin remain
unchanged; any later full build must capture actual Kbuild compiler commands
and bind that evidence to the resulting package hashes.

### I-4: Refresh SP12 r2 kernel inputs, identity, config, and DTB evidence

**State:** The active 51-entry source series includes the reviewed USB,
WCN7850 Bluetooth, Hamoa Iris driver/DTS changes, and their two context-bank
binding patches. Two complete ordered replays from the authenticated signed
7.3.1 archive produced the same final tree digest
`192c5187bca08d67cb167cf7be77996fdde7f4c3717e19bb200775bf48a161fb`. Its
manifest SHA-256 is
`6040fc283d5afe04ddfa69d1bc418ead62b5de2984b73f42c22e144a6ca74e14`.
The corrected config audit, focused changed-C compile, Iris `dt_binding_check`,
fresh target-DTB compile, and schema validation passed. The full51 ARM64 package
build passed with `TMPDIR=/var/tmp` after an earlier `/tmp` tmpfs quota failure;
the 8,487-module audit and package verification passed. The r2 pin and final51
installer ISO are refreshed. Rootless live-builder dry-runs passed on both the
x86_64 build host and native ARM64 `cs-sp12`; the latter verified the signed
base, final51 package pair, pinned support checkout, and all four private
machine-file hashes without creating an image or mounts. The native ARM64
`--apply` build passed on `cs-sp12`; its private ISO SHA-256 is
`099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47`.
QEMU attempt 6 stopped at the chooser before writes. Attempt 7 selected only
the disposable target (`psycachy-arm64-linux`), accepted the exact `ERASE`
guard, and reached “Ubuntu 26.10 is installed and ready to use” at
2026-11-14 00:04:52 UTC. It recorded 12,149,606,912 target write bytes across
49,149 operations, no failed target writes, and zero sentinel or ISO writes.
After ejecting the installer ISO and pressing Enter at Ubuntu's removal prompt,
the guest reached systemd poweroff. The QEMU process exited; target and
sentinel QCOW checks passed and the sentinel hash remained unchanged.

A detached-media boot was attempted from that installation through a temporary
QCOW overlay with networking disabled. UEFI loaded the saved Ubuntu entry and
started `shimaa64.efi`, but the display went inactive, serial output stopped
after the shim handoff, and target reads stopped at 77,785,600 bytes. After
about five minutes with no OS login, an ACPI powerdown request received no
guest response; QEMU was stopped through QMP. The installed base QCOW, overlay,
and sentinel all passed post-stop checks, and the sentinel hash was unchanged.
This attempt does not qualify a detached-media boot or the r2 runtime kernel.
The attempt-7 install and boot evidence is under
`docs/archive/validation/artifacts/sp12-r2-final51-20261113/`.

A second live-media check ran on native ARM64 `cs-sp12` in QEMU TCG because
`/dev/kvm` is unavailable. UEFI and GRUB 2.14 reached the private “Try SP12
Ubuntu 26.10” entry, but the display went black after handoff, serial output
stopped, and ISO reads stalled at about 200 MB. No disks or network were
attached; ISO writes remained zero. The VM was stopped after about six minutes
without a live desktop or login. This confirms UEFI/GRUB only, not live OS
startup or SP12 hardware behavior. Evidence is in
`docs/archive/validation/artifacts/sp12-r2-final51-20261113/`.

The 2026-11-12 session record documented the user onsite and the Apple HDD
holding the earlier private live USB image, SHA-256
`e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36`. The
final51 live image was built separately on `cs-sp12`; at that historical
inventory, the expected Apple HDD was absent and the B550I had no separate
blank installation target. Installer completion is confirmed in
generic QEMU, while live OS startup, detached boot, exact candidate-kernel/runtime-DTB
qualification, and physical hardware qualification remain pending.
Attribution/redistribution review is deferred for private-pilot scope. See the
[51-entry replay and DT schema report](archive/validation/sp12-r2-source-dt-schema-validation-20261113.md).

Historically, the 37-entry source series passed two full sequential replays
after clean builds exposed a UniPHY enum/macro collision, an OV02C10 V4L2
callback mismatch, and two unused CAMSS locals. Local patches address each;
the changed C objects compile with the r2 config, and the CAMSS cleanup
compile is warning free. The clean full ARM64 package build completed
successfully. The series contains ten reviewed r1 patches and 27 r2 patches.
Both replays produced final source digest
`f7d05945e58b3ac688caa240734525bafbdd246aa9a0c6d00ad87645a902893e`; the
pristine digest is
`dc272061b7eea961aac2112c46dc140d778a7de3bbff7dff8d1068c571631ffa`. The
active manifest SHA-256 is
`46528c8cfe61e1fb068fb4d1394de121bb9a1ce080db1287a1cb68492dc79cc2`, and the
r2 seed SHA-256 is
`cd5027943acfa23b4fc9798cc71f6f3d88996b54a3d25ec2b873762dc39e01a0`. The
overlay is frozen at `952f769e1b45f07302d69992d19e5874ee77737`, with inclusive
audit range
`ed20a9946e0136485bbac067e72100b84a0865fd^..952f769e1b45f07302d69992d19e5874ee77737`.

Camera support is required and implemented in the original 37-entry
source/config candidate. Independent review confirmed its CAMSS/CCI/CSI D-PHY/provider,
sensor, clock, and SP12 board wiring closure. Physical enumeration/capture and
the remaining SP12 hardware checks are still unqualified. The resolved config
passed 52 required-value checks with zero
mismatches or unexpected changes and the release-policy audit. The selected
camera schemas and targeted `dt-validate` passed at the earlier 34-patch
checkpoint; final37's last three patches are C-only. Final37 rebuilt the SP12
DTB and package verification matched its build ID. The final packaged DTB
SHA-256 is `ec0d4d44dfd495b5c771780fc990fa6ec8c1f617faedb174509b043f87a5da69`,
with build ID
`sha256:5ec821abf77f1ff32e2b38787b9e709bddebd918530c5ca25422f109ded5cdc9`.
Normalized config SHA-256 is
`cd8938fa6fb20bb3b7b7a131b105f5c83f9463776a18c33fe1e6dc62028d1957`. The
image and headers packages passed built-in and independent package checks;
their hashes and module-signature scope are recorded in the final37 report.
Separate r2 pin `config/arm64-iso-kernel-r2.json` matches the authoritative
identity and the verified package pair; the v4 pin remains unchanged. The
package bundle check passed. The standard static suite passed, with the
root-only `mokutil` check skipped. Root free space immediately before build was
132,098,420,736 bytes (about 123.0 GiB). The rootless r2 installer ISO passed
base, package-closure, embedded-payload, checksum, and UEFI metadata checks.
Its SHA-256 is
`f990d6308f9342dd5208ebe18c4ce5e9cb876ca418048e887d4894982841c037`. Four
network-disabled generic ARM64 QEMU `virt` attempts have run. The first
remained in early setup, the second reached a visible login without input
devices, and the third kept GDM on a second display outside VNC. Their
post-stop QCOW and sentinel checks passed. The fourth uses one virtio display
plus keyboard/tablet; it reached the disk chooser, selected only the disposable
`psycachy-arm64-linux` target, accepted the exact-serial `ERASE` prompt, and
advanced through the locale, keyboard, user, and timezone screens. The
At the 07:34 snapshot, the base image install had finished at 07:10 and the
installer was still running in-target package configuration. The log showed dracut generating the
generic fallback initramfs. A preceding `unexpected argument '-t'` message
was followed by apt package fetches and continued in-target commands; final
status was pending at that snapshot. A later `kdump-tools` hook reported a missing `chroot`
`<newroot>` argument, then proceeded to kdump initramfs generation. Curtin
reported `cmd-install: SUCCESS` at 07:26 after its 916.9-second stage-curthooks;
final system configuration is installing the pinned kernel pair from the
local repository, and the log now shows both r2 packages being set up and
dracut generating the candidate initramfs. The translation-file warnings did
not stop apt. At the 07:34 local sample, the target had 11,601,602,048 bytes
written; the read-only sentinel and ISO had zero writes, and the sentinel hash
still matches. Installer completion,
post-stop QCOW checks, package hooks,
detached-media boot, and runtime `psycachy,dtb-build-id` remained open at that
snapshot.
Independent private-support and kernel-input checks passed. The rootless
live-builder dry-run passed after staging the missing initramfs tools under
`/var/tmp`; no host packages, mounts, or output files were created. The actual
apply build still requires native ARM64, root, and isolated mount/network
namespaces. Physical qualification remains open.
Attribution and public redistribution review remain open. See the
[final source/config/DT/package report](archive/validation/sp12-r2-config-dt-final-20261113.md),
[per-patch replay](archive/validation/sp12-r2-source-replay-20261113-final-37-patch-series.json),
[overlay provenance index](../targets/sp121-arm64/provenance/r2-overlay/README.md),
and [storage reclamation record](archive/validation/storage-reclamation-20261113.md).

### 2026-11-14 bounded stable refresh decision

The exact CachyOS `7.3.4-1` archive was authenticated and staged durably. The
ordered 51-entry SP12 replay applies 50 entries; patch 46,
`patches/r2/video/02-iris-context-bank-devices.patch`, fails at `iris_probe.c`.
7.3.4 has a parent-device IOVA reservation in the same Iris probe/remove path
where the downstream patch introduces context-bank child devices. This
requires driver and DMA/IOMMU reconciliation. Stop this refresh, keep the
authenticated 7.3.1/final51 candidate, and do not build from the incomplete
tree. No source pin, patch, or config changed. See the [bounded compatibility
report](archive/validation/cachyos-7.3.4-compatibility-20261114.md) and [full
ordered replay](archive/validation/cachyos-7.3.4-ordered-replay-20261114.md).

The associated [AMD64 target audit](archive/validation/amd64-zen3-target-audit-20261114.md)
confirms the ISO-pinned kernel build is already compiled for Zen 3 (`znver3`);
no architecture migration is indicated. Its builder still uses
`-march=native` without enforcing that target against the pin.

The exact private SP12 support checkout and four matching machine files were
recovered to `phase0-work/private-inputs/`. `cs-sp12` remote storage is below
the native builder's 24 GiB minimum plus snapshot/output requirements. The
Apple HDD is now identified at `/dev/sdb` by model and serial, read-only
inspected, and unmounted; the user authorized its sequential B550I use. At the
2026-11-14 inventory, the separate Ventoy USB had only 2,353,856,512 bytes
free. On 2026-11-15, after explicit authorization, both old ISO files were
replaced with the AMD64 lifecycle and SP12 final51 ISOs; full destination
read-back hashes matched. The user later reported an AMD64 installer boot on
B550I with a generic live kernel; no exact kernel log or selector state was
retained. The original UEFI BootOrder was restored. No Apple HDD installation
write has occurred; a serial-bound external-install checkpoint was presented
and held at the user's request. See the [USB write record](archive/validation/artifacts/usb-ventoy-inventory-20261114/write-record.md),
[dated execution report](archive/validation/bounded-refresh-and-readiness-20261114.md),
and [qualification ledger](PRIVATE-PILOT-QUALIFICATION.md).

**Historical final37 installer VM result (attempt 4):** it reached the completion screen and
stopped cleanly. The target receipt lists the pinned r2 image and headers
packages at `7.3.1-1psycachy2`; both QCOW checks and the protected-disk sentinel
passed. With media detached, UEFI reached Ubuntu's serial login using the
default `7.3.0-9-generic` GRUB entry. GRUB did not list the installed r2
candidate, so this is generic fallback evidence only; candidate boot and
runtime DT build-ID verification remain open. Exact evidence is checksummed in
`archive/validation/artifacts/sp12-r2-installer-20261113/attempt-4/`.

### 2026-11-13 independent coverage audit — 49-entry predecessor replay passed

The 37-entry replay remains reproducible but did not cover all requested SP12
device features. The USB, Iris, Bluetooth, and timer additions below were
captured in the 49-entry predecessor manifest and passed two ordered replays.
That candidate was later extended with Iris binding patches after DTB schema
validation exposed the missing bindings. The active series now has 51 entries;
its replay and binding-validation evidence is linked above. The prior package
and ISO hashes remain diagnostic.

| Area | Source finding | Required disposition before rebuild |
| --- | --- | --- |
| USB host PHY | Overlay `usb/0001` handles the DWC3 xHCI host-PHY initialization path needed for runtime suspend/power-down. | Included at order 38; compile and qualify host suspend/exit on SP12. |
| USB eUSB2 wake | `usb/0002` supplies type-aware IRQ/polarity handling; it is a prerequisite for 0004. | Included at order 39, before 0004. |
| USB failed resume/runtime PM | `usb/0004` follows 0002; `usb/0005` addresses back-to-back wake IRQ/runtime-PM balancing. | Included at orders 40–41; compile and exercise wake/recovery paths on hardware. |
| Hamoa USB NoC | SP12 enables `usb_1_ss0`; Hamoa used USB AHB clocks instead of north/south aggregate-NoC AXI clocks. | Required DTS correction included at order 42; verify DT and qualify DMA with sibling controllers suspended. |
| WCN7850 Bluetooth | SP12 enables WCN7850 at 3.2 Mbaud; baseline QCA UART handling can misconsume its baud-rate completion event. | Required HCI event fix included at order 48; qualify radio operation on hardware. |
| Hamoa Iris/video | Iris was enabled but lacked Hamoa context-bank devices and per-buffer IOMMU routing. | Required EL1 context-bank set included at orders 43–47. EL2-only 0006/0007/0009 remain conditional and need a separate 7.3.1 rebase if that boot path is selected. |
| Suspend policy and timer | The Qualcomm timer candidate applies and is included; SP12 deep-residency telemetry is absent. The proposed SS1 pair still has a `system-state`/`system-sleep-only` mismatch and a binding-schema gap. | Timer fix included at order 49 for deep-suspend readiness; compile and qualify on hardware. Keep the inconsistent SS1 pair out until property/parser/schema and residency evidence are resolved. |
| Camera closure | The original chain includes CAMSS, CCI, CSI D-PHY/provider, sensors, clocks, bindings, and SP12 board wiring. Source-level review confirms the expected Hamoa/Purwa/X1P nodes and drivers; config, DT, and module/package checks passed on final37. | Preserve the current camera chain. Physical enumeration, capture, and privacy-LED operation remain unqualified. |

Patch source identities, base-tree comparisons, and replay detail are in the
[coverage-resolution report](archive/validation/sp12-r2-source-coverage-20261113.md)
and [49-entry replay](archive/validation/artifacts/sp12-r2-source-coverage-20261113/integrated-49-patch-replay.json).
The old final37 package and installer evidence remains valid for its recorded
identities only; it does not contain the new feature patches.

### 2026-11-13 Iris binding closure — active 51-entry replay and DT checks passed

The 49-entry predecessor carried the Iris context-bank driver and Hamoa DTS
updates but missed the shared Venus and SM8550 Iris binding patches. Those two
original v6 patches are now ordered after `iommu-ranges` and before the Iris
driver changes. The final 51-entry manifest passed two complete replays from
the verified signed source archive; both produced tree digest
`192c5187bca08d67cb167cf7be77996fdde7f4c3717e19bb200775bf48a161fb`.
Targeted binding checks and YAML lint passed, and the freshly compiled SP12 DTB
passed schema validation with zero diagnostics. The clean package build and
all runtime qualification remain open. Full hashes and command results are in
the [51-entry validation report](archive/validation/sp12-r2-source-dt-schema-validation-20261113.md).

Use the authenticated CachyOS 7.3.1 base without an unrelated kernel upgrade.
Freeze the overlay at `952f769e1b45f07302d69992d19e5874ee77737` and audit
history over `ed20a9946e0136485bbac067e72100b84a0865fd^..952f769e1b45f07302d69992d19e5874ee77737`.
The patch/source coverage, superseded-revision review, rebases, exact provenance
and repeated sequential applicability are recorded in the r2 manifests and
evidence links above. Preserve the authenticated 7.3.1 base, required camera
closure, SP12 suspend adaptation, and ordered RPMB lifetime repair in any
further candidate rebuild. Do not promote a package/media candidate until its
identities and complete contents pass the package and VM gates.

Use one authoritative identity for preparation, build, package verification,
installer defaults, and boot configuration:

- kernel release `7.3.1-psycachy-sp121-r2`
- Debian version `7.3.1-1psycachy2`
- image and headers package names derived from that release

Replace fixed patch-count assumptions with ordered, uniquely identified
manifest entries protected by the pinned manifest digest. Build Image, EFI
image, modules, DTBs, and headers together. Refresh package, source-tree,
resolved-config, signing-certificate, payload, DTB, bundle, and ISO pins as one
candidate set, retaining the current v4 artifacts separately. Config and
package audits must require the camera/PHY/media drivers and their dependency
closure and verify module contents and release identities.

Add root DT property `psycachy,dtb-build-id` from a canonical pre-build
input/config manifest. Record it beside the packaged DTB hash and verify the
runtime property and patch-critical tree properties. This proves intended
tree identity; it does not prove raw in-memory DTB byte equality.

**Acceptance:** complete reviewed source coverage and provenance record;
focused negative tests for missing/reordered inputs, package identity mismatch,
missing camera dependencies, mixed payloads, and stale DT build IDs; successful
module/content and package identity checks; full ARM64 package build and
candidate ISO verification; then the separate VM and hardware gates in the
ship checklist. The lead owns architecture, shared interfaces, integration,
and checklist edits. Code/evidence subtasks need named owners, isolated work
directories, exact input identities, resource budgets, and stop conditions.
Do not begin the full build until the 80 GiB capacity gate is met.

### I-2: Diagnose the ARM64 graphical installer handoff

**State:** The ARM64 v3 installer ran through package configuration and
installed the pinned kernel pair, then failed in its late command because the
packaged DTB was under `/usr/lib/linux-image-$release/qcom/` while the boot-sync
helper expected `/boot/dtb-$release`. The installer now stages that exact DTB
to `/boot` and refuses to overwrite a different existing payload. ARM64
candidate v4 was rebuilt from the verified base and pinned pair; its signed
source, 120-package closure, EFI/live payload, UEFI boot metadata, and embedded
installer match are verified. Its SHA-256 is
`7669c1bcfeccffb9b86af2958ae5607cac9dc5b55b3fa77e467b304f7143af27`. A prior
SP12 QEMU 11.1.3 VM reached the target-only selector and passed the safe cancel
path; it did not complete an install. The v3 VM stopped before erase
confirmation and made zero target writes. The fresh local v4 install on
`cs-b550i-1` reached the installer’s “Ubuntu 26.10 is installed and ready to use”
screen. At 17:49 UTC, QMP recorded 12,178,290,176 target write bytes, zero
failed writes/flushes, and zero protected-disk writes. Both QCOW2 postchecks,
the protected full-image hash, and sentinel reads passed. At the user's
request, the VM stopped before restart, media removal, and installed-target
UEFI boot. The target QCOW2 and UEFI variables are retained in ignored
`output/` for possible continuation; package and boot checks remain open.

Two later SP12 native v4 attempts used QEMU 11.1.3 TCG. Attempt 1's 2D display
went black after Linux reached GDM. Attempt 2 used virtio-gpu-gl-pci/EGL on the
Adreno render node, displayed Linux console output, then the wrapper reported
SIGBUS before the selector. Both attempts wrote zero target/protected bytes
and passed protected hash/sentinel checks. The second runner's termination
cause is unclassified. SP12 has no `/dev/kvm` and does not set
`CONFIG_KVM_ARM_HOST`. Those installer VMs and their run-owned inhibitors are
stopped.
See the [stop handoff](archive/validation/unattended-luna-stop-handoff-20261112.md)
for exact run directories and manifests.

A separate disposable COW review found that the installed GRUB configuration
does not list the SP12 candidate. A one-time GRUB CLI boot selected
`7.3.1-psycachy-sp121`. A verbose diagnostic shows both tmpfiles services,
root fsck, `/sysroot` mount, and initrd switch-root succeeded; host startup
continued into AppArmor/rfkill before the 180-second timeout. A separate
600-second COW boot reached a candidate root shell, fsck passed, and the ESP
mounted from `/dev/vda1`. A same-version package reinstall reached dracut
initramfs generation, then timed out before dpkg/hook completion. The generic
`7.3.0-9-generic` entry reached userspace. Version-upgrade, interrupted-update,
and rollback checks remain open. The retained target and firmware-variable
hashes remained unchanged; exact evidence is in
`archive/validation/artifacts/arm64-v4-reinstall-diagnostics-20261116/vm-package-reinstall-20261112/pinned-kernel-review.txt`.
A separate 1,200-second reinstall remained active in dracut at timeout
(194 MiB / 3,901 staged files; the installed initrd was unchanged at the last
sample). This shows slow active work but does not establish dpkg or boot-sync
hook completion; package after-state and interruption recovery remain
unverified. Its disposable overlay passed `qemu-img check`, and retained
target/UEFI state remained unchanged. Review:
`archive/validation/artifacts/arm64-v4-reinstall-diagnostics-20261116/vm-package-reinstall-20261112/attempt7-long-reinstall/reinstall-review.txt`.
Attempt-6 debug-shell review SHA-256 is
`01f651affddbd46002d3d4dd08def6e6b053ea4e256512d5bfcb8592d8ddee9a`; its
serial log SHA-256 is
`a52696051c39ec8d00df1c6b1a0cae93352168a7970f229fcce2a275664a5bc9`.

The earlier serial and VNC evidence shows SP12's system QEMU 11.0.3 reaching
GDM and turning black on the login transition. The later local 11.1.3 run
showed that QMP Return activates the live-session screen and Alt+Tab reveals
the selector behind Welcome to Ubuntu. A combined QMP pointer command did not
toggle its radio; separate timed move/down/up events did. The pin-path,
symlink-staging, and DTB-staging failures and fixes are recorded in the
[QEMU install follow-up](archive/validation/unattended-luna-phase1-installers-phase2-20261111.md#2026-11-12-arm64-v3-installer-dtb-path-failure-and-v4-retry).
Do not treat the corrected candidate lifecycle as complete until its offline
install, package hooks, and boot without media pass.

**Done when:** the reproducible ISO-side cause is fixed, the offline
installation and package hooks pass in a disposable VM, and the installed
target boots through UEFI with installation media removed. Keep generic QEMU
results separate from Surface hardware qualification.

### I-3: Repair UFS RPMB registration and lifetime safely

**State:** Physical failure reproduced; the adapted three-patch source repair
is pinned and compiled into the refreshed ARM64 module configuration. The exact
QEMU RPMB series and its two prerequisite series apply cleanly on a pinned
base; an isolated build passed all 32 UFS QOS tests. The first built-in compile
was terminated by SSH hangup during unrelated Kbuild objects; its incremental
resume completed successfully in `luna-rpmb-builtin-resume-20261112.service`.
It produced `Image`, `vmlinux`, `vmlinuz.efi`, and 8,484 modules with
`CONFIG_RPMB=y`; the build manifest is
`output/.unattended-luna-20261111210910Z/qemu-hosting/kernel-rpmb-validation-20261112/builtin-build-manifest.json`.
The separate diagnostic KASAN/lockdep compile completed successfully in
`luna-rpmb-diagnostic-resume-20261112.service`. The controlled no-UFS negative
case returned `-ENODEV`; the final Linux-driver guest run passed 256 concurrent
read-counter requests, recovery after a failed abort/HCE reset, and UFS driver
unbind with a held RPMB request. All four workers observed `-ENODEV`, with no
KASAN or circular-lock warning during that lifecycle. A single scheduler RCU
warning occurred before userspace init; the separate PCIe hotplug experiment
reported a `pciehp` lock-order warning and did not complete. These are
QEMU-only driver results. Physical exact-candidate qualification remains open.
See the [guest lifecycle evidence](../output/.unattended-luna-20261111210910Z/qemu-hosting/kernel-rpmb-validation-20261112/guest-lifecycle-attempts/driver-lifecycle-summary.md).

SP12 logs report that ufs_rpmb0 cannot be added to the unregistered
ufs_rpmb bus. The authenticated source assigns that bus in
drivers/ufs/core/ufs-rpmb.c but contains no registration call. Do not fix this
by registering the bus alone or by only clearing dev.bus: once RPMB devices
register, the current devm allocation and unpinned SCSI WLUN leave a request
versus host-removal use-after-free risk. The reviewed upstream v5 series
combines RPMB-core request serialization, UFS device lifetime handling, and
dropping the unused bus in that order. The adapted series is included in the
pinned SP12 source inputs and compiled into the current ARM64 package pair.
The image/headers pair and target bundle verify against the refreshed pin.
Generic QEMU validates boot, module-signature policy, lockdown, unprivileged
BPF, and kexec denial, but does not exercise the repaired Linux UFS RPMB driver.
The isolated patched QEMU model now supports the relevant RPMB command paths;
its supplied qtests pass, including test-only key programming and writes.
Those qtests validate the device model and do not replace Linux-driver guest
request, concurrency, or teardown coverage. See the dated [takeover report](archive/validation/luna-takeover-20261112.md)
for the exact base, prerequisite series, patch hashes, and build evidence.

**Done when:** module and built-in configurations compile; a disposable UFS
fixture passes registration, read-only requests, concurrent requests, and
teardown checks under KASAN/locking diagnostics; and the exact rebuilt
package passes target-specific physical qualification without RPMB
program-key or write-data operations. Keep Phase 1 blocked until then.

## Recorded decision; no route changes

### Recovery-panel route

The route is retired from supported recovery because its active EFI chain
remains unidentified and its ESP initrd differs from the installed initrd.
Its files and firmware entries remain unchanged. The documented manual rescue
path is the supported recovery procedure.

## Already implemented; avoid duplicate work

- AMD64 and ARM64 ISO builders, pinned inputs, offline package checks, and
  installer payloads are present. Refreshed local VM-test ISO candidates have
  passed source, closure, EFI/live payload, and manifest verification.
- Phase 1 policy fragments, audits, AMD64 and ARM64 candidate package pins,
  and generic-QEMU runtime policy probes are implemented. The rebuilt ISO and
  physical target gates remain in the ship checklist.
- The RPMB source repair is pinned and compiled into the refreshed SP12
  candidate; module and built-in configurations compile, and the disposable
  Linux-driver UFS fixture passes read-only counter, concurrency, reset, and
  driver-unbind lifecycle checks. Physical exact-candidate qualification
  remains open in I-3.
- The 20-operation editor smoke passes twice on both desktops from fresh
  fixtures with matching saved-document hashes. Timed Phase 2 trials remain
  open in the ship checklist.
- SP12 boot-sync and restore helpers flush staged payloads, preserve the
  invalid marker across interrupted promotion, and pass focused tests. Exact
  FAT metadata-sector EIO positive controls pass. One guest allocation-metadata
  EIO during staged `vmlinuz.new` flush preserved active hashes and marker;
  a write-throttled success update also passed. One exact-sector delayed-write
  positive control and one delayed real-helper success path were reported under
  QEMU 11.1.3. All 49 files in the SP12 runtime-evidence manifest are now
  transferred and hash-verified locally. Mapping the pre-run FAT seed confirms
  first-free-cluster FAT sectors 81/2098, data sector 10341, and free directory
  slot sector 4067. Generic ARM64 UEFI selected the marker-present test loader
  and halted on marker absence. A simulated interruption after the first
  payload promotion left a mixed kernel/initrd
  state without a marker; read-only fsck reported the dirty volume, and fresh
  UEFI selection halted at the marker guard before the candidate kernel branch.
  The 2026-11-16 focused test run passed 48 temporary-file simulations covering
  stage/flush, marker, promotion, recovery rotation, restore, and retry. The
  historical FAT evidence includes exact-sector positive controls and one
  passing guest allocation-metadata EIO during staged flush; other fault points
  remain incomplete/inconclusive. Surface DTB selection and physical
  power-loss safety remain unqualified.
  See the earlier [FAT matrix](archive/validation/unattended-luna-phase1-installers-phase2-20261111.md#fat-fault-qualification--partial-guest-coverage-matrix-open)
  and the [QEMU continuation](archive/validation/unattended-luna-phase1-installers-phase2-20261111.md#2026-11-12-qemu-update-and-arm64-installer-retry).
- `tools/phase2-kernel-trial.py` consumes existing pins and records exact
  candidate/fallback identities. It refuses unresolved Secure Boot trust,
  package errors, ambiguous GRUB entries, changed fallback state, and a backup
  manifest or volume without reviewed identities. Unit tests pass; an
  end-to-end VM lifecycle and physical use remain open in the ship checklist.
- Refreshed AMD64 and ARM64 package pairs and local ISO candidates verify
  against their pins. B550I's owner kernel and DKMS certificates match their
  reviewed fingerprints and are enrolled. The pinned package module signer is
  a separate identity; the exact image package sets
  `CONFIG_MODULE_SIG_FORCE=y`. Candidate runtime must also prove
  `module.sig_enforce=Y` under integrity lockdown. The AMD64 ISO and trial
  lifecycle remain open. See the dated [takeover report](archive/validation/luna-takeover-20261112.md)
  for the exact package configuration and evidence.
- `iso/build-sp12-live.py` now loads GRUB's available `fdt.mod` before its
  pinned Surface DTB command and audits both in the final ISO. The corrected
  local-only image built and passed its base, package, support-file, GRUB, GPT,
  installer-layer, and physical ESP/NVRAM checks. The USB rewrite is complete
  with exact direct-I/O readback on Apple HDD serial `TNS519GY1G6JGG` (image
  SHA-256
  `e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36`). The
  corrected one-time boot reaches the live session on the SP12, and the user
  reports speaker sound works there. Both WSA884x SoundWire endpoints were
  `Attached`. The staged DTB hash matches its pin, but `/sys/firmware/fdt` is
  absent, so the exact DTB passed to Linux remains unverified. The user reports
  that the read-only live recovery inspection closed the terminal without
  visible output; that gate remains open. A logged, guarded retry is documented
  in the [live qualification procedure](archive/validation/sp12-live-qualification-20261112.md).
  The installed system's speakers remain silent, and its previous capture
  showed both endpoints `UNATTACHED`, interrupt value `2048` (`AUTO_ENUM_FAILED`),
  a bus clash, FIFO overflow, and ASoC `-ENODATA` playback/resume errors. This
  evidence indicates a difference between installed and corrected live audio
  state but does not isolate the cause. See the live-media status in the ship
  checklist and the audio evidence packet.
  The 2026-11-12 speaker pass was not reproduced in a follow-on live session
  on 2026-11-16: PipeWire exposed the speaker sink, but the user reported no
  audible output. Treat built-in speaker playback as unqualified pending
  diagnosis; see the [2026-11-16 hardware check](archive/validation/sp12-live-hardware-check-20261116.md).
  The 2026-11-18 follow-up again found no audible speaker output, and GNOME
  Sound Settings exposed no microphone input despite an earlier PipeWire
  snapshot listing an internal source. The visible video nodes were identified
  as Iris decoder/encoder nodes, not capture devices; V4L2/media tools were
  unavailable, GStreamer found no source, and kernel logs included a CSI lane
  error and Iris firmware initialization failures. No mixer or camera-graph
  changes are justified without a reproduced route or media-graph diagnosis.
  See the [sanitized follow-up report](archive/validation/sp12-live-hardware-check-20261118.md).
- A corrected UEFI rescue VM used a separate rescue root, restored a disposable
  target clone, and verified exact payload hashes. Fresh AAVMF variables and
  one-time BootNext reached the intended loader. A 2026-11-14 COW follow-up
  captured GRUB 2.14 and read the restored root's generated config; its hidden
  default selects kernel/initrd/DTB `7.3.0-10-generic`. The corrected-stub
  automatic probe stayed serial-silent after UEFI started the loader, so
  execution of that entry remains unproved. A separate generic EFI/ACPI control
  manually loaded the same kernel/initrd without the DTB, mounted the restored
  root, ESP, and data volume, reached `getty.target` and the serial login
  prompt, then shut down cleanly. No account login, `dpkg --audit`, or in-guest
  restored-payload comparison was performed. All six new root/data COWs passed
  `qemu-img check`; backing sources and physical recovery state remained
  unchanged. See the
  [generic-control report](archive/validation/artifacts/sp12-restored-target-generic-control-20261114/report.md).
- The Phase 2 UPS sampler and fixed editor/video inputs already exist. Their
  measurement and workload validation remains in the ship checklist.

When a queue item closes, update the checklist and move its evidence into the
archive. Do not add an item here solely because a validation task is pending.
