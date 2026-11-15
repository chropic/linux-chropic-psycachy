# AMD64 CPU-target audit

## Finding

The pinned AMD64 kernel candidate and the retained AMD64 ISO are intended to
carry a Zen 3 (`znver3`) specialized kernel. This is supported by the saved
resolved config, compiler target metadata from the build that produced the
ISO-pinned package, the ISO kernel pin, and the ISO payload checks. The custom
kernel is more specifically targeted than the generic x86-64-v3 level: the
build uses Clang's `-march=native`, which resolved to `znver3` on the Ryzen 7
5800X3D build host. This conclusion applies to that pinned candidate and that
build; it does not mean every package with Debian architecture `amd64` is
Zen-3-specific.

No architecture migration is needed to make the existing pinned candidate
Zen-3-targeted. There is a reproducibility gap: the builder expresses its
target as `native`, while the package pin says `znver3`. A future build on a
different host can silently target a different CPU unless the result is
checked against the pin.

## Evidence

- `config/cachyos-7.3.config` and
  `config/cachyos-7.3.1-normalized.config` are generic: they set
  `CONFIG_GENERIC_CPU=y` and `CONFIG_X86_64_VERSION=1`, with
  `CONFIG_X86_NATIVE_CPU` unset. `config/psycachy.fragment` enables
  `CONFIG_X86_NATIVE_CPU=y`; the saved final
  `config/psycachy-7.3.1.config` has native enabled and generic CPU disabled.
  This is an intentional transition from generic x86-64 baseline settings to
  compiler-native targeting. The config contains no selected `CONFIG_MZEN3`;
  Zen 3 identity comes from native compiler target detection, not that Kconfig
  selection.
