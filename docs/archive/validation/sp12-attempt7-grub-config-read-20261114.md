# Attempt-7 installed root GRUB config recovery

## Result

Recovered `/boot/grub/grub.cfg` from the attempt-7 installed root filesystem through a read-only QEMU NBD Unix-socket export. The extracted file is 8,536 bytes and SHA-256 is:

`f672512098384c1bef1a16ac179ee8075bceb2791a6d417fb0ee379473e494ed`

The extracted bytes are saved at `/tmp/luna-arm64-grub-review-bb3fc37/installed-grub.cfg`.

## Method and identity checks

The attempt-7 boot receipt SHA-256 matched `c4db71f0ecb3d3b0a81517a03c00a36cc2f0d12735ca3679ad0969aacb6070bb`. Before and after reading, immutable input hashes matched:

- Base qcow2: `4ecb266ff12bfff7da84f85016f5b8dc9a8f31c501ea02c9048c00025f0a4b6c`
- Attempt-7 overlay: `ac1f8a5169d016f6f68eb383b8bbbcc842124903eef165a645f3504fbac825ea`
- Firmware vars: `ac2f68d7a767d5e79b55528c739e30707b462f129d7151d43f18cc88cdd1b1ae`

I launched `qemu-nbd --read-only --persistent --socket=/tmp/luna-arm64-grub-review-bb3fc37/corrected-ro.sock --fork --pid-file=/tmp/luna-arm64-grub-review-bb3fc37/corrected-ro.pid --offset=$((2203648*512)) <attempt-7-overlay>`; this exports only the root partition, whose GPT start sector is 2,203,648. No VM was started; no image, NVRAM, or firmware was opened writable or mounted. The corrected extraction script is `/tmp/luna-arm64-grub-review-bb3fc37/read_ext4_corrected.py`. It reads `s_inodes_per_group` at ext4 superblock offset 40 (distinct from `s_clusters_per_group` at offset 36) and resolves `/boot` inode 2,097,153, `/boot/grub` inode 2,097,163, and `grub.cfg` inode 2,097,166. The NBD server was stopped after extraction.

## Config evidence

- GRUB searches root filesystem UUID `e9f6f469-4d8f-49f0-9a0d-00098d623055`, matching the ESP stub config's UUID.
- `default="0"`; normal timeout is hidden and zero. The default Ubuntu entry points to `vmlinuz-7.3.1-psycachy-sp121-r2`, initrd `initrd.img-7.3.1-psycachy-sp121-r2`, and DTB `dtb-7.3.1-psycachy-sp121-r2`. Its command line includes `root=UUID=e9f6f469-4d8f-49f0-9a0d-00098d623055 ro quiet splash console=tty0`.
- Advanced options contain normal and recovery entries for the same 7.3.1 candidate. The recovery entry uses `ro recovery nomodeset` and also names the 7.3.1 initrd and DTB.
- Advanced options also contain normal and recovery entries for the installed fallback kernel `7.3.0-9-generic`. Those entries name its matching initrd and do not include a DTB command.
- The menu configuration has no serial terminal directive; candidate kernel cmdline routes console to `tty0`. Therefore attempt-7 serial silence is not evidence that GRUB or the kernel failed after handoff. The hidden zero-timeout default makes the 7.3.1 entry the intended automatic selection, but config contents do not prove the menu was evaluated or a command executed.

## Boundary

The first unresolved runtime boundary remains **shim → GRUB**: firmware evidence establishes that UEFI started `\\EFI\\ubuntu\\shimaa64.efi`; attempt-7 evidence still contains no GRUB banner/error or command marker. The recovered config establishes the intended default/candidate and fallback commands, not their execution. There remains no retained proof that GRUB started, loaded kernel/initrd/DTB, entered the kernel, or reached initramfs. To localize the runtime failure, a future disposable COW capture needs a post-shim GRUB marker/serial trace and a GRUB command marker, then UART early-console output. Because this config routes candidate kernel output to `tty0`, serial capture must be explicitly enabled for that reproduction.


## Follow-up diagnosis (2026-11-14)

The boundary above reflects the evidence available when the config was extracted. A later bounded COW run displayed GRUB and, through interactive RAM-only commands, loaded the installed 7.3.1 kernel/initrd/DTB and entered the kernel with diagnostic serial output. The Surface-specific DTB then failed against QEMU `virt` GIC/timer addresses. With that DTB omitted, the same kernel/initrd reached the installed Ubuntu 26.10 serial login prompt under generic EFI/ACPI; no account login occurred. This resolves the shim-to-GRUB uncertainty for the reconstructed manual-command path, not whether the original attempt executed its hidden default entry, and does not qualify physical SP12 boot. See the [detached-boot diagnosis](artifacts/sp12-attempt7-detached-kernel-diagnostic-20261114/report.md) for run limits, input hashes, and retained logs.
