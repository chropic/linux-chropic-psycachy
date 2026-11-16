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

The exact hash then completed a network-disabled Secure Boot QEMU install on a
disposable 64 GiB `/dev/vda` (`psycachy-linux`) with a read-only sentinel. The
installer completed after explicit `FIRST-INSTALL` and `ERASE` confirmations;
the completion snapshot showed 17,259,126,272 target write bytes and zero
sentinel writes. `qemu-img check`, sentinel hash/pattern verification,
`dpkg --audit`, and `apt-get check` passed. The detached installed disk reached
GDM on generic fallback `7.3.0-10-generic`. Secure Boot, lockdown, and module
signature enforcement were active; the pinned kernel and NVIDIA DKMS module
were signed, but neither per-install key was enrolled. The installer kept the
generic kernel as default pending activation, so candidate boot was not
attempted. The read-only Secure Boot helper reported
the missing enrollment; no MOK/firmware trust change was made.

The same ISO was re-entered with the installed target and sentinel read-only
and reached the default Try/Rescue language screen without an autoinstall
failure. That re-entry used a fresh disposable OVMF variables copy, so it does
not qualify physical BootOrder or one-time-menu behavior. The installed QEMU
VMs are shut down; the previously noted PID 270613 was absent at closeout. The
current fixture is retained at
`/var/tmp/amd64-perinstall-current-20261116/`; its private QA password remains
outside the repository. A live-session `sudo -n reboot` attempt displayed
`KERNEL PANIC ... Attempted to kill init! exitcode=0x0000000b`; after explicit
hard-disk selection the installed disk booted to GDM. Investigate that live
reboot anomaly at the next attended window. See the
[AMD64 report](amd64-perinstall-guarded-rescue-20261116.md) and
[evidence bundle](artifacts/amd64-perinstall-guarded-rescue-20261116/).

## Remaining work, in order

1. **Finish SP12 live-session checks at the next attended window.** Record
   display/input, USB, Wi-Fi, Bluetooth, audio, camera, storage health, and
   suspend/resume. Run only the approved RPMB registration/health checks in
   read-only mode; do not provision keys or write RPMB data. Copy the complete
   evidence set to B550I and verify hashes before ending the live session.
   The current pasted capture is archived locally; an SP12-to-B550I transfer
   was not performed or verified.
2. **Finish AMD64 candidate boot and lifecycle qualification.** Candidate:
   8,052,277,248 bytes, SHA-256
   `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc`.
   Exact-hash install, detached fallback boot, package health, and read-only
   repeat-media path passed in QEMU. On the physical B550I, install to a fresh
   serial-identified disposable target, enroll the new per-install kernel and
   DKMS MOK keys, boot the pinned kernel, and verify the RTX 4070 driver,
   graphics, networking, audio, suspend/resume, update, and fallback. Then run
   PREPARE, candidate boot, acknowledgement/refusal, promotion guard, timeout
   rollback, explicit rollback, replacement mode, tamper refusal, and saved
   generic fallback recovery. Promotion requires complete hardware
   attestation. Stage the ISO on Ventoy only with a file-level checkpoint and
   full read-back hash; no AMD64 replacement is currently staged.
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

- Preserve at least 80 GiB free; 164.47 GiB was free at the end of the AMD64
  run. Run one heavy job at a time.
- No QEMU VM or monitor was active at closeout. The exact-hash AMD64 fixture
  is retained under `/var/tmp/amd64-perinstall-current-20261116/` for later
  lifecycle work. The previous-image PID 270613 was absent. The ARM64 r1
  target fixture remains for the update test; remove fixtures only after
  their dependent tests finish.
- Do not copy the disposable VM's private MOK keys to the B550I. A physical
  installation generates its own per-install keys, which must be enrolled
  through the attended MOK manager. Do not change persistent firmware order,
  provision RPMB, write RPMB data, or test internal storage.
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
