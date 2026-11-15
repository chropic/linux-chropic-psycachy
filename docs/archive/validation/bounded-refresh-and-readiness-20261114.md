# Bounded refresh and qualification readiness report

**Work date:** 2026-11-14 (America/Denver)  
**Media inventory:** 2026-11-15 00:56 UTC / 2026-11-14 17:56 MST  
**Local storage sample:** 2026-11-15 00:57 UTC / 2026-11-14 17:57 MST  
**SP12 remote storage sample:** 2026-11-15 00:06 UTC  
**Baseline:** `bb3fc379862271bcfdd8715564990f1073b7df83`

Report, source, and regression-log digests are recorded in the
[SHA-256 manifest](bounded-refresh-and-readiness-20261114.sha256).
The starting tracked diff, untracked paths, worktree inventory, and HEAD are
preserved in the [baseline snapshot](../../../.agents/wave-a/baseline-preservation/checksums.sha256).

## Decisions and evidence

### CachyOS 7.3.4 refresh

The exact `cachyos-7.3.4-1` source archive was authenticated with the
repository-pinned Peter Jung fingerprint
`E8B9AA39F054E30E8290D492C3C4820857F654FE`. The source archive SHA-256 is
`695c641edd5df9848f931c06bf97a30734e5f28910367937d5fea235cfd39535`; the
detached signature SHA-256 is
`ec286ac98c4fae149dfb97f88505e80ed54a9e96f867f678107875e47f5e21c6`. The tag
peels to `779ca9af71579431ca932a13a7c2ed5934b289ad`, and the source reports
Linux `7.3.4`.

An ordered replay of all 51 pinned SP12 patches applied 50 entries and failed
at entry 46, `patches/r2/video/02-iris-context-bank-devices.patch`. The
failure is in `iris_probe.c`. CachyOS 7.3.4 already reserves the non-pixel
IOVA range on the Iris parent device; the downstream patch adds context-bank
child devices and changes the same probe/remove/error lifetime. This requires
a reviewed DMA/IOMMU reconciliation. The follow-on patches 47–51 apply in
the diagnostic sequence with entry 46 omitted, but the complete series does
not apply. Compatibility work stopped after about 20 minutes of the 120-minute
budget; no config migration, compile, schema validation, package build, or pin
change ran. The review therefore selects the existing authenticated
7.3.1/final51 candidate and leaves 7.3.4 deferred. The report and complete
ordered replay are [here](cachyos-7.3.4-compatibility-20261114.md) and
[here](cachyos-7.3.4-ordered-replay-20261114.md).

An independent ordered replay reconciliation confirmed that entries 47–51
apply after their actual predecessors when entry 46 is skipped diagnostically.
It withdrew earlier pristine-source spot checks of entries 47–49 because
those patches depend on prior series changes. The sole replay blocker remains
entry 46; applying later patches does not make the full series complete.

The signed source archive, detached signature, and verification record are
preserved under
[`phase0-work/authenticated-sources/cachyos-7.3.4-1/`](../../../phase0-work/authenticated-sources/cachyos-7.3.4-1/).
The temporary extracted source trees and their GPG home remain under `/var/tmp`:
the shell safety guard rejected their recursive removal after open-file,
process, and mount reviews passed. No kernel source, patch, config, package,
or release pin was changed.

### AMD64 architecture target

The retained AMD64 kernel build is already specialized for Zen 3: build
metadata tied to the ISO-pinned package hashes records a Ryzen 7 5800X3D build
host and Clang's effective `znver3` target. The package pin also declares
`cpu_target: znver3`, and the saved resolved config enables
`CONFIG_X86_NATIVE_CPU=y`. No change to the AMD64 architecture label or
compiler target is needed. The audit found a reproducibility gap: the build
uses `-march=native` and does not fail if that resolves differently from the
pin. The currently running B550I kernel's saved config hash also differs from
the ISO-pinned config, so the exact pinned candidate is not claimed as the
installed image. See the [Zen 3 audit](amd64-zen3-target-audit-20261114.md).

