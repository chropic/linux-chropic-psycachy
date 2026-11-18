# SP12 live hardware check — 2026-11-18 follow-up

## Evidence boundary

This report summarizes user-provided diagnostics and operator observations from
the final51 live session. It intentionally excludes raw terminal output,
network identifiers, device serials, boot identifiers, and per-device
inventories. No in-session ISO hash was captured, so the running session is
identified by its reported kernel and DTB, not by proof of the exact ISO bytes
read by firmware.

## Session and hardware results

| Area | Result | Evidence and limits |
| --- | --- | --- |
| Candidate runtime | Identity matches the final51 pin | Reported kernel `7.3.1-psycachy-sp121-r2` and DTB build ID `sha256:43e6fa05d5ee85e49bfc1d295f0ce77bcba55e1366b39f2cc6240d69783249d0`. No in-session ISO hash was captured. |
| Suspend/resume | Pass, with Wi-Fi state discrepancy | Before/after diagnostics retained the same boot identity; uptime advanced about 103 seconds. The operator reports the system worked after resume. The captured NetworkManager snapshot showed Wi-Fi disconnected, while the operator confirms Wi-Fi works; whether it reconnected automatically was not established. |
| Bluetooth | Pass by operator report | Bluetooth was powered and neither soft- nor hard-blocked in the captured state. |
| Speakers | Fail | No audible output was reported. PipeWire exposed a speaker sink, but no default configured output was shown. A speaker-test stream remained listed after its timeout. No mixer changes were made. |
| Microphone | Input discovery failure; capture untested | GNOME Sound Settings showed no input device. An earlier PipeWire snapshot listed an internal microphone source, so the UI and PipeWire observations differ. No capture was performed. Earlier kernel messages included a missing VA Capture codec DAI and deferred DMIC pinctrl probes. |
| Camera | Discovery/capture unqualified | The available video nodes were identified as Qualcomm Iris decoder and encoder nodes, not camera-capture nodes. `v4l2-ctl` and `media-ctl` were unavailable; GStreamer found no video source. Kernel logs included an invalid CSI lane and Iris firmware initialization failures. No capture or privacy-LED check was performed. |
| RPMB | Registration pass only | The kernel logged UFS RPMB region registration with capacity 128. No authenticated read-counter request was made; key provisioning and RPMB data writes remain out of scope. |
| Storage and installation | Blocked | Kernel logs recorded USB transport failures, attempted writes, and an ext4 journal abort/read-only remount on an unidentified external filesystem. Its physical device was not mapped. No installer was run; the logs do not establish which attached media were affected or unaffected. Do not treat storage health as passed. |

## Qualification disposition

Wi-Fi, Bluetooth, and suspend/resume have operator-reported passes, with the
captured Wi-Fi state discrepancy retained above. Speakers remain silent;
microphone input discovery and camera discovery fail in the reported desktop
state. RPMB registration alone does not qualify RPMB transactions.

Do not start an installation or storage-health test until the USB/filesystem
errors are safely attributed and the connection is stable. Any future install
must use only the separately approved Apple HDD, after a fresh serial-bound
artifact/target/partition checkpoint and explicit approval. Keep SP12 internal
storage and other protected media out of scope. No firmware/NVRAM or RPMB
changes were made for this follow-up.
