# ISO publication readiness

**Status as of 2026-11-18:** neither current ISO is ready for public release.
Build and content audits have passed, but pilot qualification and public-release
gates remain open. This summary omits raw logs, personal identifiers, network
identifiers, and per-device inventories.

## Current candidates

| Target | Candidate | Current evidence | Remaining private-pilot gates |
| --- | --- | --- | --- |
| AMD64 B550I | 8,052,277,248 bytes; SHA-256 `908f7df0604cc28a4d36c7dbcf19fd9e09cdc16c42035f25876763092c4db7dc` | Independent content audit, disposable install, generic-fallback boot, package checks, and read-only repeat-media boot passed. | Complete the exact-hash activation and rollback lifecycle; validate the candidate and graphics/network/audio/suspend behavior on target hardware; investigate the live-session reboot anomaly. |
| ARM64 SP12 combined | 5,500,940,288 bytes; SHA-256 `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27` | Build/content audit and Ventoy destination read-back passed. A native live session reported the pinned kernel and DTB identity, but no in-session ISO hash was captured. | Complete hardware and storage qualification; close the external-target install, installed-system boot, package-health, and recovery gates. |

## SP12 hardware matrix

The operator reports Wi-Fi, Bluetooth, keyboard/touch input, and
suspend/resume working. The post-resume capture showed Wi-Fi disconnected even
though the operator confirms it worked; the automatic-reconnect detail remains
unresolved. Built-in speakers remain silent. GNOME Sound Settings showed no
microphone input, although an earlier PipeWire snapshot listed an internal
source; capture has not been tested.

Camera discovery remains unsuccessful: the available video nodes are codec
decoder/encoder nodes, not camera-capture nodes; V4L2/media tools were
unavailable and GStreamer found no source. The kernel logged an RPMB region
registration, but no authenticated read request was made.

The same session's kernel log recorded USB transport failures, attempted writes,
and an ext4 journal abort/read-only remount on an unidentified external
filesystem. The physical device was not mapped, so no specific drive or medium
can be attributed. Storage health and installation remain blocked pending
resolution. See the [sanitized SP12 follow-up report](archive/validation/sp12-live-hardware-check-20261118.md)
and the [ship checklist](SHIP-CHECKLIST.md).

## Additional public-release gates

After both private pilots pass their exact-candidate software, recovery,
hardware, and restore checks:

- Run all six Phase 2 performance scenarios on both targets, with at least
  three interleaved baseline/candidate pairs per scenario.
- Meet the documented thresholds: at least 10% lower whole-system energy where
  measurable, completion time no more than 10% longer, and p95 response latency
  no more than 5% worse. New storage errors, watchdog events, failed resume, or
  functional regressions reject a result.
- Resolve the SP12 whole-system-energy measurement gap in the approved setup.
- Complete redistribution and attribution clearance for every shipped
  component.
- Freeze the final ISO, package, kernel, DTB, source, configuration, and
  manifest identities and archive the release checksums.

This status page is not installation approval or a public ship decision.
