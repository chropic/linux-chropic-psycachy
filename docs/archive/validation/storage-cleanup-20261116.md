# Storage cleanup and pilot handoff — 2026-11-16

## Result

The user's rerun of `sudo bash iso/build.sh` finished. The current AMD64 ISO
is `output/amd64-iso-lifecycle-20261116-perinstall-guarded-rescue/psycachy-ubuntu-26.10-desktop-amd64.iso`,
8,052,277,248 bytes, SHA-256
`908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`. Its
build log ends with `Built ...`; the adjacent `SHA256SUMS` matches. It remains
unstaged on Ventoy and still needs exact-hash installation, repeat-media, and
lifecycle qualification.

The final audit sample from `df -B1 /` reported **190,989,393,920 bytes
free** (177.87 GiB), **105,090,048,000 bytes (97.87 GiB) above** the 80 GiB
reserve. The final cleanup pass began at 178,686,480,384 bytes free and ended
at the value above, a measured net increase of 12,302,913,536 bytes (11.46
GiB). A prior
cleanup window measured 141,897,551,872 to 178,695,442,432 bytes free, a net
increase of 36,797,890,560 bytes. The combined net difference between the
first and final samples is 49,091,842,048 bytes; these are `df` snapshots, so
small changes from concurrent filesystem activity are included.

## Retired outputs

- Removed the superseded AMD64 V14 repository (282 packages, 1,753,378,740
  bytes) and the superseded ARM64 V4 ISO (5,074,714,624 bytes) plus its 120
  offline package payloads. The V4 checksum passed before removal. Compact
  manifests, hashes, build logs, and package inventories remain under
  `docs/archive/validation/artifacts/amd64-v14-repository-retired-20261116/`,
  `docs/archive/validation/artifacts/retired-package-generations-20261116/`,
  and `output/.unattended-luna-20261111210910Z/iso-arm64-refreshed-v4/`.
- Removed superseded package pairs, installer bundles, extracted audit copies,
  duplicate offline repositories, and completed `/var/tmp` capture trees
  after checking active processes, mounts, backing chains, pins, and unique
  source changes. Compact logs, selected screenshots, and checksums remain in
  the corresponding `docs/archive/validation/artifacts/` records.
- Removed duplicate generated build/cache trees after matching the retained
  authenticated source, signature, or package hashes. Four unique SP12 source
  deltas were retained as patches at
  `docs/archive/validation/artifacts/sp121-patch08-source-deltas-20261116/`.
- Retired old QEMU build outputs and binary archives; build metadata and hash
  lists remain in
  `docs/archive/validation/artifacts/qemu-build-retirement-20261116/`. The
  pending ARM64 reproducer's QEMU 11.1.3 binary and signed source inputs remain
  in the active QEMU support tree.
- Removed the obsolete 136,400,896-byte `kernel-package.iso` from a completed
  ARM64 reinstall diagnostic. Its SHA-256 is
  `853fe2250984d4618d1b4e86a070111e896786c1a92735c0d4f36dff9b9e5bb8`; it was
  not archived. The compact serial logs, review notes, and selected PNGs were
  moved and verified under
  `docs/archive/validation/artifacts/arm64-v4-reinstall-diagnostics-20261116/`.

## Retained inputs and temporary fixtures

- The current AMD64 candidate, both signed Ubuntu bases, the exact AMD64 and
  SP12 package pairs, offline repositories, authenticated SP12 source and
  signature, final51 support/recovery files, fallback trees, source changes,
  and signing material remain listed in the
  [current artifact keep list](current-artifact-keep-list-20261116.md).
- The SP12 update runner retains its QEMU 11.1.3 binary at
  `output/.unattended-luna-20261111210910Z/qemu-hosting/csb550i-1-arm64-installer-qemu113-20261112/qemu-system-aarch64`,
  SHA-256 `7719a165316bbbc568bc2de698b7ea9548cc369b1ced34e38e60da68d0ce62f2`,
  plus the signed source archive, detached signature, and release key under
  `output/.unattended-luna-20261111210910Z/qemu-hosting/source/`.
- Exactly two VM disk fixtures remain. The AMD64 fixture at
  `/var/tmp/amd64-perinstall-bind-20261115/` is still used by QEMU PID 270613
  with the older `per-install-pin` ISO; monitor client PID 276667 remains
  connected, so the VM and disk are untouched. The ARM64 r1 target at
  `output/.unattended-luna-20261111210910Z/qemu-hosting/csb550i-1-arm64-v4-attempt8/vm/target.qcow2`
  is a 64 GiB virtual QCOW2 with no backing file; its UEFI variables and
  read-only protected-disk sentinel remain beside it. No active QEMU process
  or dedicated mount references the ARM64 fixture.
- No additional task-specific guest target disks or per-run firmware-variable
  copies were found under `/tmp` or the output tree; bundled OVMF templates
  remain with the VM tools. The SP12 final51 combined ISO remains staged on
  Ventoy with its previous full read-back hash. The first one-time firmware
  boot menu did not list Ventoy; at the time of this cleanup snapshot, the
  image had not booted.

## Qualification boundary

Storage cleanup is complete and the 80 GiB reserve is maintained. The SP12
native live session and hardware checks, the AMD64 exact-hash software gates,
the ARM64 update run, and both physical pilots remain open. The initial
firmware observation is recorded in the
[SP12 boot report](sp12-firmware-boot-attempt-20261116.md). No
installation target or RPMB state was written as part of this cleanup.

## Follow-up later on 2026-11-16

After this cleanup snapshot, the user reported that the SP12 final51 combined
image booted to a live session. The supplied kernel/DTB and mount diagnostics
are archived at
[`artifacts/sp12-live-boot-20261116/diagnostics.txt`](artifacts/sp12-live-boot-20261116/diagnostics.txt).
This supersedes the earlier statement that the image had not booted. It does
not close the live-device matrix or installed-system gates; see the
[boot report](sp12-firmware-boot-attempt-20261116.md) and
[private-pilot handoff](private-pilot-handoff-20261116.md).
