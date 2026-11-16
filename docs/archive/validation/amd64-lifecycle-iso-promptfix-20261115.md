# AMD64 lifecycle ISO rebuild with activation-prompt fix — 2026-11-15

**Recorded:** 2026-11-15 22:45 UTC / 15:45 MST
**Repository:** `feature/linux-chropic-psycachy-b550i-sp121` at `da3bb62`
**Result:** corrected candidate built and independently audited; exact-hash
network-disabled KVM smoke passed to the guarded disk selector. Disposable
installation and lifecycle sequence remain open.

## Candidate identity

- Local ISO:
  `output/amd64-iso-lifecycle-20261115-promptfix/psycachy-ubuntu-26.10-desktop-amd64.iso`
- Size: 8,052,277,248 bytes.
- SHA-256:
  `1406eefc1b559ec8363827521ed15e3ced7410873bf7f3d329140a2a1b286c85`.
- The adjacent `SHA256SUMS` verifies. Its file SHA-256 is
  `f1ad648581384952a457f622e519519a5bffe0f4dcc7e93cb2655e1a307ce0ba`.
- Build log SHA-256:
  `ba6ea12df85b8b012bc279c4d5d9e487850c5622a0f054cbba2ddd4ab68648e0`.
- Build manifest SHA-256:
  `53f654aae46d3dc286168983b4bb66861eba7595e27a1b55d774f5c65a654f6d`.

The corrected image is local only. It has not replaced the AMD64 pre-fix ISO
on Ventoy. The SP12-only Ventoy approval does not cover an AMD64 replacement.

## Inputs and build

The build ran on Ubuntu 26.10 amd64 as root inside an unprivileged user
namespace. It wrote the new output directory and temporary `/var/tmp` scratch;
it did not install packages on the host or alter physical media. The command
was:

```sh
unshare --user --map-root-user -- bash iso/build.sh \
  output/iso-inputs-20261110/ubuntu-26.10-desktop-amd64v3.iso \
  output/.phase1-closeout-20261110T192001-0700/amd64-build \
  output/amd64-iso-lifecycle-20261115-promptfix \
  output/.unattended-luna-20261111135015Z/amd64-offline-repo
```

The Canonical-signed Ubuntu 26.10 amd64v3 base ISO is 6,298,435,584 bytes,
SHA-256 `16c9d9122160d901c78d0528cad4556c778701039ea2879b89483d4fd0c0d10b`;
`iso/verify-ubuntu-iso.sh` verified its detached signature. The exact pinned
7.3.1 package pair came from `output/.phase1-closeout-20261110T192001-0700/amd64-build`:

| Package | SHA-256 |
| --- | --- |
| `linux-headers-7.3.1-psycachy_7.3.1-1psycachy1_amd64.deb` | `cccd88818bdcbae2789d98725b754a9253744b42a2ec16458dbc0a424cb0b872` |
| `linux-image-7.3.1-psycachy_7.3.1-1psycachy1_amd64.deb` | `a3e89bb7091640abad457a55184555533a6cde72d6b79a78c97f1b25dc111fa6` |

These hashes match the active `znver3` kernel pin. The separate `phase2`
package directory contains a different, rejected pair and was not used. The
offline repository contains 282 packages; its sidecar verified, and the build
authenticated and checked the 280 Ubuntu packages against current signed
archive indexes.

## Build and independent audit

Builder checks passed, including the two GRUB kernel-command updates,
successful ISO creation, unchanged base `/EFI/boot` files and
`/casper/vmlinuz`, and a present UEFI boot record.

An independent read-only review passed these checks:

- The ISO hash/size and sidecar match this record.
- The embedded `activate.sh` byte-matches source SHA-256
  `3d2936990480078ca4326221adb1a333e65a53efa47ac1d10b1a1b2af5ecb50b`, and
  the build manifest binds that exact source path and hash. A harness sourced
  the embedded helper and confirmed blank promotion-path input exits nonzero
  before invoking the trial helper.
- All 13 lifecycle and installer helpers match their sources and manifest
  hashes. The embedded kernel pin and both kernel packages match the active
  configuration, repository checksums, and package-index metadata.
- All 282 embedded repository files match their `SHA256SUMS` entries.
- The three base EFI boot files and casper live kernel are byte-identical to
  the signed source ISO. The raw UEFI boot image bytes also match at the
  recorded LBAs, SHA-256
  `a581aa88b04c830922dff3ee5873918c89c80fe7db4c457ecc45314091e1a325`.
- Both BIOS and UEFI boot entries are present. The interactive autoinstall
  retains the serial-bound disk selector and guarded install flow.

The source-level prompt tests and static checks were run with the fix before
this build; they were not rerun here. This report records the builder and
artifact audits, not an installed-system result.

