# Supervised continuation report — 2026-11-15

**Prepared:** 2026-11-15 17:15 UTC / 10:15 MST

**Read-only machine snapshot:** 2026-11-15 17:03 UTC / 10:03 MST

**Primary checkout:** feature branch at `869d4bceae45e72411dbfbebacad0e1abacde09e` before this session's integration changes

**Earlier implementation baseline:** `bb3fc379862271bcfdd8715564990f1073b7df83`

**Scope:** continue the private B550I AMD64 and SP12 ARM64 pilots from the 2026-11-14 handoff. This report is a status record, not a physical-write checkpoint.

The report's SHA-256 is recorded in the adjacent
`supervised-continuation-20261115.sha256` sidecar.

## Work completed

### AMD64 target guard

Integrated the reviewed source change in `build.sh` and added
`tests/test_amd64_cpu_target_guard.py`. The builder checks Clang's effective
`-march=native` target against the pinned AMD64 `cpu_target` before
compilation, validates the final native/generic CPU Kconfig selections, and
records the expected and detected targets while retaining the previous
metadata line. The existing `znver3` pin and package bytes were not changed.

The 10 focused tests cover matching/mismatched targets, failed and malformed
Clang output, malformed pin data, unknown or incompatible arguments, ARM64
dispatch and pre-probe rejection, and final config-check ordering. An
independent reviewer approved the change. The real-host Clang probe reported
`znver3`, matching the pin. No kernel/package rebuild or actual Kbuild command
evidence was produced; future full builds still need compiler-command
evidence tied to the resulting package hashes.

### AMD64 activation prompt

Independent review found that the prompt `Reviewed health attestation path
(blank to stop)` selected a default path when the input was blank. A freshly
generated unreviewed attestation normally fails validation, but a valid file
could be completed while the prompt waited and promoted by pressing Enter.
The corrected `iso/activate.sh` now stops on blank input and forwards an
explicit path unchanged. Two focused tests exercise the actual prompt
function with a temporary fake trial helper; the independent review approved
the fix. Because `activate.sh` is embedded in the AMD64 installer, the
existing ISO is now a pre-fix artifact. It must not be used for lifecycle
qualification or promotion. Rebuild, audit, freeze, and boot-smoke a new exact
ISO before lifecycle qualification.

### Verification

- `python3 tests/test_amd64_cpu_target_guard.py`: 10 passed.
- `python3 tests/test_iso_activate_promotion_prompt.py`: 2 passed.
- `bash -n build.sh iso/activate.sh`: passed.
- `git diff --check`: passed.
- `bash tests/static-check.sh`: passed; it recorded 71 configuration changes
  and skipped the root-only `mokutil` check.
- No VM, kernel or package build, ISO build, package transaction, privileged
  operation, firmware update, physical write, reboot, or internal install ran.

## Capacity, inputs, and cleanup

At capture, local `/` and `/var/tmp` had **86,567,591,936 bytes free
(80.62 GiB)**. This is 668,246,016 bytes (0.62 GiB) above the required 80 GiB
reserve and 42,281,426,944 bytes (39.38 GiB) below the 120 GiB working target.
The previous AMD64 disposable installer target allocated 12,715,630,592
bytes, which would cross the reserve. `/tmp` is tmpfs and does not count as
disk-backed build capacity.

The read-only inventory certified **0 bytes safe to reclaim**. Large QCOW
artifacts include unresolved backing dependencies and retained qualification
evidence; no cleanup or deletion occurred. The report lists concrete review
targets and safe-retirement conditions in the isolated local inventory.

The exact pinned SP12 support checkout and all four machine-file hashes were
verified locally. The `cs-sp12` peer was offline, so no fresh remote check was
made. Its latest identity-verified reading is stale: 18,877,702,144 bytes
free (17.58 GiB) at 2026-11-15 00:12 UTC, below the native builder's 24 GiB
minimum before installer snapshot, staging, and output space.

The system QEMU command is not on `PATH`, but a retained local QEMU 11.0.3
binary at `output/iso-vm-tools/root/usr/bin/qemu-system-x86_64` runs with all
shared libraries resolved. The host exposes KVM, but `/dev/kvm` is owned by
group `kvm` and the current user is not a member. No VM was started because
the disk reserve is insufficient; no group or permission change was made.

## Media and firmware state

The full current Ventoy destination read-back hashes match both staged files:

- AMD64 pre-fix lifecycle ISO: 8,052,277,248 bytes,
  `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`.
- SP12 final51 file: 4,810,534,912 bytes,
  `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47`.

