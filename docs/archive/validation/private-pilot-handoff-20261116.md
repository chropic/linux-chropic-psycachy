# Private-pilot handoff — 2026-11-16

**Resume point:** storage cleanup is complete, the current AMD64 ISO build
finished, and SP12 has now reached a live session from the staged final51
combined media. The two pilots are not qualified for installation or
promotion. After the diagnostics handoff, the user authorized software-only
follow-up while away from the B550I; the work completed and current blocker
are recorded below. No physical pilot operation was started in that
continuation.

## Newly verified on SP12

The user-provided capture is stored at
[`artifacts/sp12-live-boot-20261116/diagnostics.txt`](artifacts/sp12-live-boot-20261116/diagnostics.txt)
and passes its adjacent `SHA256SUMS` check. It reports:

- Kernel `7.3.1-psycachy-sp121-r2`.
- Runtime DTB ID `sha256:43e6fa05d5ee85e49bfc1d295f0ce77bcba55e1366b39f2cc6240d69783249d0`, matching the final51 pin.
- Ventoy mounted read-only at `/cdrom`; read-only `/rofs`; writable live `/cow` overlay.
- A 476.7 GiB `sda` disk with vfat and ext4 partitions present but no mount points. Use the recorded serial only as evidence for this boot; identify devices again by model, serial, size, contents, and mount state before any future write.

The staged combined ISO is 5,500,940,288 bytes, SHA-256
`56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`.
Its full Ventoy destination read-back passed earlier. The current diagnostic
does not contain an in-session ISO hash, write counters, or a firmware-variable
comparison. It establishes live startup and kernel/DTB identity, not the full
hardware matrix or installed-system qualification.

## AMD64 software-only follow-up

The current AMD64 candidate remains 8,052,277,248 bytes with SHA-256
`908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`. Its
source changes were committed as `0ea566ecabc3849b73d9f5439f907f21d6e80072`.
The build manifest names base revision
`4bf0407c33024afea51da24bcae5e5f688a79da4` with a dirty tree; a post-commit
comparison verified all 36 in-repository source hashes against the committed
checkout. The ISO itself was not rebuilt. The full `tests/static-check.sh`
suite passed; its root-only `mokutil` check was skipped.

No fresh exact-hash install or lifecycle VM run was started. The old QEMU
process (PID 270613) is still using the previous candidate and disposable
fixture under `/var/tmp/amd64-perinstall-bind-20261115/`, stopped at a UEFI/MOK
screen. Its monitor was not controllable from the current shell, so the VM and
its disks were left untouched and no second heavy QEMU run was launched. The
SP12 SSH check also timed out. Resume by releasing the old VM from its
originating terminal and shutting it down cleanly; then run the current ISO's
install, detached boot, repeat-media, and lifecycle cases. Hardware checks
still require physical B550I/SP12 access.

## Remaining work, in order

1. **Finish SP12 live-session checks at the next attended window.** Record
   display/input, USB, Wi-Fi, Bluetooth, audio, camera, storage health, and
   suspend/resume. Run only the approved RPMB registration/health checks in
   read-only mode; do not provision keys or write RPMB data. Copy the complete
   evidence set to B550I and verify hashes before ending the live session.
   The current pasted capture is archived locally; an SP12-to-B550I transfer
   was not performed or verified.
2. **Complete AMD64 software qualification against the exact current hash.**
   Candidate: 8,052,277,248 bytes, SHA-256
   `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`.
   It is not staged on Ventoy. Still required: fresh install, detached boot,
   repeat-media reproduction with installer logs/write counters/package state
   and `dpkg --audit`, then prepare/boot/acknowledge/promote, timeout and
   explicit rollback, replacement mode, tamper refusals, and fallback
   preservation. Recheck Secure Boot, lockdown, module trust, DKMS, NVIDIA,
   networking, audio, and suspend/resume on the B550I. Promotion requires
   complete hardware attestation.
3. **Complete the ARM64 changed-release update on a fresh overlay.** The prior
   attempt reached a login prompt but did not run `dpkg` or hooks. An explicitly
   authorized disposable credential/seed is required. Observe package hooks,
   dracut, matched kernel/module/DTB/initramfs staging, fallback preservation,
   media-free boot, interruption recovery, and rollback. The retained r1
   target is at
   `output/.unattended-luna-20261111210910Z/qemu-hosting/csb550i-1-arm64-v4-attempt8/vm/target.qcow2`;
   use a fresh child overlay and copied UEFI variables.
4. **Close the FAT/recovery interruption matrix.** Cover staging/flush, marker
   transitions, each payload promotion, recovery rotation, and restore
   interruptions. Retain fault-overlap evidence, payload/marker checks,
   read-only filesystem checks, loader-selection results, and successful
   recovery/retry evidence. Simulated power loss does not qualify physical
   power-loss safety.
5. **Run physical installed-system rehearsals only after the software gates.**
   B550I requires a fresh serial-bound Apple HDD checkpoint and separate
   artifact/hash approval; verify Secure Boot, NVIDIA/DKMS, update, fallback,
   promotion review, and rollback. SP12 external installation also needs its
   own fresh target/artifact checkpoint and explicit approval. Keep internal
   disks and protected media out of installer harnesses.
6. **Independent review and release closeout.** Reconcile the qualification
   ledger, implementation queue, and ship checklist after exact-hash and
   hardware results. Both pilots need passing software, recovery, and
   exact-hardware gates. The public phase remains later: six-scenario
   performance comparisons and redistribution/attribution review.

## Working constraints and retained state

- Preserve at least 80 GiB free; the latest cleanup report records about
  177.87 GiB free. Run one heavy job at a time.
- Do not modify the active AMD64 VM until its monitor client is released and
  QEMU has shut down cleanly. QEMU PID 270613 uses the older image; monitor
  client PID 276667 is still connected. The ARM64 r1 target fixture remains
  for the update test. Remove both fixtures after their dependent tests finish.
- The matching final51 private signing key has not yet been confirmed in the
  local checkout; verify it from the authenticated SP12 build when reachable.
- No code change follows from the boot diagnostics: the runtime kernel and DTB
  match the pin. Change code only if a remaining reproducer demonstrates a
  defect.
- No internal installation, persistent firmware-order change, RPMB
  provisioning/write, or deliberate physical power-cut test is authorized by
  this handoff.

See the [qualification ledger](../../PRIVATE-PILOT-QUALIFICATION.md),
[implementation queue](../../IMPLEMENTATION-QUEUE.md),
[ship checklist](../../SHIP-CHECKLIST.md), and
[current artifact keep list](current-artifact-keep-list-20261116.md).
