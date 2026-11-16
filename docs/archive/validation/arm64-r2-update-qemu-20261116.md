# ARM64 r2 update and recovery qualification (QEMU) — 2026-11-16

**Result:** changed-release package installation, media-free r2 boot, SP12
payload selection/synchronization, and return to r1 passed on disposable QEMU
storage. The focused interruption simulation suite and a controlled dpkg
unpack/configure recovery also passed. This does not qualify the physical SP12
loader, abrupt mid-hook interruption, real power-loss safety, or B550I
hardware.

## Test setup

The source was the retained ARM64 r1 target, SHA-256
`29e3a9c6be1d36b326192088483686860e794239ed4d877c0b71213e88113d72`, with a
copied UEFI variable file. The package-install VM used a standalone disposable
copy. A later media-free boot and selector run used a child QCOW2 overlay, so
the post-install snapshot remained unchanged. A separate controlled recovery
run used a fresh child overlay backed by that snapshot. All three VMs used
QEMU 11.1.3 TCG on `virt`/GICv3 with 6 vCPUs and 6 GiB RAM. Networking was
disabled. The package ISO and protected sentinel were read-only in the install
and recovery runs; the media-free run had no ISO attached and kept the
sentinel read-only. Copied UEFI variables used AAVMF without Secure Boot.

The previous login account was reset only inside the disposable guest with a
random local credential. The credential and shadow-file intermediates were
kept outside the repository and are excluded from the evidence bundle.

## Results

1. **Exact-hash update completed.** The package ISO hash was
   `1103a9e88d1a5961d6286cba10f54d2565353d8d19601873a1ddafdb481ba9cd`. The
   image package hash was
   `a1398ad1445d0a712aece65fbb2aa129a8afece4011e54773b6940616cae40bd`; the
   headers package hash was
   `80139be7bc17a3ab5034f2deafb220bd6373bd33b23ddd8e5032f98bf89dccf3`. Both
   installed as version `7.3.1-1psycachy2`. The package hooks completed the
   normal and kdump dracut initramfs builds and regenerated GRUB entries for
   r2, r1, and Ubuntu `7.3.0-9-generic`. `dpkg --audit` was empty and offline
   `apt-get --no-download check` passed. The source r1 image and generic kernel
   remained installed.

2. **The r2 kernel booted without installation media.** The copied UEFI state
   selected Ubuntu shim/GRUB. With the package ISO detached and networking
   disabled, the VM reached GDM and a serial login. The login banner and
   `uname -a` both reported
   `7.3.1-psycachy-sp121-r2` (`#1psycachy2`, aarch64). `dpkg --audit` remained
   empty. This was a generic QEMU `virt` boot through Ubuntu GRUB; it did not
   boot the physical SP12 platform or its custom removable fallback EFI path.

3. **SP12 selection and rollback synchronized complete payload sets.** The
   guest's boot configuration initially selected r1, and its ESP already
   matched r1. Running `sp12-select-fallback` for the removed r1 release
   selected package-owned r2, staged its DTB, saved the prior complete set,
   and synchronized the ESP. Byte comparisons confirmed the ESP kernel,
   initramfs, and DTB matched the r2 files; `SP12BOOT` was present and the ESP
   was read-only afterward. Running the helper for r2 selected r1 again. The
   r1 kernel, initramfs, and DTB then matched the ESP, the marker remained, the
   ESP was read-only, and the retained r2 recovery manifest passed
   `sha256sum -c`. Both releases and the generic fallback remained installed.

4. **Process-level fault simulation passed.** The focused suite passed 48
   tests across boot synchronization, fallback selection, FAT cleanup
   ownership, and FAT sector mapping. It covers temporary-file fault cases
   for staged flush, payload promotion, marker transitions, recovery rotation,
   restore, and retry. This is mock/process simulation, not physical
   power-loss testing.

5. **Controlled dpkg recovery passed.** On a fresh child overlay backed by the
   completed r2 clone, `dpkg --unpack` returned 0 and deliberately left the r2
   image and headers packages unpacked but not configured. Running
   `dpkg --configure -a` completed both package hooks, generated normal and
   kdump initramfs images, regenerated GRUB entries for r2/r1/generic, and ran
   the boot-sync hook. The final package statuses were installed,
   `dpkg --audit` was empty, and offline `apt-get --no-download check` passed.
   QMP powerdown and QEMU exit were clean. This exercises recovery from a
   controlled incomplete package state within the same guest boot; it does not
   simulate a forced stop during postinst or dracut.

## Integrity and limits

All QEMU guests shut down through QMP and exited with status 0. `qemu-img
check` reported no errors for the updated target, media-free child, and dpkg
recovery child. In the recovery run, QMP recorded 1,588,500,480 target write
bytes, zero package-ISO or protected-sentinel write bytes, and zero failed
operations on all three devices. The source target, original UEFI variables,
original sentinel, package ISO, and completed update-clone backing file
retained their recorded SHA-256 values. The test used no physical disk, Ventoy
media, firmware-order change, RPMB write, or hardware-dependent promotion.

The no-media r2 boot followed Ubuntu shim/GRUB, not `EFI/BOOT/BOOTAA64.EFI`.
The helper switched the disposable ESP to r2 and back to r1, but the VM was not
rebooted through the custom SP12 loader after those transitions. The controlled
unpack/configure recovery passed, but recovery after forcibly stopping QEMU or
killing dpkg during a postinst/dracut hook remains untested. Earlier FAT
evidence includes exact-sector positive controls and one passing guest
allocation-metadata EIO during staged payload flush. Other metadata and
interruption points remain incomplete or inconclusive; no result establishes
physical power-loss safety.

## Remaining work

- If additional software qualification is warranted, test recovery after an
  abrupt QEMU stop during dpkg postinst/dracut on a disposable overlay; the
  controlled unpack/configure recovery above does not cover that failure mode.
- Reboot through the custom SP12 removable fallback loader after selecting r2
  and after restoring r1, using a platform-appropriate emulator or the
  attended SP12. Generic `virt` results do not establish SP12 hardware boot.
- Complete the read-only live-device and RPMB health checks, then any external
  installation only with a fresh serial-bound target checkpoint and separate
  approval. Do not provision or write RPMB data.
- On B550I, enroll the per-install MOK keys through the attended firmware
  screen, attempt the pinned candidate, and check the RTX 4070/NVIDIA path.
  Keep lifecycle promotion behind hardware attestation.
- Retain the 80 GiB free-space reserve. After removing the disposable ARM64
  update and recovery VM files, the host had 165 GiB free.

The raw transcripts, exact inputs, package hashes, QMP counters, integrity
checks, and SHA256SUMS are in
`artifacts/arm64-r2-update-qemu-20261116/`.
