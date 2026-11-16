# AMD64 per-install signing and guarded Try/Rescue candidate — 2026-11-16

**Status:** Fresh candidate built and independently audited; its default
Try/Rescue path reached the live desktop in a network-disabled, diskless VM.
Fresh installation, repeat-media behavior, and the remaining activation
lifecycle still need exact-hash runs.

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
The static check's root-only `mokutil` probe was skipped.

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

This prior-image result gives a bounded timeout/fallback observation only.
The current candidate still needs a fresh exact-hash installation, detached
boot, repeat-media attempt with post-attempt package and write-extent audit,
candidate boot, acknowledgement/refusal gates, explicit rollback, replacement
mode and tamper-refusal checks. The old VM monitor is held by a stale client
in another terminal; work on that fixture is paused until its monitor is
released. NVIDIA-dependent promotion remains an exact-hardware B550I gate.

No ISO was staged on Ventoy, and no physical disk, internal storage, or host
firmware order was changed. At the end of this run `/` had
125,794,316,288 bytes free (117.15 GiB), above the 80 GiB reserve.