## Capacity and qualification boundary

Immediately after the build, local `/` had 104,519,655,424 bytes free
(97.3 GiB), 17.3 GiB above the 80 GiB reserve. After the KVM smoke, free space
was 104,746,668,032 bytes (97.55 GiB), 17.55 GiB above the reserve. The
previously observed full disposable target allocation of 12,715,630,592 bytes
would leave about 5.71 GiB above it. Monitor capacity during each lifecycle
scenario and stop before free space falls below 80 GiB.

No disposable installation, activation, acknowledgement, promotion, rollback,
media replacement, Apple HDD write, firmware change, or exact-hardware test
has occurred. The exact-hash network-disabled KVM smoke passed to the guarded
disk selector and stopped with its only listed target unchecked, as detailed
below. `/dev/kvm` is root-owned by group `kvm`; launching each KVM scenario
requires supervised interactive sudo.

## Follow-up — exact-hash KVM boot smoke

The corrected ISO was booted on 2026-11-15 with QEMU 11.0.3, KVM acceleration
and host CPU features, 2 vCPUs, 4 GiB RAM, no network, and a fresh insecure
OVMF variable store. It reached the Ubuntu desktop's guarded dedicated-disk
selector. The selector listed only `/dev/vda`, serial `psycachy-linux`, size
68.7 GB; its erase checkbox was clear. No target or install mode was selected.

The QEMU monitor reported the writable 64 GiB `linux.qcow2`, the separate
64 GiB `other.qcow2` attached read-only, and the ISO attached read-only.
`tests/iso-vm.sh verify-other` passed after shutdown, including the saved
sentinel checksum and 1 MiB pattern read. `qemu-img check` passed for both
QCOWs, and the candidate ISO's `SHA256SUMS` returned `OK`. The monitor's
`quit` command stopped QEMU; the process and port 4513 are closed.

Private local evidence remains under
`output/amd64-iso-liveboot-20261115-promptfix/`: the selector capture
`selector-screen.png` (SHA-256
`b2f14cd99dda5fad55f59001396974e771ef87428e4244ffdebd9c6ac33d7e10`) and
`serial.log` (SHA-256
`575fe3b7fce03fa94ddbbd45a9b640a2fea6ced38449167ae6b8f32747fca117`). The
protected disk remains intact at SHA-256
`b7f1ada63281ed7e5bc7127dffbfc4c91582fab3080133b01a966c7624d97bb6`.

This smoke used Secure Boot disabled and stopped before installation. It does
not qualify Secure Boot, installed-system boot, acknowledgement, promotion,
rollback, or physical B550I behavior. The next software gate is the separate
disposable install and lifecycle sequence; the corrected ISO remains off
Ventoy.

## Follow-up — Secure Boot install failure and NVIDIA parser fix

The exact ISO recorded above was used for a fresh disposable install attempt
on 2026-11-15 with QEMU 11.0.3/KVM, 2 vCPUs, 4 GiB RAM, no network, and the
Microsoft-signed OVMF firmware. The guest reported Secure Boot enabled and
kernel lockdown `integrity`; it booted the Ubuntu 26.10 live kernel
`7.3.0-9-generic`. Only disposable target `/dev/vda` (serial
`psycachy-linux`) was selected. The installer wrote to a standalone VM QCOW;
the protected sentinel disk and ISO were read-only.

The installer stopped in `/cdrom/psycachy/late-install.sh` with:

```text
offline repository must identify one matching NVIDIA driver/DKMS pair
PsyCachy installation: offline repository has no unique NVIDIA package pair
```

The actual repository contains one matching pair, both version
`615.71.09-0ubuntu1`: `nvidia-dkms-615-open` and
`nvidia-driver-615-open`. The builder and source had called
`dpkg-deb -f DEB Package Version`, whose output labels each value (`Package:`
and `Version:`); the inline parser treated the whole labeled lines as bare
values, so it rejected the valid pair. Package contents and their hashes were
verified. The source now parses those field labels and rejects duplicate
matching package names. The change was pushed as `d76342e`.

The new `tests/test_iso_nvidia_package_pair.py` exercises the installer’s
actual inline parser against real fixture packages, covering a matching pair,
a version mismatch, multiple matching pairs, and duplicate package names.
All four focused tests and `bash tests/static-check.sh` passed. An independent
source review found no remaining parser issue.