The staged SP12 file is verified live media only. Its buildinfo records
`installer_iso_sha256: null`; its recorded builder-script hash differs from
the current builder that accepts the opt-in installer payload. It does not
close the combined live/rescue/install image gate. It reached a private GRUB
entry in QEMU but not a live OS.

Read-only `efibootmgr` output showed `BootCurrent=0000` and
`BootOrder=0000,0002,0005,0004`, with `Boot0005` identifying General UDisk.
The 2026-11-14 write record says `BootOrder=0000,0002,0004` and places that
entry outside the order. This discrepancy is unresolved. No firmware state
was changed. The precise external target and protected-device serials are
retained in a local offline console runbook and are not included in this
sanitized report.

## ARM64 update and recovery evidence review

The r2 changed-release attempt remains **incomplete**. It reached the guest
login prompt without an authorized disposable credential or seed; no
authenticated session, dpkg transition, package hook, dracut completion, ESP
sync, or boot-selection result was recorded. QEMU ended after host SIGTERM,
and clean guest shutdown is unconfirmed. Independent review verified all 34
output-manifest entries, 39 archive checksums, and the retained pre/post
input hashes. Older historical review text reports 33 manifest entries; the
current review confirms 34 without changing the incomplete result.

The retained physical restored-default record supports only the historical
7.3.0 fallback, not final51 SP12 qualification. The generic-QEMU restored-root
control used manual GRUB loading of a generic kernel/initrd without a DTB; it
does not establish automatic hidden-default boot or Surface-DTB behavior.
Helper interruption tests pass only within process-kill, ENOSPC, or mock
scope. Prior guest EIO attempts targeted the wrong sectors; injector positive
controls do not prove guest EIO handling. Physical RPMB checks remain
read-only, and no RPMB provisioning or data write occurred.

## Gate classification

| Gate | Result | Current boundary |
| --- | --- | --- |
| AMD64 native target guard | **Pass** | Integrated source, 10 focused tests, static suite, independent review; no kernel rebuild or Kbuild evidence. |
| AMD64 activation prompt fix | **Pass at source level** | Two focused tests, static suite, independent review; the current ISO still embeds the pre-fix script. |
| AMD64 lifecycle VM | **Blocked by capacity** | QEMU binary is available, but local free space cannot preserve the reserve for the prior observed target allocation. |
| AMD64 external B550I rehearsal | **Blocked by prerequisite gates** | No new ISO, VM lifecycle, or fresh physical-write checkpoint. No installation write occurred. |
| ARM64 changed-release update | **Incomplete** | Login prompt only; no package transition. Needs an authorized disposable credential/seed and capacity. |
| SP12 combined media | **Blocked** | Staged image is live-only; remote builder is offline and last measured capacity is insufficient. |
| SP12 live/rescue and external rehearsal | **Incomplete / not started** | No final51 native live qualification or external rehearsal. |
| SP12 internal installation | **Not started; last by design** | All preceding software, recovery, live, and external gates remain open. |

## Next checkpoint

1. Restore enough local disk-backed space to reach at least 120 GiB free, then
   measure the intended VM/build peak and keep at least 80 GiB free. No current
   cleanup candidate is certified; preserve QCOW chains, unique evidence, and
   private inputs unless a separate retirement manifest is reviewed.
2. When `cs-sp12` is online, verify its host identity and current free space
   through the authorized Tailscale workflow. Do not bypass identity checks.
3. With capacity and any required local authorization ready, run the exact
   AMD64 lifecycle candidate in a disposable VM with compatible CPU features.
   Use fresh disposable ARM64 copies only after a test credential/seed is
   explicitly authorized; keep it out of delivery media.
4. Rebuild the corrected AMD64 ISO, independently audit its complete output,
   freeze buildinfo/checksums, and smoke-test that exact hash. Build the SP12
   combined image natively from the verified pinned support inputs and exact
   final51 installer ISO; audit the full output and freeze its identity.
5. Only after software/media/recovery gates pass, reidentify the B550I,
   external target, source media, protected disks, and firmware state. Present
   a fresh hash/serial/partition-bound checkpoint and await explicit user
   approval before the Apple HDD rehearsal. Save the console runbook before
   reboot; assume no chat or remote access during the hardware session.
6. Archive and independently review B550I evidence before reusing the Apple
   HDD for SP12 rehearsal. Qualify SP12 native live/rescue and external
   installation before presenting the final internal-install checkpoint.
   The SP12 internal clean install remains last.

Both pilots remain open. No result here authorizes an install, firmware
change, cleanup deletion, or media replacement.
