# B550I AMD64 7.3.5 C candidate

This target is the AMD64 counterpart to the SP12 7.3.5 C release track. It
shares the BORE and SLUB-canary patches and the C hardening policy, while
keeping each platform's driver patches separate. The 50 SP12-specific patches
are not part of this target.

The candidate uses the frozen B550I C config in
`output/prestable-20261118/configs/b550i-C.config`. It enables BORE,
`INIT_ON_FREE_DEFAULT_ON`, `KSTACK_ERASE`, `SLAB_CANARY`, typed kmalloc cache
partitioning, and strict IOMMU DMA; slab merging is disabled. It is specialized
for Zen 3 (`znver3`).

The build script only creates and audits packages. It does not install
packages, touch boot configuration, build/write media, or access firmware. The
package version sorts below the eventual `7.3.5-1psycachy1` release. The source
signer's trust is not established, and the generated module-signing private key
is ephemeral, so this is test-only and not shippable.

On the B550I, use its installed Clang/LLVM 22 toolchain and require Clang's
native target to resolve to `znver3`:

```sh
targets/b550i-amd64/build.sh \
  output/prestable-20261118/package-candidates/b550i-C \
  native 8
```

For an isolated builder, the same script also accepts a staged toolchain root
in place of `native`. Native config comparison records the pinned host's
Kconfig capability probes (including Rust compiler and pahole versions) as
explicit deltas; `CONFIG_RUST` itself must remain disabled.

The candidate's required next gates are package/content audit, software-only
boot checks, an explicit signing/trust plan, and exact-kernel B550I
qualification. Do not treat the legacy 7.3.1 ISO pin or its packages as the
release target.