The failed run's evidence is retained under
`output/amd64-iso-lifecycle-run-20261115/`. The Secure Boot capture
`secureboot-live-check.png` has SHA-256
`598ba2ad721e07f7c4ba97b2cbbe5d89a39f2c7fadf5c20b06653c500ca87d3b`; the
installer error capture `install-failure-log.png` is
`bfcc8fe2fe8067f0e3fda3cd0b5c36c0f014a30b65b1cc3046328d3a7f8b2b6c`, and
`installer-log-failure.png` is
`5d2cf57f700249cbfbd2ddca77bffd11396ab4221cf63d8e4ca4989f52df8f6a`. The
serial log hash is `575fe3b7fce03fa94ddbbd45a9b640a2fea6ced38449167ae6b8f32747fca117`.
The standalone target QCOW was cleanly stopped and checked; its SHA-256 was
`db25c87ae9a8b3a02f921231bc5b80f949a8f2378e2e1e886542af2ff2e110d4`.
After shutdown, the protected sentinel still matched
`b7f1ada63281ed7e5bc7127dffbfc4c91582fab3080133b01a966c7624d97bb6`, and
both QCOW checks passed. No physical disk, USB, or host firmware/NVRAM was
written; only the disposable target QCOW and VM-local OVMF variables were
modified.

The disposable VM tree has since been removed. The previous ISO binary was
checksum-verified before retirement; its sidecar identity, build manifest and
build log remain. The separate failure screenshots, serial log and sentinel
evidence remain intact. The retired `1406eefc…` candidate was never on
Ventoy; the older pre-fix AMD64 ISO remains there and is still ineligible for
qualification.

The fixed source has been rebuilt into a new local candidate:
`output/amd64-iso-lifecycle-20261115-nvidiafix/psycachy-ubuntu-26.10-desktop-amd64.iso`,
8,052,277,248 bytes, SHA-256
`d463a31aaa0d2fbce293e38bed360f9d50770dceee344bed716bbc1d71d238fa`. Its
adjacent `SHA256SUMS` passes. Independent review confirmed that the manifest
records source revision `d76342ef29401e5081af4dccf8f497bbb4d7a1b9`; the
embedded `install-target.sh` matches source and its manifest hash
`e5c452e20be218401d95423664496a4f8c486c31406a3d62c9803de9abde87eb`. The
review extracted the offline repository and verified all 282 package
checksums, names, versions, and architectures against the manifest. The
embedded parser identified the unique `nvidia-dkms-615-open` and
`nvidia-driver-615-open` pair at `615.71.09-0ubuntu1`, with hashes
`8e0d84138e877eee24f5b7db3ed292ccd6e384f844776d19945e89d18f3bc0ec` and
`9efa45da9743159fd361e358c762a1b0cdbd410c7d9bd32f7bc23c8d63ed4dc8`. The
Canonical signature and pinned source ISO passed verification; the embedded
EFI directory and `/casper/vmlinuz` match the signed base. The review found no
artifact-integrity issue.

The successful build log includes non-fatal `dpkg-scanpackages` warnings
because the private repository uses no override file, APT cache-unlink
warnings from the unprivileged build namespace, and an xorriso warning that
the preserved Ubuntu volume label is not a strict ISO 9660 mount-point name.
The signed-base, package, index, and content checks all passed, and ISO
creation completed successfully.

The reviewer’s 1.7 GB `/tmp` extraction was removed with sudo after the
extracted EFI files proved root-owned. A fresh VM directory was initialized
with a new empty 64 GiB target QCOW, a 64 GiB sentinel QCOW, and fresh
Microsoft-signed OVMF variables. The user launched the new ISO under QEMU
11.0.3/KVM with 2 vCPUs, 4 GiB RAM, and no network. Serial output first
showed the signed GRUB menu; a subsequent VNC capture reached the guarded
dedicated-disk selector. It lists only `/dev/vda` (`psycachy-linux`, 68.7 GB)
and the erase checkbox is clear. No target was selected and installation had
not started. VNC display :14 and monitor port 4514 are active. The selector
screenshot is retained at
`output/amd64-iso-lifecycle-run-20261115/secureboot-fixed-candidate-selector.png`,
SHA-256 `f634de971e7dc4f13394c9737d1ade48d7aaad06a4be7b9dd66db0f4cb13d013`.
It shows only `/dev/vda` (`psycachy-linux`, 68.7 GB) with the checkbox clear.
Root free space before boot was 104,606,810,112 bytes (about 97.44 GiB),
17.44 GiB above the 80 GiB reserve. Continue only on the fresh disposable
target and preserve the reserve throughout the install and later lifecycle
scenarios. This candidate remains local and has not been staged on Ventoy or
physically booted.

## Follow-up — fixed candidate install and detached first boot (2026-11-15 17:47 MST)

