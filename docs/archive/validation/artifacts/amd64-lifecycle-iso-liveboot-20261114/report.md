# AMD64 lifecycle ISO live boot smoke evidence

Run: 2026-11-14 03:51–03:53 UTC  
ISO: `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso`  
ISO SHA-256: `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`

The network-disabled UEFI/KVM run booted the exact candidate to the Ubuntu
live desktop and PsyCachy guarded disk selector. The only listed target was
`/dev/vda`, serial `psycachy-linux`; it remained unchecked. No disk, mode, or
erase confirmation was chosen. QEMU was stopped at the selector through the
monitor and the outer wrapper reported exit status 0. The captured wrapper
result is in `run-result.txt`; `monitor-action.txt` records the HMP greeting
and sent command. No raw QEMU exit-status log or full monitor transcript was
retained, so the exit status is a lead-recorded result rather than independently
re-verifiable raw output.

`grub-menu.png`, `kernel-boot-splash.png`, and
`installer-disk-selector.png` are sequential screen captures. `serial.log`
retains the GRUB warning `can't find command 'grub_platform'`; the same bare
line appears in the signed Ubuntu base ISO's GRUB configuration, and the boot
continued through the live desktop. This run used OVMF `init-insecure`, so it
does not test Secure Boot.

Both QCOWs passed `qemu-img check`. The target map has no present guest-data
blocks. The read-only sentinel hash/read check and candidate ISO checksum
check passed. `run-command.txt`, tool hashes, QEMU version, and the firmware
mode retain execution details. The live desktop auto-logged in; no installed-
system login, Ubuntu installation, or post-selection lifecycle step was tested.
