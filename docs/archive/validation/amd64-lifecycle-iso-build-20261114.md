# AMD64 lifecycle ISO build record

**Recorded:** 2026-11-14 03:42 UTC  
**Updated:** 2026-11-14 04:11 UTC (bounded boot evidence and review appended)  
**Baseline:** `bb3fc379862271bcfdd8715564990f1073b7df83`  
**Status:** Private candidate ISO built and independently reviewed at the file/payload level; install and lifecycle runtime qualification remain open.

## Candidate identity

- ISO: `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso`
- Size: 8,052,277,248 bytes
- SHA-256: `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`
- Output `SHA256SUMS` verifies the ISO hash. Build log SHA-256:
  `a03563b6d1fc7d21efe1f411679776abcee753ed58e2ff6d3f90e7f2e5aef0f0`.
- Build-time manifest SHA-256:
  `94be983994c7155a764f7cdf434983193055f316ff222f11902232585bf65d7b`.

The ISO was built from the Canonical-signed Ubuntu 26.10 AMD64 base,
`output/.phase1-closeout-20261110T192001-0700/amd64-build` (the exact pair in
the active AMD64 kernel pin), and the retained local offline repository
`output/.unattended-luna-20261111135015Z/amd64-offline-repo`. The build ran
inside an unprivileged user namespace; its root-only package checks ran as
namespace root without host-root access. The build log reports 280 Ubuntu
packages checked against authenticated archive indexes. The repository's 282
packages include those 280 plus the two pinned PsyCachy kernel packages.

## Review and verification

The independent [artifact review](artifacts/amd64-lifecycle-iso-build-20261114/independent-review/review.md)
found no embedded payload mismatch. Its SHA-256 is
`54e2aaa157ce0e033e5e63d384a3d164c2ee3c208388d465d0089b2dd7076cf5`; the
complete 190 MiB review bundle is checksummed in that directory.

The review independently checked the ISO hash/size, all 316 source-hash rows
in the build manifest, all 282 offline repository package hashes, the signed
base ISO, the embedded lifecycle scripts, selected autoinstall and GRUB
content, the exact kernel pin and image/header packages. The embedded
`phase2-kernel-trial.py` hash is
`35e0f892caff684a704b95567b514fb0ea4dd6b395efa068a5337fd2dbb79372` and its
extracted bytes match the source.

The build also reports that the signed base EFI files and casper kernel are
unchanged and that the UEFI boot record is present. Build-time checks passed.
The log contains non-fatal APT cache cleanup and translation-metadata
warnings.

The original build-time manifest listed the trial helper as modified but did
not include its hash. The [manifest supplement](../../../output/amd64-iso-lifecycle-20261114-build2/manifest-supplement.txt)
binds the independently extracted helper hash to this exact ISO and leaves the
original build-time manifest and ISO checksum file unchanged. `iso/build.sh`
now includes that helper in future manifests; the change is covered by a
regression test. The independent reviewer accepted the fix and confirmed no
ISO rebuild is needed because the change affects only external manifest
generation and the script is not embedded in the ISO. Focused tests now pass
(38 kernel-trial tests), `bash -n iso/build.sh`, `git diff --check`, and the
full static suite pass (71 recorded configuration changes; root-only
`mokutil` check skipped).

The manifest-fix review is archived at
[manifest-fix-review.md](artifacts/amd64-lifecycle-iso-build-20261114/manifest-fix-review.md)
(SHA-256 `d88f43586c79f70f473296b43eae4c08618f28b58a65b713de5367f8f7b709d6`).

## Qualification boundary

A bounded no-network UEFI/KVM boot smoke on 2026-11-14 used a fresh disposable
target COW and a read-only sentinel. The exact ISO reached the Ubuntu live
desktop's guarded disk selector, displaying only the disposable target serial
`psycachy-linux`. The VM stopped there without selecting a disk or proceeding
to first-install/replacement mode or the `ERASE` confirmation. Both QCOWs
passed `qemu-img check`, the sentinel hash/read verification passed, and the
target COW map has no present guest-data blocks. The run used the non-Secure
Boot OVMF firmware configuration. A GRUB warning about `grub_platform` also
appears in the signed base ISO's own GRUB config and did not prevent this boot.
See the separate [live-boot record](amd64-lifecycle-iso-liveboot-20261114.md)
and its checksummed [evidence bundle](artifacts/amd64-lifecycle-iso-liveboot-20261114/).
The outer evidence-manifest (`SHA256SUMS`) SHA-256 is
`fb43243df0f109fd53c390bc6d6c4fe412aac2561704607dab56f95e722d8de9`. An
independent reviewer approved the no-write and storage claims; the review is
at [independent-review/review.md](artifacts/amd64-lifecycle-iso-liveboot-20261114/independent-review/review.md)
(SHA-256 `d5ce7d350376249450f1769b3054240af95f55ef6264e01eab7ce1396c5427eb`;
separate checksum-manifest SHA-256 `a7a205529a09b65318b9e7917fe352104a3df3b710d44c8d564f3568f649e72d`).
The reviewer notes the wrapper exit status is recorded but not independently
verifiable from raw retained QEMU output.

No VM installation, installed-system login, activation, candidate
acknowledgement, promotion, fallback boot, rollback, Secure Boot enrollment,
NVIDIA runtime, or physical B550I test was performed. The boot smoke reached
the auto-logged-in live desktop and adds evidence only through the guarded disk
selector; it does not qualify the ISO for promotion or hardware use.

An earlier preflight attempt stopped on a non-pinned kernel package directory;
a second attempt correctly rejected a stale offline repository kernel pair.
Neither produced an ISO. Their retained logs remain under
`output/amd64-iso-lifecycle-20261114/`; the successful candidate and its
sidecars are under `output/amd64-iso-lifecycle-20261114-build2/`.
