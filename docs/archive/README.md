# Evidence summaries

Use the [release backlog](../BACKLOG.md) for decisions. These summaries retain
the observations that guide the next test. Raw logs, screenshots, inventories,
binary artifacts and original dated reports stay in private storage.

## B550I boot

The C test ISO contains the audited packages, but its live entry uses Ubuntu's
kernel. A physical Ventoy boot ended with PID 1 exit `0x00000100`; the selected
entry and preceding console were not captured. A historical VM installer reboot
ended with `0x0000000b`. A later boot from an overlay reached login but did not
repeat installation. Compare like-for-like: continuous console, same-session
installer reboot and kernel identity at each stage.

## Surface boot and recovery

The selected C kernel and DTB booted on hardware. Under QEMU `virt`, the Surface
DTB reached a PSCI/SMC panic; the generic guarded installer path reached disk
selection after fixing its autoinstall config path. The writable target appeared,
the read-only sentinel did not, and no disk was selected. Neither result
qualifies the full install. A firmware entry starting also does not prove Linux
booted. Verify the ESP kernel/initramfs/DTB, read-only remount and manual rescue
on the selected candidate; VM fault injection cannot establish flash durability.

## Surface peripherals

The internal camera pattern returned 30 buffers; neither physical sensor
returned a frame. Compare baseline and lane-map fix with unchanged userspace.
The named speaker/mic endpoints existed but default routing pointed at absent
`auto_null`. Use an explicitly targeted quiet playback stream, then direct ALSA
if needed; distinguish an advancing hardware pointer from audible sound. Test
mic capture separately with consent; retain signal metrics rather than recordings.
A successful resume with PCIe/hwmon warnings is not a clean resume result.

## Performance fixtures

Run ≥3 interleaved reference/candidate pairs with equal work, policy, thermal
conditions and peripherals. Use 30-minute idle, 20 fixed editor operations on a
64 KiB fixture, 20-minute local 1080p30 H.264 playback, fixed `make -j4` plus
editor, full `make -j$(nproc)`, and 15-minute suspend. Validate output hashes and
resume function. The desktop UPS yields estimated Wh only; unavailable Surface
whole-system telemetry must be reported as unmeasured.
