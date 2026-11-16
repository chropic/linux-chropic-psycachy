# AMD64 per-install signing and guarded Try/Rescue candidate — 2026-11-16

**Status:** The 8,052,277,248-byte candidate was independently audited. Its
exact hash completed a network-disabled install on a disposable 64 GiB target,
booted the installed Ubuntu fallback to GDM, and re-entered the ISO through
the default Try/Rescue path with the installed target and sentinel read-only.
The guest package audit passed. Secure Boot was enabled, but neither
per-install owner key was enrolled, so the pinned kernel did not boot and the
activation lifecycle remains open. No Ventoy staging or physical hardware
operation occurred.

## Candidate identity

- ISO: `output/amd64-iso-lifecycle-20261116-perinstall-guarded-rescue/psycachy-ubuntu-26.10-desktop-amd64.iso`
- Size: 8,052,277,248 bytes.
- SHA-256: `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`.
- Adjacent ISO sidecar: `SHA256SUMS` verifies; sidecar SHA-256 is
  `9e400fe8a8339f5d54f913194d3849f235b2be50af1362ad8742c772f29ab4b6`.
- Build log SHA-256:
  `b141b742f7e017501bbfb31e4c6c55397a276e98b45616a5067d7827bbd23031`.
- Build manifest SHA-256:
  `7d78430bb9fc5cfd1a3f975efaf35b9c76ca0cfbeba11bbe2b14ccc4c2841b7b`.
- Independent review JSON SHA-256:
  `045844a8a90e4ffa640d8e281fc52bbcb8668c14c87b3dc6166f0cf473ec76bf`.

The earlier `20261115-guarded-rescue` output was dated before the per-install
certificate-binding change and contained older installer helper hashes. Its
ISO was checksum-verified and retired; its build log, manifest, and sidecar
remain. This new candidate combines the current certificate-binding and
guarded-menu source changes. The separately installed VM still uses the
previous `per-install-pin` image (SHA-256
`3c8d488be56c0b94e3a535c6fd3cfed9b84c55d65a41fc15056be43ffe1abb36`); its
lifecycle observations below do not qualify this new ISO.

## Inputs and build

The build ran as root in an unprivileged user namespace. It verified the
Canonical-signed Ubuntu 26.10 amd64v3 base ISO (SHA-256
`16c9d9122160d901c78d0528cad4556c778701039ea2879b89483d4fd0c0d10b`), the
exact `znver3` kernel pair, the offline repository sidecar, and 280 Ubuntu
packages against authenticated archive indexes. The kernel package hashes
were:

| Package | SHA-256 |
| --- | --- |
| `linux-headers-7.3.1-psycachy_7.3.1-1psycachy1_amd64.deb` | `cccd88818bdcbae2789d98725b754a9253744b42a2ec16458dbc0a424cb0b872` |
| `linux-image-7.3.1-psycachy_7.3.1-1psycachy1_amd64.deb` | `a3e89bb7091640abad457a55184555533a6cde72d6b79a78c97f1b25dc111fa6` |

Build command:

```sh
unshare --user --map-root-user -- bash iso/build.sh \
  output/iso-inputs-20261110/ubuntu-26.10-desktop-amd64v3.iso \
  output/.phase1-closeout-20261110T192001-0700/amd64-build \
  output/amd64-iso-lifecycle-20261116-perinstall-guarded-rescue \
  output/.unattended-luna-20261111135015Z/amd64-offline-repo
```

The manifest records source base revision
`4bf0407c33024afea51da24bcae5e5f688a79da4` and a dirty working tree. After
the build, the exact nine-file source and test change set used for this ISO
was committed as `0ea566ecabc3849b73d9f5439f907f21d6e80072`. A post-commit
comparison recomputed every one of the 36 in-repository source hashes in the
manifest against the checkout at that commit: all 36 matched. The ISO was not
rebuilt from a clean worktree; the hash comparison ties the recorded source
inputs to the committed content.

## Independent content review

The adjacent [review record](../../../output/amd64-iso-lifecycle-20261116-perinstall-guarded-rescue/independent-review.json)
records these checks:

- The ISO sidecar matches the full image. All 36 source-file hashes recorded
  by the build manifest match the current checkout.
