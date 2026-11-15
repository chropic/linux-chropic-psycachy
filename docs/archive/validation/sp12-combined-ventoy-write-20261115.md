# SP12 combined image staged on Ventoy — 2026-11-15

**Result:** Approved file-level replacement passed; both ISO destination
read-back checks passed. Native SP12 runtime qualification remains open.
**Post-write state checked:** 2026-11-15 13:56 MST.

## Candidate and media identity

- Candidate: `private-sp12-r2-final51-combined.iso`
- Size: 5,500,940,288 bytes
- SHA-256:
  `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`
- Source on SP12:
  `/var/tmp/sp12-r2-combined-20261115/output/private-sp12-r2-final51-combined.iso`
- Target: Ventoy UDisk serial `General_UDisk-0:0`; exFAT data partition
  UUID `4E21-0000`, mounted at `/run/media/charlie/Ventoy`.

The user explicitly approved replacing the prior SP12 live-only ISO and its
sidecars. The old file was 4,810,534,912 bytes, SHA-256
`099fb8b9afa7e7a28f500db8c203e278a94847701e895b7299478c9bc3a3ea47`.
Its exact remote copy, checksum sidecar, and buildinfo remain at
`/var/tmp/sp12-r2-final51-build/output` on SP12 for recovery.

## Write and verification

The local writer reidentified the UDisk model, serial, filesystem UUID, and
mount, checked source size and sidecar, and confirmed the available-space
calculation. It streamed the image into a temporary `.partial` file using
`dd conv=fsync`, verified the exact byte count, and renamed it to the final
name. It then copied and byte-compared the 103-byte checksum sidecar and
5,258-byte private buildinfo, synced, and completed full destination
read-backs:

- Combined SP12 ISO: `private-sp12-r2-final51-combined.iso: OK`
- Protected AMD64 ISO: `psycachy-ubuntu-26.10-desktop-amd64.iso: OK`
  (8,052,277,248 bytes; SHA-256
  `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`)

The writer exited with code 0 and reported `write_result=PASS`. The final
Ventoy partition has 2,138,603,520 bytes free. The combined ISO and metadata
are present under their final names; the old live-only ISO is absent.

## Boundary

Only files on the existing Ventoy data partition were changed. The Ventoy
partition table and 32 MB VTOYEFI partition were not written. Firmware/NVRAM,
the Apple HDD, internal storage, and installation targets were not changed.
The exact target, protected device identities, and recovery procedure are in
the private local
`artifacts/sp12-combined-build-20261115/ventoy-write-checkpoint.md`.

This staging result does not qualify a physical SP12 boot. The combined image
is experimental; native live/rescue startup and Wi-Fi, audio, suspend, and
other exact-device checks remain open. No installer entry was selected.
See also the [build and content audit](sp12-combined-build-20261115.md).
