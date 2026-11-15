# Restored-target generic QEMU userspace control

**Observed:** 2026-11-14.  
**Result:** the restored target root reached `getty.target` and a serial login
prompt under generic QEMU EFI/ACPI after interactive RAM-only GRUB commands
loaded its kernel and initrd without a DTB. The guest shut down cleanly after an
ACPI powerdown request. No account login or authenticated session occurred.
This does not qualify the restored Surface DTB, automatic default entry, or
physical SP12 recovery boot.

## Findings

- A display-enabled disposable COW boot confirmed UEFI BootNext starts
  `BOOTAA64.EFI` and GRUB 2.14 reaches a prompt. `ls` and `echo $root` showed
  the restored `/boot` filesystem as `(hd2,gpt13)`. A read-only GRUB `cat`
  captured `/grub/grub.cfg`: the hidden zero-timeout default names kernel
  `7.3.0-10-generic`, its matching initrd, and a DTB. Its root filesystem UUID
  is `493aa442-e2db-4f46-87aa-5bc45cff581a`; its `/boot` filesystem UUID is
  `437cff80-1529-44a3-b605-a5f5e3d68e46`.
- Manually issuing `configfile (hd2,gpt13)/grub/grub.cfg` produced no further
  serial marker. After 4:21 with QEMU still running and no kernel/userspace
  evidence, QMP `system_powerdown` left it running; QMP `quit` stopped this
  probe. The root and data top COWs passed `qemu-img check` and remained at
  their initial 256 KiB metadata size.
- A separate fresh-variable run used the pre-existing disposable ESP copy
  whose stub path is corrected to `configfile ($root)/grub/grub.cfg`. UEFI
  again logged the exact BootNext partition GUID and started the loader, but
  the serial log stopped at the GRUB EFI screen. After two minutes, QMP
  `system_powerdown` did not stop the VM; QMP `quit` ended this bounded probe.
  It does not establish that the hidden default entry ran.
- In the generic-platform control, fresh root and data COWs and a fresh copy of
  the recorded AAVMF variable store were used. With QEMU `virt`, TCG,
  `virtualization=on`, `-nic none`, and 2 GiB RAM, RAM-only GRUB commands loaded
  `/vmlinuz-7.3.0-10-generic` and `/initrd.img-7.3.0-10-generic`, set
  `root=UUID=493aa442-e2db-4f46-87aa-5bc45cff581a`, enabled PL011 serial
  diagnostics, and omitted the `devicetree` command. The kernel reported EFI
  ACPI tables and mounted the restored root by its UUID. Its log shows the
  filesystem initially mounted `ro`, then `EXT4-fs` remounted it `r/w`; the
  `systemd-remount-fs.service` unit also completed. Systemd mounted `/boot`,
  `/boot/efi` (restored ESP UUID `C1D2-E253`), and `/mnt/sp12-data`.
  It reached `getty.target` and printed `sp12-phase1-vm login:`. No credentials
  were sent. An ACPI powerdown request led systemd to unmount the filesystems,
  reach `poweroff.target`, and print `reboot: Power down`.

## Integrity and scope

The runs attached no network. All root/data writes went to fresh top COWs; the
restored ESP was read-only. Pre/post hashes matched for the source root/data
QCOW tops, source ESP, source AAVMF variables, and firmware code; the corrected
disposable ESP hash was also checked after the run. A separate post-run audit
matched all retained root backing-chain and data-fixture hashes to the prior
full-input manifest. All six new root/data COWs passed `qemu-img check`.
The complete `/var/tmp` run directory peaked at 227,812,118 bytes, under its
2 GiB scratch cap. Commands, input hashes, COW checks, hashes, and raw serial
logs are retained beside this report.

The generic control establishes that the restored root, boot partition,
restored ESP, and data mount can reach ordinary systemd userspace under QEMU's
generic EFI/ACPI platform when the Surface DTB is omitted. It does not verify
`dpkg --audit`, runtime payload hashes from inside the guest, execution of the
automatic hidden default entry, DTB/device-tree compatibility, Secure Boot,
physical SP12 boot, or hardware behavior. The old ESP path mismatch remains a
disposable-fixture issue; its automatic corrected-stub handoff was still
serial-silent in the bounded probe.
