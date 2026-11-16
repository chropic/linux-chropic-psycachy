# SP12 live-boot diagnostics — 2026-11-16

`diagnostics.txt` preserves the user-provided terminal output. The captured
r2 kernel and runtime DTB ID match the final51 pins. The live ISO is mounted
read-only at `/cdrom`; `/rofs` is read-only squashfs and `/cow` is the live
writable overlay. The `lsblk` output shows the 476.7 GiB `sda` device and its
partitions with no mount points. No external installation, device-function
matrix, RPMB write, or write-counter capture is included in this record.
