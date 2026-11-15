# Independent review: ARM64 r2 changed-release reproducer

**Review scope:** Read the worker report and sealed output bundle in `/tmp/luna-arm64-update-20261114/`; verify the output manifest, current pre/post input hashes, key copied artifact hashes, and recorded QCOW2 checks. No QEMU or guest interaction was performed. No workspace file was changed. Baseline cited by the worker: `bb3fc379862271bcfdd8715564990f1073b7df83`.

## Claim-by-claim findings

1. **Classification is incomplete, not a reproduction or a failure of the update path — APPROVED.** The worker's `report.md` explicitly says no changed-release package transition was run and does not claim to clear the gap. The package pair is indeed a release change: pin `config/arm64-iso-kernel-r2.json` and the exact image/headers deb hashes are reproduced consistently in pre/post inputs, and both package files identify the requested `7.3.1-1psycachy2` release by their paths. The report carefully says the prior `7.3.1-1psycachy1` state comes from prior-run notes and was not queried in this attempt.

2. **No explicit target login credential or seed, so no authorized guest shell — SUPPORTED WITH EVIDENCE SCOPE.** The serialized run log ends at `luna-arm64 login:` after systemd/cloud-init-local output. `run-qemu.sh` starts the retained guest with no network (`-nic none`), attaches the package ISO read-only, and the recorded relay is a serial pass-through, not an automated login script. The report and stop-status both state no authorized credential/seed was available and none was guessed. This supports no authenticated shell or package command during the recorded attempt; it is not an independent inspection of hidden QEMU input events beyond the saved launch/relay/log evidence.

3. **No dpkg/package/postinst transition or its postchecks — APPROVED AS NOT RUN.** There is no authenticated shell evidence or package command output. The report names dpkg, maintainer scripts, dracut, SP12 postinst, ESP sync, and package postchecks as unexercised. Consequently the attempt gives no positive or negative evidence about those hooks, boot-config mutation, ESP changes, or fallback preservation.

4. **Pre/post package/pin/target/firmware source hashes stable — VERIFIED.** `pre-input-hashes.txt` and `post-input-hashes.txt` are byte-identical. I reran `sha256sum -c` against each list from the repository root; every line passed, including pin `6fb4104b…bee7c90`, image deb `a1398ad1…cae40bd`, headers deb `80139be7…9dccf3`, retained target `29e3a9c6…113d72`, retained vars `ed3bc0c0…eb64175`, and AAVMF code `e58a9508…d61e5`. The package ISO embeds copies of the same two package byte streams, recorded as image `a1398ad1…cae40bd` and headers `80139be7…9dccf3` in the key-artifact record.

5. **Only run-owned COW and cloned vars changed among the tracked run artifacts — VERIFIED.** `pre-run-owned-hashes.txt` and `post-run-owned-hashes.txt` show unchanged read-only package ISO (`1103a9e8…1ba9cd`), child COW changed from `7cbbd2fd…51efcc` to `e7abec7c…059da1`, and cloned vars changed from source-copy hash `ed3bc0c0…eb64175` to `e48dc6f6…0a8847`. Source target and source vars remain the identical hashes listed above. The COW was based on the exact retained target path; the captured backing check states no errors.

6. **QCOW2 consistency checks — VERIFIED FROM HASHED CAPTURED OUTPUTS.** `backing-check.txt`, `child-precheck.txt`, and `child-postcheck.txt` each state `No errors were found on the image.` Their hashes are present in the sealed `output-manifest.sha256`, and `sha256sum -c output-manifest.sha256` passed for all 33 listed run artifacts. The child post-info records the expected retained target as backing and `corrupt: false`; the child post-map reports depth-0 allocations. I did not invoke `qemu-img` or QEMU during this review.

7. **Shutdown caveat retained — APPROVED.** `qemu.exit` says wrapper `qemu_rc=0`, but `qemu.stderr` explicitly says QEMU terminated on signal 15 and `stop-status.txt` records failed/no-response QMP system-powerdown and no confirmed shutdown line. Therefore wrapper status 0 is not evidence of clean guest shutdown; the worker report correctly labels clean shutdown unconfirmed.

8. **Run controls and size — CONSISTENT.** Captured launch command uses TCG, 6 vCPUs, 4 GiB RAM, network disabled, read-only code firmware, read-write cloned vars, read-write child COW, and read-only package ISO. `pre-run-usage.txt` reports the run directory at 362,979,328 bytes (< 4 GiB cap). The wrapper's `qemu_rc=0` should be interpreted only as shell wrapper outcome, subject to the signal caveat above.

## Approval

**Approved as an evidence-bounded incomplete attempt.** It does not reproduce, resolve, or refute the changed-release upgrade behavior. The exact missing prerequisite is an explicitly authorized target login credential or retained disposable cloud-init seed. The next attempt should use a new child COW and cloned firmware vars, then collect the package and boot/ESP/fallback postchecks. No credentials should be guessed.

## Source bundle identity

- `output-manifest.sha256`: SHA-256 `a5d8e88d1d9f1b6130de7b84a4c10f6feac0bb58cc7a4d96b2…` (full digest recorded in `checksums.txt`)
- Worker report: SHA-256 `9b760452966f9f147f1b103bab2ab9f18767fab931c77a6b853aa20560beb561`
- `pre-input-hashes.txt` and `post-input-hashes.txt`: each SHA-256 `efaabe8b1a5f617b793cc9f954ecb97d1ade56d53a3f30f7f5e80db156d59d9f`
- `key-artifact-hashes.txt`: SHA-256 `3f2dbf2959b557578a77c56933dd0f38bfe53a53b4da006e2739ebcb67e73499`
