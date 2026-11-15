# ARM64 r2 changed-release update attempt — incomplete

## Result

The requested normal changed-release package transition was **not run**. The exact target v4 COW backing image booted far enough to show a serial login prompt (`luna-arm64 login:`), but no explicitly recorded test credential or target cloud-init seed was available. I did not guess credentials or issue guest commands. Thus `dpkg`, maintainer scripts, dracut, the SP12 postinst hook, ESP synchronization, and package postchecks were not exercised. This attempt does not reproduce or clear the r2 update gap.

Existing prior-run notes identify the retained target as having image/headers `7.3.1-1psycachy1`; the requested pair is `7.3.1-1psycachy2`, so the intended operation was a real release change. This run did not independently query the guest dpkg database.

## Run controls and evidence

- Baseline HEAD: `bb3fc379862271bcfdd8715564990f1073b7df83`.
- Only new run artifacts were created under `/tmp/luna-arm64-update-20261114/`.
- Target: fresh QCOW2 child `target-r2-child.qcow2`, virtual size 64 GiB, backed only by retained `.../vm/target.qcow2` (SHA-256 `29e3a9c6be1d36b326192088483686860e794239ed4d877c0b71213e88113d72`). The backing target had a pre-run `qemu-img check` pass. No original target/vars file was written.
- Firmware vars were cloned to the run directory; code firmware was read-only. Networking was disabled. Package ISO was attached read-only and contained only the exact image and headers package pair.
- QEMU was the retained QEMU 11.1.3 binary, SHA-256 `7719a165316bbbc568bc2de698b7ea9548cc369b1ced34e38e60da68d0ce62f2`; it ran under TCG with 6 vCPUs and 4 GiB RAM. The captured launch script is `run-qemu.sh`.
- Firmware/GRUB/kernel selection details were not fully captured because the serial relay attached after early boot output. Serial evidence does show the existing guest reaching initrd/root-device processing, finding ESP UUID `4053-1CD8`, completing initrd switch-root, running `cloud-init-local`, and then showing `luna-arm64 login:`. There is no authenticated shell evidence.
- QEMU elapsed about 10 minutes. QMP `system_powerdown` did not yield a response; host SIGTERM was sent to QEMU PID 775105 per the parent instruction. `qemu.stderr` records signal 15. The serial log has no confirmed shutdown line. **Clean guest shutdown is unconfirmed.**
- The post-run COW passed `qemu-img check`: no errors. Child image actual size was 70,979,584 bytes; `qemu-img map` reports 69,795,840 bytes at depth 0. The complete run directory occupied 438,751,232 bytes, below the 4 GiB cap.
- Exact pin, both package files, retained target, retained firmware vars, and AAVMF code SHA-256 values are identical in the pre- and post-run hash lists. Cloned run vars changed from source hash `ed3bc0c0a050f40f4c33eee325e242f8daa2bc2358c172ef5cd691961eb64175` to `e48dc6f6eaab8d30f138a17ee29e91719aea5e5cad50729fc845d3484b0a8847`; the source vars stayed unchanged.
- Package ISO SHA-256: `1103a9e88d1a5961d6286cba10f54d2565353d8d19601873a1ddafdb481ba9cd`.
- New COW SHA-256: pre-run `7cbbd2fdeb1f0d3374fb209ff742a5eabba12e8c973be4b37fdac7c8d551efcc`; post-run `e7abec7cfd6526b2f78227c35cc96a97a660f6b31a9d0b30efdfccd398059da1`.

## Minimum missing prerequisite and next safe test

Provide or identify an explicitly authorized login credential for the retained target, or a retained disposable cloud-init seed that supplies a known test account. Then repeat only on a new child COW and a fresh clone of firmware vars, attach the exact package ISO read-only, disable networking, and run the normal r2 package transition without manual boot.conf edits or DTB staging. Collect baseline and final dpkg audit/status; kernel postinst, dracut, sync hook; boot.conf; `/boot` and ESP kernel/initrd/DTB hashes; and fallback state. Stop at the same COW/storage cap and classify timeout as incomplete.

The report does not establish package-hook success, GRUB/default-kernel changes, ESP payload changes, fallback preservation after an update, or clean shutdown.