- All 282 embedded repository package hashes match the embedded
  `SHA256SUMS`. The embedded pinned package pair matches the active kernel
  pin.
- All 13 installer and lifecycle helpers match the current source. The
  embedded kernel pin uses `certificate_binding: per-install` with empty
  source certificate hashes.
- The embedded GRUB menu matches a fresh transformation of the signed-base
  menu. “Try PsyCachy (live/rescue)” is the default; only the explicit guarded
  install entry adds `autoinstall` and points to
  `/cdrom/psycachy/autoinstall.yaml`.
- The three EFI boot files, casper live kernel, and raw UEFI El Torito image
  match the signed Ubuntu base. The raw UEFI image hash is
  `a581aa88b04c830922dff3ee5873918c89c80fe7db4c457ecc45314091e1a325`.

The source checks already run for this source state passed: 40 phase2 trial
tests, 6 GRUB-menu tests, 10 disk-selector tests, and `tests/static-check.sh`.
The static check's root-only `mokutil` probe was skipped. The full static
suite was rerun after the source commit and passed again.

## Exact-hash default boot smoke

The candidate booted with QEMU 11.0.3/KVM, q35, 2 vCPUs, 4 GiB RAM, UEFI
Microsoft-signed OVMF, no NIC, and no target or sentinel disks. GRUB displayed
the new menu and selected the first/default “Try PsyCachy (live/rescue)” entry.
The guest reached Ubuntu's live desktop and its initial language-choice
screen. The autoinstall failure dialog seen with the prior menu did not appear.
The VM was then stopped through its monitor; only the temporary OVMF variables
file was writable. This confirms the default live boot path, but it does not
test installation, repeat-media behavior, or writes to a disposable target.

Screenshots and checksums are retained beside the image:

- `evidence/default-grub-try-rescue.png`, SHA-256
  `2dbb52f2e4210e8bf0c4ba03779b35a3f7cfde54cf29a50fd95dfcfaa42207a1`.
- `evidence/try-rescue-live-desktop.png`, SHA-256
  `4851f4c71163959f3dc41f1f9b8312ba00d372fd71e8bffd907a23cd80f36ff8`.

## Exact-hash guarded installation

The test VM used QEMU 11.0.3/KVM, q35, 2 vCPUs, 4 GiB RAM, Microsoft-signed
OVMF with Secure Boot enabled, and no network. The writable target was a fresh
64 GiB sparse QCOW presented as `/dev/vda`, serial `psycachy-linux`. A separate
64 GiB QCOW sentinel (`psycachy-other`) remained read-only. Only `/dev/vda`
appeared in the disk selector. The successful attempt selected
`first-install`, entered `FIRST-INSTALL`, and then entered `ERASE` at the
explicit `/dev/vda` erase prompt. Two earlier incomplete confirmation attempts
failed closed before target writes.

The installer reached its completion screen. Its final log reports that the
PsyCachy packages were installed and Ubuntu remains the default pending
activation. At the completion screen QEMU block statistics showed
17,259,126,272 target write bytes, zero sentinel writes, and zero ISO writes.
The first-install write count is expected because the operator explicitly
confirmed the dedicated disposable target; the sentinel remained unchanged.
After the run, both QCOW images passed `qemu-img check`, and
`tests/iso-vm.sh verify-other` verified the sentinel SHA-256 and its 1 MiB
`0x5a` pattern.

## Detached first boot and installed guest state

With the installer ISO ejected, the installed disk booted to GDM and the QA
account reached the Ubuntu 26.10 first-run welcome screen. The selected
release was Ubuntu fallback `7.3.0-10-generic`; the installer intentionally
kept Ubuntu as the default pending activation, so the pinned
`7.3.1-psycachy` candidate was not attempted. `dpkg --audit` returned no entries,
and `sudo apt-get check` completed without a reported package error. DKMS
reported NVIDIA 615.71.09 installed for `7.3.0-10-generic`,
`7.3.0-9-generic`, and `7.3.1-psycachy`.