- `build.sh` applies the PsyCachy fragment, records `cpu_target=native`, and
  saves `clang-22 -march=native -###` output in `build-metadata.txt`. The
  retained metadata for the ISO-pinned image package is
  `output/.phase1-closeout-20261110T192001-0700/amd64-build/build-metadata.txt`.
  It reports the build CPU as “AMD Ryzen 7 5800X3D 8-Core Processor” and
  Clang's effective `-target-cpu znver3`. Its effective target features
  include AVX2, BMI/BMI2, F16C, FMA, LZCNT, and MOVBE. The metadata toolchain is
  Clang/LLD 22.1.8. This is direct evidence that native selection resolved to
  Zen 3 for this build. The kernel's Kconfig has a `X86_NATIVE_CPU` option for
  locally optimized native builds; see the [Linux x86 Kconfig source](https://github.com/torvalds/linux/blob/master/arch/x86/Kconfig.cpu).
- The retained ISO-pinned resolved config has SHA-256
  `c6ab15474731c035fc3906a907ecbfa1f92b6a2174af03e42420693b72dc3733`, which
  matches `config/psycachy-7.3.1.config` and the config saved beside that
  package. `config/amd64-iso-kernel.json` labels the pair `architecture:
  amd64` and separately declares `cpu_target: znver3`; it pins the image and
  header hashes and kernel payload hash. The ISO lifecycle manifest records
  the same pinned package hashes (`a3e89...` image and `cccd...` headers) in
  the offline repository and embedded package list. Thus the ISO workflow
  embeds the pinned candidate, while `amd64` remains Debian's package
  architecture field.
- `config/amd64-iso-base.json` names the Ubuntu input
  `ubuntu-26.10-desktop-amd64v3.iso`. That `amd64v3` name describes the Ubuntu
  base image selection; it is not proof of the PsyCachy kernel's compile
  target. The kernel's `znver3` identity is established separately by its
  package/config pin and build metadata.
- AMD identifies the Ryzen 7 5800X3D as Zen 3 and lists AVX2 among its
  supported instruction sets on its [product page](https://www.amd.com/en/products/processors/desktops/ryzen/5000-series/amd-ryzen-7-5800x3d.html).
  The current host's read-only `lscpu` output identifies that model and
  includes AVX2, BMI1, BMI2, F16C, FMA, LZCNT, MOVBE, and XSAVE-related flags.
  These are consistent with the x86-64-v3 requirements in the
  [x86-64 psABI](https://gitlab.com/x86-psABIs/x86-64-ABI/-/blob/master/x86-64-ABI/low-level-sys-info.tex).
  The build target is specifically `znver3`, not merely a claim that the
  artifact uses only the v3 baseline. No independent disassembly of the
  existing kernel binary was performed.

## Package, ISO, and installed-host distinctions

The Debian package architecture `amd64` and the ISO's Ubuntu base name are
architecture/platform labels; neither one by itself encodes a CPU tuning
target. The ISO pin's `cpu_target` value is useful provenance, but it is just
metadata unless checked against an effective compiler target. Here, the
retained build metadata supplies that corroboration for the package hashes in
the ISO manifest.

The current read-only host inventory reports `x86_64`, a Ryzen 7 5800X3D,
installed packages `linux-image-7.3.1-psycachy` and
`linux-headers-7.3.1-psycachy` at `7.3.1-1psycachy1`/`amd64`, and running
release `7.3.1-psycachy`. Do not treat that as proof the ISO-pinned image is
installed: `/boot/config-7.3.1-psycachy` hashes to
`3f5fce90b5f91eef3a6d8842f3b7c40c44f24b1c32f700d84db905e83fceb4ae`, whereas
the ISO pin's resolved config is `c6ab1547...`. The package version and
`uname -r` are shared across builds, so the exact running image is not
identified by those labels alone. The earlier phase-2 rebuild output also has
the `3f5f...` config and different package hashes. The pin's exact candidate
should remain distinct from the currently installed/running package until
its image hash is independently tied to the installed payload.

## Scoped recommendation

Keep the current pinned candidate as a Zen 3 target. Do not change the
architecture or ISO package labels to `amd64-v3`: the Debian architecture
must stay `amd64`, and the actual kernel target is `znver3`.

For the next AMD64 build, make the existing intent fail-closed:

1. Before compilation, require the recorded compiler-native CPU to resolve to
   `znver3` (or require the actual target CPU explicitly), and fail if it does
   not. `build.sh` currently records the CPU and compiler target but does not
   compare them with `config/amd64-iso-kernel.json`'s `cpu_target`.
2. After config resolution, verify `CONFIG_X86_NATIVE_CPU=y` and the expected
   resolved-config hash; after compilation, record the effective target from
   the real Kbuild compiler invocation, not only a standalone compiler probe.
   Add a package/ISO audit that ties this metadata to the package hashes and
   embedded kernel payload.
3. If builds must be reproducible on other machines, replace implicit native
   selection with a pinned explicit Zen 3 Kconfig/compiler target. Confirm
   the pinned kernel source supports the intended selector/flag, then run
   `olddefconfig` and inspect actual Kbuild commands before adopting it. Do
   not assume `CONFIG_MZEN3` exists or that the kernel config alone constrains
   all compilation without that source-level check.

Qualification for a newly rebuilt package should verify source/signature and
toolchain identity; inspect final resolved config and effective compile
commands; verify package metadata stays `amd64`, checksums and embedded image
match the CPU-target pin; inspect selected ELF/object instructions if the
build artifacts allow it; then boot in a disposable environment that exposes
the required CPU features, followed by the already-planned physical B550I
qualification. None of those steps should overwrite the existing pin or
package evidence before the new pair is reviewed.

## Evidence limits

This audit inspected existing configs, manifests, metadata, package hashes,
and current read-only host state only. It did not run a kernel build, alter
configuration or pins, inspect/disassemble a binary kernel payload, install a
package, or write to hardware. The ISO's recorded payload audit confirms
identity and consistency with its pin; it does not prove the kernel booted on
the present host. The existing build metadata and CPU model support the Zen 3
target claim, but they are not a substitute for auditing compiler commands in
any future build.
