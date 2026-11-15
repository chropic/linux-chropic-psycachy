# Attempt-7 detached-boot diagnosis

**Observed:** 2026-11-14, 09:39–10:12 UTC  
**Result:** in a reconstructed COW, interactive RAM-only GRUB commands loaded the installed 7.3.1 kernel, initrd, and SP12 DTB; the run did not prove execution of the hidden zero-timeout default entry. The SP12 DTB does not describe QEMU `virt`; it causes early kernel failures there. With the SP12 DTB omitted, the same kernel and initrd boot the installed Ubuntu 26.10 root under QEMU's generic EFI/ACPI platform and reach the serial login prompt. No account login or authenticated session occurred. This does not qualify a physical SP12 boot or establish what happened during the original detached attempt, whose vars file is missing.

## What was established

- A fresh COW boot displayed the GRUB 2.14 menu after UEFI Boot0006 started `\\EFI\\ubuntu\\shimaa64.efi`. The unmodified no-media run remained at an inactive display through its 300-second limit. Its serial log stayed quiet after the shim handoff because the installed entry routes output to `tty0`.
- With a USB HID keyboard attached, an interactive GRUB command line found the installed root UUID `e9f6f469-4d8f-49f0-9a0d-00098d623055`. GRUB loaded `/boot/vmlinuz-7.3.1-psycachy-sp121-r2`, `/boot/initrd.img-7.3.1-psycachy-sp121-r2`, and `/boot/dtb-7.3.1-psycachy-sp121-r2`; `post-linux`, `post-initrd`, and `post-dtb` markers returned. The run used RAM-only GRUB commands and a temporary PL011 diagnostic command line.
- With default `virt` PSCI behavior and the SP12 DTB, the kernel identified `Surface Pro 12in 1st Edition` and faulted on `__arm_smccc_smc`, then panicked. This is consistent with the DTB's SMC PSCI conduit not matching the default QEMU virtual CPU configuration.
- Repeating with QEMU `virtualization=on` made PSCI v1.1/SMC initialize. The SP12 DTB then reported no GIC distributor at `0x17000000`, no usable timer, and PSCI failures for CPUs 1–4; the kernel faulted in `__ipi_send_mask` while sending an IPI. This localizes the remaining failure to the SP12 hardware description versus the QEMU `virt` device map.
- In a separate COW run with `virtualization=on`, the same kernel and initrd booted without issuing GRUB's `devicetree` command. The kernel used the generic EFI/ACPI platform, initialized PSCI, GICv3, and the virtual timer, switched to the installed Ubuntu 26.10 root, started systemd services, and printed `psycachy-test-QEMU-Virtual-Machine login:` on `ttyAMA0`. No username or password was entered.
- The GRUB command `insmod part_gpt` printed that `/boot/grub/arm64-efi/part-gpt.mod` was missing. `insmod ext2`, UUID search, and the kernel/initrd/DTB load commands still succeeded in the interactive run. Keep this as a separate packaging/configuration item; it was not the observed kernel failure.

## Run conditions and limits

All QEMU runs used TCG, four CPUs, 8 GiB RAM, no network (`-nic none`), a read-only sentinel, and a fresh writable child of the retained attempt-7 overlay. The generic ACPI comparison omitted the installed SP12 DTB; it tests generic kernel/rootfs startup only. The diagnostic kernel command line was `root=UUID=e9f6f469-4d8f-49f0-9a0d-00098d623055 ro console=ttyAMA0,115200 earlycon=pl011,0x09000000 loglevel=8 rd.debug`.

The historical attempt-7 command names `vars-detached.fd`, which is absent. These follow-ups cloned the retained `vars.fd` (SHA-256 `ac2f68d7a767d5e79b55528c739e30707b462f129d7151d43f18cc88cdd1b1ae`) into each run directory. They therefore reconstruct the UEFI state and do not claim byte-for-byte replay of the missing detached-run variables file.

After shutdown, each of the four reported boot-run top COWs passed `qemu-img check`; the retained base, backing overlay, firmware code, vars source, and sentinel hashes matched the recorded inputs. The sentinel remained `b7f1ada63281ed7e5bc7127dffbfc4c91582fab3080133b01a966c7624d97bb6`. The largest run directory allocation was 50,982,912 bytes, below its 256 MiB cap. Root and `/var/tmp` had 96,785,928,192 bytes free after the runs, about 10.1 GiB above the 80 GiB reserve. No credential or update seed was used, no network was attached, and no backing image or physical disk was written.

## Qualification boundary

The old “shim → GRUB” uncertainty is resolved for this reconstructed COW: UEFI, shim, GRUB, kernel, and initrd execution were observed. The exact installed SP12 DTB cannot be meaningfully qualified on generic QEMU `virt`, whose GIC/timer map differs. The generic ACPI run proves the installed kernel/initrd/rootfs reach userspace in that virtual environment only. Native SP12 boot, exact r2 runtime identity on hardware, and all physical acceptance checks remain open.

## Retained evidence

- `unmodified-no-media-serial.log`, `unmodified-grub-menu.png`, and `unmodified-post-handoff.png`
- `target-dtb-default-conduit.serial.log`, `target-dtb-default-conduit-display-inactive.png`, and `run-target-dtb-default-conduit.sh`
- `target-dtb-smc-conduit.serial.log`, `target-dtb-smc-conduit-display-inactive.png`, `target-dtb-grub-load-markers.png`, and `run-target-dtb-smc-conduit.sh`
- `generic-acpi-handoff.serial.log`, `generic-grub-console.png`, `generic-grub-root-found.png`, and `run-generic-acpi-handoff.sh`
- `source-inputs.sha256`, `sentinel-precheck.txt`, and `postrun-checks.txt`
