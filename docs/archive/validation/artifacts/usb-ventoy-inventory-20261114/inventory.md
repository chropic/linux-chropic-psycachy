# Attached Ventoy USB inventory

**Pre-write read-only inspection:** 2026-11-14, America/Denver  
**Whole-device by-id:** `/dev/disk/by-id/usb-General_UDisk-0:0`  
**Partition 1 by-id:** `/dev/disk/by-id/usb-General_UDisk-0:0-part1`  
**Observed device:** `UDisk`, reported serial `General_UDisk-0:0`, 14.6 GiB  
**Filesystem:** exFAT label `Ventoy`, UUID `4E21-0000`; mounted at
`/run/media/charlie/Ventoy`  
**Free space:** 2,353,856,512 bytes at inspection.

No partition, filesystem, or file writes had been made at the time of this
inventory. The protected Lexar BIOS rescue USB is a different device
(`AA8AGLJAH1RZABDT`) and remained untouched during the later approved ISO
replacement as well.

## Existing files

| File | Size | Timestamp | Evidence |
| --- | ---: | --- | --- |
| `psycachy-ubuntu-26.10-desktop-amd64.iso` | 8,366,061,568 bytes | 2026-11-07 13:12:50 -0700 | SHA-256 `8caac7f32e750566c5676940364b40ce37d765f6a945feb5ad2ae43baf4b0870`; no adjacent sidecar/buildinfo was present. It differs in size and hash from the selected lifecycle ISO. |
| `sp12-ubuntu-26.10-arm64-private-live-v2.iso` | 4,971,847,680 bytes | 2026-10-24 18:32:48 -0600 | SHA-256 `d550c05575196069bd458f3a97c04acfc6660ceb4cdb5e7b7dab37879b6b6ec5`; verified equal to the adjacent `.sha256` sidecar. Buildinfo says target kernel `7.3.0-sp12-v7.3-platform`, created 2026-10-24, and `installer_status=experimental-not-installation-tested`. |

The SP12 `.sha256` and `.buildinfo` files are archived beside this inventory.
At the time of the pre-write inventory, the SP12 ISO was not the final51 live
image (SHA-256
`099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47`). No
independent boot test of the Ventoy device or its SP12 ISO had been performed.
The later AMD64 installer boot and remaining SP12 boot gap are recorded in the
[write record](write-record.md).

The final51 SP12 image is 4,810,534,912 bytes and the selected AMD64 lifecycle
ISO is 8,052,277,248 bytes. Together they require 12,862,812,160 bytes before
small sidecars and filesystem overhead, exceeding the 2,353,856,512 bytes
free at the time of this inventory. The later user-authorized file-level
replacement and read-back verification are documented in the
[write record](write-record.md).