### Storage and physical media

- The Apple HDD is now attached at `/dev/sdb`: `APPLE HDD HTS545050A7E362`,
  serial `TNS519GY1G6JGG`, 500,107,862,016 bytes. Its prior ext4 partition was
  inspected read-only, then unmounted. Partition 3 is ext4 label `writable`
  and contained only `lost+found`; partition 2 is EFI. Historical ISO9660
  metadata is present, but the current raw image prefix was not rehashed in
  this pass. No block or filesystem writes were made. The user authorized
  sequential reuse as the B550I external target; archive the needed current
  device evidence and use its supervised write checkpoint before installation.
- The separate USB enumerates as `/dev/sdc`, `UDisk`, reported serial
  `General_UDisk-0:0`, 14.6 GiB. It is mounted as Ventoy and already contains
  two large ISO files; only 2,353,856,512 bytes were free. Its SP12 ISO has
  size 4,971,847,680 bytes and SHA-256
  `d550c05575196069bd458f3a97c04acfc6660ceb4cdb5e7b7dab37879b6b6ec5`,
  matching its sidecar. Its buildinfo is dated 2026-10-24, says target kernel
  `7.3.0-sp12-v7.3-platform`, and labels installation testing experimental.
  It is not the final51 live ISO and has not been independently boot-tested.
  The other AMD64 ISO is 8,366,061,568 bytes, SHA-256
  `8caac7f32e750566c5676940364b40ce37d765f6a945feb5ad2ae43baf4b0870`, and
  differs from the selected lifecycle ISO. The stick is preserved; no media
  write was made. Its existing contents
  leave too little free space to copy final51. The protected Lexar BIOS-rescue USB, serial
  `AA8AGLJAH1RZABDT`, remains untouched. The [USB inventory and archived
  sidecar/buildinfo](artifacts/usb-ventoy-inventory-20261114/inventory.md)
  preserve the observed identities.
- At 2026-11-14 17:57 MST, `/` and `/var/tmp` had 88,315,269,120 bytes free
  with the compatibility scratch trees still present. A prior full AMD64 installer
  VM used 12,715,630,592 bytes; local free space cannot accommodate that
  allocation while retaining the 80 GiB reserve. The native SP12 builder had
  18,877,718,528 bytes free, below its 24 GiB minimum before accounting for
  the base-ISO snapshot and final output. No remote cleanup candidate was
  certified safe, and no remote files were deleted.
- The exact SP12 support checkout at commit
  `ea0f07e66beea95898d96fbeb6daa472f4735af3` in the `source/` subdirectory,
  and four pinned machine files were
  recovered under
  `phase0-work/private-inputs/sp12-r2-live-support-recovery-20261113/`:
  `board.bin` (`0ef5f6f3cb124f33c6de52371819ccd7c13763ceb86d476a178fd56e4cdc26a3`),
  `X1P42100-Microsoft-Surface-Pro-12in-tplg.bin`
  (`89b731f3f98fc2b84699bca39e56e390925a44a26d5aea80382cf617e00c08d8`),
  `MICROSOFT-Surface-Pro-12in.conf`
  (`171acda75bba76cc47bd258de7cfabe9474382c76e994e8c8164496b00bb50d1`),
  and `Surface12in-HiFi.conf`
  (`76eec2a1f34b9bea9c36c76a75de24c83d8840f73c57dadf1ed397bb5063edaa`).
  The expected checkout path is absent on the remote host; the recovered
  local copy has not been transferred because remote space is below the build
  gate.
- The local host has `/dev/kvm` and `qemu-img`, but `qemu-system-x86_64` is not
  installed. The AMD64 lifecycle VM was not repeated; disk capacity would
  still be insufficient for its observed target allocation while preserving
  the reserve.
