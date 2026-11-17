# SP12 live hardware check — 2026-11-16

## Evidence basis

This report summarizes terminal captures and operator observations from the
SP12 live session on 2026-11-16. The source captures were supplied in the
conversation and are not committed as raw files. Results without a complete
machine-readable capture are identified as operator-reported. Device serial
numbers and the Wi-Fi network name are omitted because the repository is
public.

## Boot and safety state

- The SP12 booted from the staged final51 combined live USB and reached the
  desktop on kernel `7.3.1-psycachy-sp121-r2`. The supplied boot diagnostics
  reported the expected device model and DTB build ID. `/sys/firmware/fdt` was
  absent, so the exact FDT passed to the kernel remains unverified. No
  in-session ISO hash was captured.
- `/` was the live overlay; `/rofs` and `/cdrom` were read-only. The earlier
  `/cow is not a mountpoint` message is consistent with `/cow` being the
  overlay's backing directory, not a separate mount.
- The `efi=noruntime` boot showed the non-fatal efivars/runtime warning; the
  live session continued. No EFI-variable or persistent boot-order change was
  made during this check.
- The internal disk's two partitions had no mountpoints. The Ventoy USB was
  active at `/cdrom`; the separate UDisk was present but unmounted. No internal
  disk or UDisk write was performed.

## Hardware results

| Area | Result | Evidence and limits |
| --- | --- | --- |
| Wi-Fi | Pass (operator-reported) | Wi-Fi connected after being unblocked; network name omitted. |
| Bluetooth | Pass (operator-reported) | User tested Bluetooth and reported it works. |
| USB | Enumeration pass | `lsusb` showed USB hubs, the ASIX USB Ethernet adapter, and two flash-storage devices. `lsblk` distinguished the live Ventoy media from the separate unmounted UDisk. This was not a storage throughput or health test. |
| Internal storage protection | Pass for this session | Internal partitions remained unmounted; no internal-disk writes were reported. |
| Built-in speakers | Fail | User repeatedly reported no audible output. PipeWire eventually exposed `Built-in Audio Speaker playback` (sink ID 45), and an active 440 Hz stream appeared in the earlier capture. The initial active-stream mixer capture showed both WSA speaker DAC switches off and the right `MultiMedia1` channel off. No final mixer readback was captured after the later route attempt, so the last control state is unknown. |
| Microphone | Not tested | PipeWire listed the internal microphone source, but no capture test was performed. |
| Camera | Fail for application discovery | `/dev/video0` and `/dev/video1` existed, but the camera application reported no cameras. `v4l2-ctl` was not installed; no package was installed and no camera capture was verified. |
| Battery and charging | Initial critical reading; charging later operator-confirmed | UPower first reported 6% and discharging, about 19 minutes remaining, with all AC inputs offline and critical action `Sleep`. The user connected the charger and confirmed the system reported online and charging; a refreshed raw power capture was not supplied. |
| Suspend/resume | Pass (operator-reported) | After connecting the charger, the user suspended and resumed the live session successfully. |

## Audio troubleshooting record

The first PipeWire capture showed a speaker sink and active `speaker-test`
stream, with both WSA884x SoundWire endpoints `Attached`. The sink's software
volume was not muted, but the active-stream ALSA snapshot showed
`SpkrLeft DAC` and `SpkrRight DAC` off, with the right `MultiMedia1` channel
off. After restarting user audio services, PipeWire temporarily exposed only
`Dummy Output` while ALSA still listed the X1P42100 playback PCM. The ALSA UCM
card was visible as `hw:0`, and the Surface UCM file mode was `0644`. Selecting
the HiFi profile restored the speaker sink and microphone source, but did not
restore audible speaker output.

The installed `wpctl` command did not support `get-profile`. The suggested
placeholder `SINK_ID` was entered literally and the `set-volume` command
failed as an invalid number; numeric sink ID 45 was then supplied, but no
successful command output or final mixer readback was captured. The user
continued to report no sound after the route-test instructions. The session
did not establish the remaining kernel, SoundWire, UCM, or amplifier cause.
Speaker troubleshooting was stopped at the user's request.

## Remaining qualification

- Keep speaker output and camera discovery marked failed for this live boot.
- Microphone capture, camera capture, storage health, RPMB behavior, and
  installation remain untested in this session.
- The live-session tests do not qualify an installed system or establish the
  exact ISO bytes loaded by firmware.
