# Approved Ventoy ISO replacement record

**Completed:** 2026-11-15 02:11 UTC / 2026-11-14 19:11 MST  
**Authorization:** the user approved replacing both existing ISO files on this
USB after being shown the exact candidate hashes, sizes, combined size, old
file identities, and available capacity.

## Target and scope

- Whole-device by-id: `/dev/disk/by-id/usb-General_UDisk-0:0` → `/dev/sdc`.
- Reported model/serial: `UDisk` / `General_UDisk-0:0`, 14.6 GiB.
- Ventoy partition: `/dev/sdc1`, exFAT label `Ventoy`, UUID `4E21-0000`,
  mounted at `/run/media/charlie/Ventoy`.
- The existing Ventoy partition table and filesystems were preserved. Only the
  two approved ISO files were replaced; no whole-device or partition image was
  written.
- Protected Lexar BIOS-rescue USB serial `AA8AGLJAH1RZABDT`, Apple HDD serial
  `TNS519GY1G6JGG`, and system internal disks were not written during this
  operation.

## Source and destination verification

| ISO | Source size | Source SHA-256 | USB read-back SHA-256 | Result |
| --- | ---: | --- | --- | --- |
| `psycachy-ubuntu-26.10-desktop-amd64.iso` | 8,052,277,248 bytes | `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c` | `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c` | Exact size and full read-back hash matched. |
| `private-sp12-r2-final51.iso` | 4,810,534,912 bytes | `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47` | `099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47` | Exact size and full read-back hash matched. |

The AMD64 ISO was copied to a hidden partial filename with a filesystem flush;
the transfer reported 2,311.72 seconds. Its complete destination file was
read back and hashed before it was renamed to the final ISO name. The SP12 ISO
was streamed from `cs-sp12` over approved Tailscale SSH into a hidden partial
file using `dd` with `conv=fsync`; the transfer reported 1,145.4 seconds and
completed with exit status 0. The exact byte count and complete destination
hash were checked before renaming it.

The AMD64 ISO SHA-256 sidecar is present on the USB and archived beside this
record. The original SP12
`.sha256` sidecar and 4,486-byte `.buildinfo.json` were fetched from the same
`cs-sp12` output directory and copied to the USB; the sidecar hash equals the
full destination read-back hash. Those SP12 metadata files are retained beside
this record. The SP12 sidecar's SHA-256 is
`87bf4e0400ecbdd8c160d6e0cce6a8bf4137e4a7b5b2172e0022a9ebf1ce11a2`; the
buildinfo SHA-256 is
`2b70507b1de09cc660170aab3e9f37b4ae00808c21782f1fdbe3a488b970de42` on both
the source host and local archive. The media filesystem was synced after the
renames and metadata copies.

After the operation, the Ventoy filesystem remained mounted as exFAT UUID
`4E21-0000`, both ISO files had their expected byte sizes, and 2,828,926,976
bytes were free after metadata copies. At the time of staging, no firmware boot
had been performed. The subsequent user-reported one-time boot and firmware
order reconciliation are recorded below. The replaced ISO identities and
pre-write inventory are retained in
[`inventory.md`](inventory.md); the old ISO binary contents were not archived.

## B550I boot observation and firmware-order reconciliation

The user reported that the approved AMD64 ISO booted into the installer on the
MSI MPG B550I Gaming Edge WiFi and displayed a generic live kernel, recalled as
`7.3.0-9-generic`. No exact `uname -r` output or screenshot was retained, and
the guarded selector's final state was not captured. This is user-reported
media boot evidence only. The approval covered no installation or disk erase;
the live generic kernel does not identify the installed candidate's Zen 3
kernel.

Before reboot, read-only `efibootmgr -v` showed `BootOrder: 0000,0002,0004`
(Ubuntu, Windows Boot Manager, Lexar rescue). After the one-time boot, firmware
showed `BootOrder: 0000,0002,0005,0004`, with new `Boot0005` labeled `UEFI:
General UDisk 5.00, Partition 2`. No EFI-variable write had been issued before
that observation. The original order was restored with
`pkexec efibootmgr -o 0000,0002,0004` and verified by read-back. `Boot0005`
remains stored but is no longer in `BootOrder`; the protected Lexar entry
remains `Boot0004` and was not selected. No installation target or erase was
authorized by this checkpoint. The current post-restore read-only firmware
inventory is archived at
[`firmware-boot-order-post-restore.txt`](firmware-boot-order-post-restore.txt).

The Apple HDD was absent from the first post-boot inventory, then reappeared
and was reidentified by the stable path
`/dev/disk/by-id/ata-APPLE_HDD_HTS545050A7E362_TNS519GY1G6JGG` → `/dev/sdc`.
It reports 465.8 GiB, model `APPLE HDD HTS545050A7E362`, serial
`TNS519GY1G6JGG`, whole-device ISO9660 label `Ubuntu 26.10 arm64`, partition 2
FAT/ESP UUID `98A7-CC63`, and partition 3 ext4 UUID
`bb78f7c8-7c47-4bb4-89fe-e40432e0ca44` (461.3 GiB). No partition is mounted,
and `fuser` reported no active process using the disk. Its prior `/dev/sdb`
name is stale; installation selection must use the model and serial shown by
the installer.

The current raw image prefix was not rehashed: unprivileged block reads were
denied, and a privileged `fdisk -l` query was cancelled while waiting for
local authentication. The retained
2026-11-12 direct-I/O record documents a full prefix read-back with SHA-256
`e29dd59f76fcf73ce1e7ed8dfe60d88b83f7d2dd3c8a4cfcbab1b9b413817e36`. That
exact corrected ISO remains on `cs-sp12` at
`/var/tmp/sp12-live-output-20261112/sp12-ubuntu-26.10-arm64-live-private-fdt-fix.iso`
and its current SHA-256 was rechecked. The original direct-I/O output is
retained at
[`flash-corrected-iso-readback.txt`](../../../../../output/.unattended-luna-20261111210910Z/qemu-hosting/sp12-live-qualification-20261112/flash-corrected-iso-readback.txt)
(SHA-256 `5b90489b644bcb54bd2b3f6b668fa10217ea10f067ea5213a57b8f00995e2682`).
The prior read-only inspection of the same ext4 UUID found only `lost+found`;
this pass did not remount the partition. A same-size local ISO hashes to
`dfd9c3e081a002a8a9ad572750d4998da06255dd7a51cb223b5271f07b210523`; it is a
different pre-fix artifact and was not treated as the HDD source.
