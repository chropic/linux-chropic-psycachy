# SP12 firmware and live-boot result — 2026-11-16

## Initial attempt

The user first attempted to select the staged SP12 final51 combined image from
the one-time firmware boot menu. The user reports that **Ventoy was not
listed**, so the USB image was not selected and no operating system booted.

The earlier read-only inventory that recorded a Ventoy BootOrder entry was
for the B550I, not SP12, so it does not establish SP12's firmware state.

## Follow-up live boot

The user later reported that the SP12 image booted. The pasted terminal
diagnostics are retained in
[`artifacts/sp12-live-boot-20261116/diagnostics.txt`](artifacts/sp12-live-boot-20261116/diagnostics.txt)
with an adjacent `SHA256SUMS` file. They show:

- Running kernel: `7.3.1-psycachy-sp121-r2`.
- Runtime DTB build ID: `sha256:43e6fa05d5ee85e49bfc1d295f0ce77bcba55e1366b39f2cc6240d69783249d0`, matching the final51 pin.
- Ventoy ISO mounted at `/cdrom` as read-only ISO9660; `/rofs` is read-only squashfs; `/cow` is the live writable overlay.
- `lsblk` reports `sda` at 476.7 GiB with a 1 GiB vfat partition and a 475.7 GiB ext4 partition. Neither partition has a mount point in the capture. The reported disk serial is preserved in the raw diagnostic.

This is a successful physical live-session startup with the expected kernel
and DTB identity. The Ventoy file had previously passed a full destination
read-back for SHA-256
`56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`; the
session capture itself does not include an in-session ISO hash. The output
does not record the display/input, wireless, Bluetooth, audio, camera, storage
health, suspend/resume, or read-only RPMB checks. It also does not include
write counters or a post-boot firmware-variable comparison. No installation
or RPMB write was reported.

The staged image was
`/run/media/charlie/Ventoy/private-sp12-r2-final51-combined.iso`, SHA-256
`56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`. The
first firmware-menu failure is superseded by the successful follow-up live
boot. Native device checks and external installation remain open. The
diagnostics do not report an installation, RPMB write, or persistent
firmware-order change. At the next attended live session, finish the
device/read-only checks and transfer the evidence to B550I with verified
hashes before ending the session.