- Tailscale SSH to `cs-sp12` completed after the user approved the Tailscale
  authentication check. Tailscale validated the host's advertised SSH key
  ([Tailscale SSH documentation](https://tailscale.com/docs/features/tailscale-ssh));
  no SSH host-key bypass or replacement was used.

### Approved Ventoy USB refresh (2026-11-15)

After the original inventory above, the user authorized replacing both
existing ISO files on `/dev/disk/by-id/usb-General_UDisk-0:0`. The selected
AMD64 lifecycle ISO and SP12 final51 image were copied to the existing Ventoy
filesystem; each destination was read back in full and matched its source
SHA-256. The old ISO identities remain recorded in the inventory, both new
sidecars/build information are retained, and the Ventoy partition table and
filesystem were preserved. The USB now has 2,828,926,976 bytes free after
metadata copies. At media-staging completion, no firmware selection, boot
test, Apple HDD write, installation, or internal erase had occurred. The user
later reported that the AMD64 ISO booted into the B550I installer with a
generic live kernel, recalled as `7.3.0-9-generic`; this does not establish the
installed candidate's `znver3` kernel, and no exact uname/selector-state record
was captured. Firmware showed a new UDisk entry in `BootOrder` after the
one-time boot; the original `0000,0002,0004` order was restored and verified.
The detailed [write record](artifacts/usb-ventoy-inventory-20261114/write-record.md)
and updated [qualification ledger](../../PRIVATE-PILOT-QUALIFICATION.md) track
the result. The Apple HDD subsequently reappeared at the exact stable ID
`/dev/disk/by-id/ata-APPLE_HDD_HTS545050A7E362_TNS519GY1G6JGG`, 465.8 GiB; it
is unmounted and identified, but its current raw ISO prefix was not rehashed
under the available account. The prior direct-I/O read-back record and exact
corrected source remain available, and no installation write has occurred. A
later exact serial-bound B550I external-install checkpoint was presented; the
user chose to hold it for now, so the Apple HDD remains unchanged.

## Regression record

Focused changed-behavior regressions passed:

- `python3 tests/test_phase2_kernel_trial.py`: 38 tests.
- `python3 tests/test_iso_select_disk.py`: 8 tests.
- `python3 tests/test_iso_late_logging.py`: 1 test.
- `python3 tests/test_sp12_live_builder.py`: 16 tests.
- `bash tests/static-check.sh`: passed; 71 recorded configuration changes
  checked, root-only `mokutil` check skipped.

Logs are retained in `.agents/wave-a/`:

| Log | SHA-256 |
| --- | --- |
| [phase2 kernel trial](../../../.agents/wave-a/test_phase2_kernel_trial.log) | `43ff599e3cdf3e4e44ad94187eeeaf115159ccc46a932c242526bfa7f8d9e3ab` |
| [ISO late logging](../../../.agents/wave-a/test_iso_late_logging.log) | `0cec8af754af3e47aa44b22ec8ef1b7cf04e57d8213ee4b7ff83a80eb5aeca8d` |
| [ISO disk selector](../../../.agents/wave-a/test_iso_select_disk.log) | `133449d6f429f0588126e0403937f271f33f90517460d5c4b39d69c2eeda0f25` |
| [SP12 live builder](../../../.agents/wave-a/test_sp12_live_builder.log) | `15dbe03505bcc696bc21aaf450f7d6692c3aee41cbef16cf1db25819466a9ef8` |
| [static check](../../../.agents/wave-a/static-check.log) | `4718cf5d8db5af437653c88e602249ad50debe91cfc4bd9c2d325069f2bfd700` |

## Remaining gates

The existing AMD64 lifecycle ISO reached its guarded installer selector, but
the disposable install/activation/acknowledgement/promotion/rollback sequence
is not complete. Physical B550I Secure Boot, NVIDIA, graphics, networking,
audio, suspend, update, and fallback checks remain open. The final51 SP12
installer and combined live image have not passed native SP12 live startup and
installed-system checks. The separate USB has not been confirmed as a
disposable rescue target, and its current free capacity is insufficient for
another final51 image. No B550I or SP12 fresh installation, firmware change,
RPMB write, or internal erase occurred in this pass.