The guest reported Secure Boot enabled, lockdown `[integrity]`, and
`module_sig_enforce=Y`. `sbverify` confirmed the installed candidate kernel is
signed by `/CN=PsyCachy Secure Boot Kernel`; `modinfo` reported the candidate
NVIDIA module signer `PsyCachy DKMS Module Signing`. Both per-install owner
certificates were **not enrolled** according to `mokutil --test-key` and the
installed read-only Secure Boot helper. No MOK enrollment or firmware trust
change was performed. Candidate boot was not attempted because the installer
kept Ubuntu as the default pending activation. This does not qualify
candidate-kernel boot or NVIDIA trust. The virtio-GPU VM has no
RTX 4070, so NVIDIA module loading and graphics remain untested.

One live-session reboot attempt using `sudo -n reboot` displayed
`KERNEL PANIC ... Attempted to kill init! exitcode=0x0000000b`. The installed
system then booted to GDM after selecting the hard disk explicitly. This
panic was observed in the Try/Rescue live session, not during the detached
installed-system boot, and remains an item to check during the next attended
hardware rehearsal.

## Exact-hash repeat-media re-entry

The same ISO was booted again with the installed QCOW attached read-only, the
sentinel read-only, networking disabled, and a fresh disposable OVMF variables
copy. The default GRUB entry was “Try PsyCachy (live/rescue)”; the guest
reached Ubuntu's language screen without launching the installer or showing
the previous autoinstall failure. At the live screen QEMU reported zero writes
to both disks. The fresh OVMF copy makes this a repeat-media content/path
check, not a test of the installed VM's saved BootOrder or physical one-time
boot menu.

Evidence for the exact-hash install, guest state, and read-only repeat-media
run is collected in the
[evidence bundle](artifacts/amd64-perinstall-guarded-rescue-20261116/). Its
`SHA256SUMS` covers all retained screenshots and text records.

## Separate prior-image lifecycle observations

The previous `per-install-pin` image was installed to a disposable QCOW under
the Microsoft-signed OVMF profile, with networking disabled and a read-only
sentinel. Its Secure Boot helper reported Secure Boot enabled and both
per-install owner keys enrolled. `PREPARE` succeeded and scheduled the pinned
candidate once. The trial record later reached `timed_out` with
`Required signed module is not loaded: nvidia`; after that run the guest was
on Ubuntu fallback `7.3.0-10-generic`. The candidate release itself was not
captured, so this does not prove a candidate boot. The virtio-GPU VM has no
NVIDIA device. No acknowledgement or promotion was performed.

This prior-image result gives a bounded timeout/fallback observation only. For
the current candidate, exact-hash installation, detached generic-fallback
boot, package audit, signed-payload inspection, and read-only repeat-media
re-entry are now recorded above. Candidate-kernel boot, acknowledgement and
refusal gates, promotion, timeout and explicit rollback, replacement mode,
tamper refusal, and recovery of the saved generic fallback remain open. The
previously noted old VM PID 270613 was absent at closeout. NVIDIA-dependent
promotion remains an exact-hardware B550I gate.

## Remaining gates before private-pilot use

1. On the B550I, perform a fresh serial-bound installation to an approved
   disposable external target. The physical install creates its own
   per-install keys; do not transfer the disposable VM's private keys.
2. Enroll that install's kernel and DKMS module certificates through the
   physical MOK manager, then verify the exact pinned kernel boots with Secure
   Boot, lockdown, and module signature enforcement active.
3. Verify NVIDIA 615.71.09 loads on the RTX 4070, graphics and display work,
   and the full networking, audio, suspend/resume, update, fallback, and
   recovery checks pass.
4. Complete the exact candidate lifecycle: PREPARE, candidate boot,
   acknowledgement/refusal, promotion guard, timeout rollback, explicit
   rollback, replacement mode, tamper refusals, and saved generic fallback.
   Promotion must remain blocked without the B550I hardware attestation.
5. Stage this ISO on Ventoy only with a file-level checkpoint and full
   destination read-back hash, then one-time boot that exact image without
   changing persistent firmware order.
6. Complete the SP12 live-device/RPMB-read-only matrix and its separately
   checkpointed external-install/update work. FAT interruption recovery and
   public performance/redistribution closeout remain shared release gates.

No ISO was staged on Ventoy, and no physical disk, internal storage, or host
firmware order was changed. Only disposable OVMF variables files were used in
the VMs. The final free-space sample was 176,599,101,440 bytes (164.47 GiB),
above the 80 GiB reserve.