The exact parser-fix ISO, 8,052,277,248 bytes with SHA-256
`d463a31aaa0d2fbce293e38bed360f9d50770dceee344bed716bbc1d71d238fa`, passed
its adjacent `SHA256SUMS` check. It was installed in a fresh 64 GiB disposable
QEMU target under QEMU 11.0.3/KVM, 2 vCPUs, 4 GiB RAM, no network, and the
Microsoft-signed OVMF profile. The installer target was only `/dev/vda`, serial
`psycachy-linux`; its review screen showed a FAT32 EFI partition and ext4 root
partition. The separate 64 GiB `psycachy-other` sentinel disk and ISO were
read-only. First-install mode was used, and the installer reached
“Ubuntu 26.10 is installed and ready to use” without the prior NVIDIA-pair
parser error.

After the completion prompt, the ISO was forcibly ejected through the QEMU
monitor and the VM restarted. Firmware booted `Boot0005 Ubuntu` from the
installed disk's `\EFI\ubuntu\shimx64.efi`; the guest reached the
`vmtest` GDM login screen without attached installation media. The screenshot
is retained at
`output/amd64-iso-lifecycle-run-20261115/secureboot-fixed-installed-first-boot.png`,
SHA-256 `5a7d3c7a3dff354dfdf16697a4c594231c02cb993254c49da506d7c253cbc48f`.
The initial KVM serial log is
`output/amd64-iso-lifecycle-vm-20261115-nvidiafix/serial.kvm-install.log`,
SHA-256 `620d5994f3587134a6882a9e07d95f229210b704bf727634b1b582b3b4e9d52f`.

The 64 GiB virtual target QCOW occupies 13,338,107,904 bytes. `qemu-img check`
reported no errors, and `tests/iso-vm.sh verify-other` returned `OK`
for both the sentinel hash and its 1 MiB pattern. The VM was shut down through
the monitor. A later disk-only TCG run also reached the installed login screen
and was shut down cleanly; its serial log hash is
`11951fc1dc85fbb0a7abe23a4571da980dacbb0cbeb091aa384458f61309e9de`.
Local `/` had 91,200,782,336 bytes free (85.0 GiB), about 5 GiB above the
80 GiB reserve. Continue to monitor before allocating further lifecycle
overlays or backup payloads.

This closes the exact candidate's disposable first-install and detached
first-boot gates. It does not by itself record `mokutil --sb-state`, installed
kernel lockdown, `module.sig_enforce`, MOK enrollment/trust, candidate kernel
activation, acknowledgement, promotion, timeout rollback, explicit rollback,
replacement mode, tamper refusal, or physical B550I behavior. The installed
guest's Secure Boot and module-trust state remains unverified. The image is not
staged on Ventoy or physically booted; no physical disk, media, or host
firmware/NVRAM was written. See the [current continuation report](supervised-continuation-20261115.md)
and [qualification ledger](../../PRIVATE-PILOT-QUALIFICATION.md).

## Follow-up — repeat media boot and installer failure (2026-11-15)

After the detached installed-disk boot, the same ISO was reattached read-only
to try to reach a live session without using the guest account. The UEFI boot
manager selected the QEMU DVD device and GRUB's `Try or Install Ubuntu` entry.
The GUI relaunched the guarded installer and displayed:

```text
Installation failed
A command in the autoinstall file failed to run during installation.
```

No detailed installer log or screenshot of this error was retained. I did not
intentionally confirm a second erase/install. The ISO source audit explains
why the installer relaunched: `iso/build.sh:65-82` adds `autoinstall` to both
GRUB Linux entries, and the ISO has no live-only entry. The selector in
`iso/select-disk.py:183-221` requires an explicit disk, mode, and `ERASE`
confirmation before configuring storage. The exact command failure and the
extent of any virtual-target writes remain unknown.

I ejected the ISO and restarted from the installed disk. The guest again
reached the `vmtest` GDM screen. The retained serial log for this media/reboot
attempt is
`output/amd64-iso-lifecycle-vm-20261115-nvidiafix/serial.kvm-live-media-retry.log`,
SHA-256 `814c7ae6d32b9daf7634c760a576b6400b8b67943695f6472792ecaa451ee741`;
the GUI installer failure itself is not present in that serial log. After
shutdown, `qemu-img check` reported no QCOW errors and
`tests/iso-vm.sh verify-other` again passed the protected disk hash and 1 MiB
pattern. The target still boots, but its package state and post-attempt disk
contents have not been audited. Its QCOW length is now 13,369,409,536 bytes,
31,301,632 bytes above the previously recorded post-install length; this
change is not attributed to the installer without a sector-level comparison.

For a safe one-boot live-session attempt, edit the GRUB kernel line and remove
`autoinstall` before booting. This was not done during the failed re-entry.
Local `/` had 91,159,805,952 bytes free at the post-run check (about 84.9 GiB,
4.9 GiB over the 80 GiB reserve). No physical disk or media was touched.
