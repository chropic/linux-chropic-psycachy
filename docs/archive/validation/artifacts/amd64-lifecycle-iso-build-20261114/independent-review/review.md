# Independent review: AMD64 lifecycle ISO build2

## Result

No mismatch was found in the inspected final ISO payload. The artifact hash and size match the supplied identity; all selected extracted lifecycle files, pin, and kernel packages match their current local source/input bytes. The final GRUB file matches the exact transform in `iso/build.sh` applied to the authenticated Ubuntu base ISO's GRUB config.

There is one build-manifest traceability omission: `manifest.txt` records `M tools/phase2-kernel-trial.py` in the working-tree status but does not record a hash line for that helper, even though `iso/build.sh` copies it into the ISO. Independent extraction shows the embedded helper equals the current local helper byte-for-byte (SHA-256 `35e0f892caff684a704b95567b514fb0ea4dd6b395efa068a5337fd2dbb79372`). Thus this is a source-manifest omission, not an observed payload mismatch.

## Artifact and checksum verification

- ISO: `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso`
- SHA-256: `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`
- Size: `8,052,277,248` bytes
- `sha256sum -c SHA256SUMS`: pass; the file contains the ISO hash above.
- `manifest.txt`: SHA-256 `94be983994c7155a764f7cdf434983193055f316ff222f11902232585bf65d7b`
- `build.log`: SHA-256 `a03563b6d1fc7d21efe1f411679776abcee753ed58e2ff6d3f90e7f2e5aef0f0`
- Hash-checked manifest source entries: 316 checked, zero mismatches, zero skipped. Full result is `manifest-source-check.txt`.
- Offline repository `SHA256SUMS`: all 282 package artifacts pass, including the two pinned custom kernel packages. Full result is `offline-repo-check.log`.

The signed Ubuntu input was independently checked against Canonical's CD image keyring: GPG reports a good signature for the checksum list, and the base ISO hash `16c9d9122160d901c78d0528cad4556c778701039ea2879b89483d4fd0c0d10b` matches that signed list and the build manifest.

## Selected payload comparisons

The following extracted ISO payloads exactly match their current local source files by SHA-256:

| ISO payload | SHA-256 | Source comparison |
|---|---|---|
| `/psycachy/helpers/activate-launcher.sh` | `52dcfe1efb29c99e73a6ca25e279aae7361f164c355dec0d91b4b3b9035303a1` | `iso/activate-launcher.sh`, equal |
| `/psycachy/helpers/activate.sh` | `ef2897080e0361505dd98b148f9e6071df93d4d24dab958fdd1f22fa75c19825` | `iso/activate.sh`, equal |
| `/psycachy/helpers/phase2-kernel-trial.py` | `35e0f892caff684a704b95567b514fb0ea4dd6b395efa068a5337fd2dbb79372` | `tools/phase2-kernel-trial.py`, equal; source hash omitted from build manifest |
| `/psycachy/helpers/install-target.sh` | `e8fc54567695e5de5e5eb5ff7b8f12d2708c8355237cadf53c0b11bc21e00d89` | `iso/install-target.sh`, equal |
| `/psycachy/late-install.sh` | `45e00191d4e1ec69822ea822d7843af8eb1cf64e08ae8c32d3229a57ea728880` | `iso/late-install.sh`, equal |
| `/psycachy/select-disk.py` | `6e47c85b24cda306c278dcd6031252921ede3b9b4decd5c0609ea9606709ee80` | `iso/select-disk.py`, equal |
| `/psycachy/helpers/amd64-kernel-pin.json` | `d91598eb8ab0f5c31d6d496d20046e417bd16b33d59dc5694137eaed79b610c1` | `config/amd64-iso-kernel.json`, equal |
| `/psycachy/repo/linux-image-7.3.1-psycachy_7.3.1-1psycachy1_amd64.deb` | `a3e89bb7091640abad457a55184555533a6cde72d6b79a78c97f1b25dc111fa6` | exact active pinned package, equal |
| `/psycachy/repo/linux-headers-7.3.1-psycachy_7.3.1-1psycachy1_amd64.deb` | `cccd88818bdcbae2789d98725b754a9253744b42a2ec16458dbc0a424cb0b872` | exact active pinned package, equal |
| `/autoinstall.yaml` | `2933472d06a5a883920c28ed0d6e87a6e68cbfcf54891c42b05f4d6c5f0269ee` | `iso/autoinstall.yaml`, equal |
| `/boot/grub/grub.cfg` | `eff73c8da6cec6b144d06978387fc9f6fc33ead345c1a0f58a530e5b88b6209c` | byte-identical to build script's `autoinstall`-argument transform applied to base ISO GRUB; 2 kernel lines changed |

The embedded pin's image/header package names, versions, architecture and checksums match the two embedded `.deb` files and the current pin. No NVIDIA version assumptions or package discrepancies were examined beyond this pin/package identity comparison.

## What the builder tested, and limits

The build log reports an authenticated-archive check of 280 Ubuntu packages. The repository has 282 `.deb` files: 280 Ubuntu packages plus the two custom PsyCachy kernel packages. The project verifier uses APT's signed Ubuntu archive indexes for the Ubuntu package hashes and separately checks the custom packages against the AMD64 kernel pin. The build also validates the local offline package set and signed base ISO, replays boot images, compares EFI files and live kernel against the source ISO, and checks that a UEFI boot record is present; the build log ends with successful ISO creation. The log does show non-fatal missing translation metadata and APT cache cleanup warnings.

This review did not boot or install from the ISO, exercise an installation-mode choice, run the activation trial or promotion, test rollback, verify firmware behavior, or validate machine-specific storage and Secure Boot behavior. The build/test evidence establishes byte content, package input checks, and stated build-time checks only.

## Review evidence files

- `manifest-source-check.txt`: current hashes for all manifest hash entries.
- `offline-repo-check.log`: checksum results for all 282 repo packages.
- `base-signature-check.log`: Canonical checksum-list signature verification output.
- `iso/`: selected read-only extracted ISO files; `grub-base.cfg` and `grub-expected.cfg` document the GRUB comparison.
- `SHA256SUMS`: checksums for this review bundle.
