# SP12 final51 combined image build and content audit — 2026-11-15

**Build:** 2026-11-15 12:48:04–12:50:40 MST (19:48:04–19:50:40 UTC)
**Host:** `cs-sp12.taila8843d.ts.net`, ARM64, running
`7.3.1-psycachy-sp121`
**Result:** Native build and independent content audit passed. Runtime and
physical qualification remain incomplete.

## Candidate identity

- Path on SP12: `/var/tmp/sp12-r2-combined-20261115/output/private-sp12-r2-final51-combined.iso`
- Size: 5,500,940,288 bytes
- SHA-256: `56083da5996fb4fe371b100e8fb325e0083e43208307d4af7f4aa592fa8d3a27`
- Builder source: commit `cccd7cf051311399e2125ba6883b3d21b41a6413`;
  script SHA-256
  `ea03ecba82d9f618a4fc797d94014ded98211a41752f7d0e793040e84cd65112`
- Buildinfo: `private-local-testing-only-do-not-publish`; it pins the signed
  Ubuntu base, final51 kernel pair and pin, installer ISO, support source
  commit, four private machine files, and generated payload hashes.

The signed Ubuntu 26.10 ARM64 base hash is
`9242a38c47eb53a5beb153c249d4843e4366f8955e9b972663e4ab7989311e9f`.
The opt-in installer ISO hash is
`2d8b4588a7397aa9a297866fc24cafde45fd867eecc05fa377c1c71b5d42abb1`.
The final51 image and headers package hashes are
`a1398ad1445d0a712aece65fbb2aa129a8afece4011e54773b6940616cae40bd`
and
`80139be7bc17a3ab5034f2deafb220bd6373bd33b23ddd8e5032f98bf89dccf3`.
The private support source commit is
`ea0f07e66beea95898d96fbeb6daa472f4735af3`.

## Build and audit

The first root-run build on the same staged inputs stopped in the final
installer support-manifest check because a local path variable had replaced
the support-file map. It retained an invalid, unvalidated partial
(5,500,940,288 bytes; SHA-256
`48a23b26fe698365f07b0467a28d5eec4b2976cabe2bc2719494dcb2acb2212d`)
and an error log. The variable was renamed in commit `cccd7cf`; the 16
focused builder tests and `bash tests/static-check.sh` passed. The failed
partial was removed after hashing; the error summary remains in the private
local evidence folder.

The user then reran the staged command on SP12. The successful log records
verified input checksums and the Canonical signature, `validated=True`,
unchanged physical ESP/NVRAM/mount state, and the final ISO hash above. The
builder reported:

- Pinned base, package manifest, kernel, modules, DTB, initramfs, and live
  layer passed.
- Default Try/Rescue entry has no autoinstall command; base installer layers
  are unchanged.
- The guarded install entry is separate and uses the pinned support files.

An independent read-only audit verified the complete image against its
buildinfo and pins. It checked the kernel payload, DTB, initrd, squashfs,
manifests, GRUB entries, embedded installer payload and support files. The
Try/Rescue entry is first and does not autoinstall; the explicit installer
path retains guarded target selection; the generic QEMU diagnostic route
remains separate. All 1,170 target-support manifest entries and the four
machine files in the live layer matched. The 150 pre-existing installer
payload files matched the input image byte-for-byte. GPT and UEFI El Torito
integrity checks passed, and EFI bytes matched the signed base. The independent
review marked content checks PASS and runtime boot qualification INCOMPLETE.

Sanitized text evidence and checksum/buildinfo sidecars are kept locally under
`docs/archive/validation/artifacts/sp12-combined-build-20261115/`; the ISO
and full buildinfo remain on SP12. The first-run error log is retained with
the evidence. The remote output-audit scratch and successful/failed builder
scratch have not yet been cleaned.

## Qualification boundary and next checkpoint

This is an experimental private test image, not a qualified release. Live
Wi-Fi, audio, suspend, and the other exact-device checks await a native SP12
boot. No media was written and no installation target was changed in this
build. The combined ISO is not yet staged on Ventoy. The existing AMD64 ISO
and USB partition layout remain untouched.

The next media step is a separate supervised file-level checkpoint for
Ventoy UDisk serial `General_UDisk-0:0`, UUID `4E21-0000`. The measured
combined ISO fits only after replacing the existing SP12 live-only file;
the AMD64 ISO must remain unchanged. The full target identity, exact sidecar
updates, protected devices, and recovery action must be presented again before
that write. Native boot and installed-system acceptance remain open afterward.
