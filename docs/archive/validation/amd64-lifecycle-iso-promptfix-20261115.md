# AMD64 lifecycle ISO rebuild with activation-prompt fix — 2026-11-15

**Recorded:** 2026-11-15 21:21 UTC / 14:21 MST
**Repository:** `feature/linux-chropic-psycachy-b550i-sp121` at `da3bb62`
**Result:** corrected candidate built and independently audited; new-hash VM
boot smoke and lifecycle sequence remain open.

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
(97.3 GiB), 17.3 GiB above the 80 GiB reserve. The previously observed full
disposable target allocation of 12,715,630,592 bytes would leave about
5.5 GiB above that reserve. The upcoming boot smoke uses fresh sparse QCOWs;
monitor capacity before any full installation or scenario that grows them.

No VM boot of this exact hash, disposable installation, activation,
acknowledgement, promotion, rollback, media replacement, Apple HDD write,
firmware change, or exact-hardware test has occurred. The next gate is a
network-disabled UEFI/KVM smoke of this exact hash, stopping at the guarded
disk selector. `/dev/kvm` is root-owned by group `kvm`; the current user needs
interactive sudo for KVM access. Do not select an installer target during
that smoke.
