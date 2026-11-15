# Final independent review: AMD64 lifecycle ISO live-boot smoke

**Reviewed:** 2026-11-14, read-only. No workspace files were changed.

## Disposition

**Approved with evidence limits stated below.** The exact candidate boot reached the Ubuntu live desktop and guarded disk selector. No install action was taken. The outer evidence manifest and the separate independent-review checksum manifest both verify.

## Candidate and run boundary

Candidate: `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso`, 8,052,277,248 bytes, SHA-256 `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`. The candidate checksum file passed both the archived verification and a fresh checksum check. Captured run details specify QEMU 11.0.3, KVM, network disabled, fresh `init-insecure` OVMF vars/non-Secure-Boot firmware, 2 vCPUs, 4 GiB RAM, a writable disposable 64 GiB COW target with serial `psycachy-linux`, and a read-only 64 GiB sentinel COW. This does not qualify Secure Boot, GPU, or physical B550I behavior.

The GRUB, UEFI boot-progress and selector screenshots support the serial/log record that GRUB 2.14 booted the default Try or Install entry into the live desktop and guarded selector. The selector shows only `/dev/vda`, serial `psycachy-linux`, with the checkbox unchecked. No disk, install mode, or `ERASE` confirmation was selected. The desktop auto-logged in; no installed-system login or post-selection lifecycle step was run. The `grub_platform` warning is captured, matches the signed base ISO configuration, and did not stop this observed boot.

## No-install / no-write evidence

The target COW passed `qemu-img check`; its retained map marks the full virtual range absent/zero with no present data blocks. The sentinel drive is attached read-only in `tests/iso-vm.sh`; the sentinel post-copy SHA-256 matches its pre-run hash `b7f1ada63281ed7e5bc7127dffbfc4c91582fab3080133b01a966c7624d97bb6`, and its 1 MiB pattern read passed. Both QCOW checks passed. Together with the unchecked selector and absence of confirmation, this supports no guest target-sector writes and no sentinel modification during this smoke.

## QEMU stop/exit evidence

`monitor-action.txt` retains the HMP greeting, the sent `quit` command, and socket closure. `run-result.txt` retains the outer execution result `qemu_status=0`. These support that the wrapper returned status 0 after the monitor stop. The result is not a raw QEMU process log; no separate raw exit-status file or full monitor transcript was retained. The current report correctly says the wrapper result is not independently re-verifiable from raw QEMU output.

## Storage reserve arithmetic

At the recorded 03:55 UTC measurement, `/` and `/var/tmp` had 97,450,049,536 bytes free. The 80 GiB reserve is 85,899,345,920 bytes, so above-reserve headroom was:

`97,450,049,536 - 85,899,345,920 = 11,550,703,616 bytes` (about 10.76 GiB).

The retained earlier AMD64 installer target's `qemu-img info` actual allocation was 12,715,630,592 bytes. Repeating that observed allocation would exceed headroom by:

`12,715,630,592 - 11,550,703,616 = 1,164,926,976 bytes` (about 1.08 GiB).

The separate `/tmp` tmpfs had 12,805,242,880 bytes free. The decision to defer a full disposable install is supported by those measurements; re-measure before the next run.

## Checksums, links, and status wording

The reviewed **evidence-manifest hash** is the SHA-256 of the outer bundle `SHA256SUMS`: `fb43243df0f109fd53c390bc6d6c4fe412aac2561704607dab56f95e722d8de9`. All 22 files listed by that manifest passed `sha256sum -c`. The independent-review subdirectory is excluded from the outer evidence manifest to avoid self-reference. Its separate checksum manifest was verified and validates the review report. The review itself is independently checksummed outside the evidence bundle.

The current live-boot and build records both label `fb43243...` as the outer evidence-manifest hash. The earlier stale `620ef...` reference is no longer present in those records. Their wording correctly distinguishes the auto-logged-in live desktop from an installed-system login. Local Markdown links in the ledger, implementation queue, ship checklist, build record, and live-boot record all resolve.

## Files checked

- Live-boot record SHA-256: `188a2f8d95fd6d4b9fee224dd7816df8a53eecf1c5dee73412d82050e0d13095`.
- Build record SHA-256: `48163ae89fcfc9a1a5f6c0a37d00c0d4458c2aeec3f63ddd1e8db2dda3af8947`.
- Outer evidence-manifest SHA-256: `fb43243df0f109fd53c390bc6d6c4fe412aac2561704607dab56f95e722d8de9`.
- A separate checksum manifest verifies the independent review report.

Commands/inspection: `sha256sum -c` on both manifests and candidate checksum; `sha256sum` on the candidate; read-only review of `run-result.txt`, `monitor-action.txt`, `run-command.txt`, QCOW metadata/map/checks, sentinel checks, screenshots and serial log; inspection of `tests/iso-vm.sh` drive/network arguments; Markdown link resolution across the five status/report documents; and `qemu-img info` on the retained earlier installer target for the allocation figure.
