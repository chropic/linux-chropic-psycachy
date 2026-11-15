# Kernel refresh compatibility: CachyOS 7.3.4-1

**Scope:** frozen target `cachyos-7.3.4-1` / Linux `7.3.4`, SP12 ARM64 r2.  
**Recommendation:** **defer candidate refresh and all builds** until Iris context-bank patch 46 is reconciled against 7.3.4 and the complete ordered series reapplies. The exact source is authentic and was locally staged for this audit; source availability is not the blocker.

## Source identity and availability

- CachyOS release page identifies `cachyos-7.3.4-1`, based on Linux 7.3.4, released 2026-11-11, signed by Peter Jung; GitHub labels the tag signature verified and notes the signing key is expired: [CachyOS release](https://github.com/CachyOS/linux/releases/tag/cachyos-7.3.4-1).
- Exact release assets: [source archive](https://github.com/CachyOS/linux/releases/download/cachyos-7.3.4-1/cachyos-7.3.4-1.tar.gz) and [detached signature](https://github.com/CachyOS/linux/releases/download/cachyos-7.3.4-1/cachyos-7.3.4-1.tar.gz.asc).
- Exact peeled tag commit from `git ls-remote`: `779ca9af71579431ca932a13a7c2ed5934b289ad` (tag object `102157f63c3e23398b6b4b4efd2a5be0ac70cbf9`). CachyOS release metadata says it rebases to 7.3.4 and lists its intervening CachyOS branch additions.
- Linux kernel.org lists the corresponding stable `linux-7.3.4` release and detached upstream signature, dated 2026-11-10: [kernel.org v7.x index](https://www.kernel.org/pub/linux/kernel/v7.x/) and [7.3.4 changelog](https://www.kernel.org/pub/linux/kernel/v7.x/ChangeLog-7.3.4).
- The repository cache had `cachyos-7.3.1-1.tar.gz` and `.asc` only. I fetched the exact 7.3.4 archive and detached signature to `/var/tmp/sp12-cachyos-7.3.4-compat/`; they remain there for subsequent isolated review. Archive size is 269,754,070 bytes; SHA-256 is `695c641edd5df9848f931c06bf97a30734e5f28910367937d5fea235cfd39535`; BLAKE2b-512 is `438505cf485af55d63f82675df5d57c8f584abad72c1aacf5e126e8cdc5b2a0153e05ec017769aaf70fc081e3969ba3e83760556a6d53d3f7a0641961c71cce2`.
- The BLAKE2b value matches CachyOS `linux-cachyos/.SRCINFO`, which names the exact 7.3.4-1 archive, `.asc`, and `validpgpkeys` including the project-pinned Peter Jung fingerprint: [CachyOS .SRCINFO](https://github.com/CachyOS/linux-cachyos/blob/master/linux-cachyos/.SRCINFO).
- Local `gpg --status-fd=1 --verify` returned `VALIDSIG E8B9AA39F054E30E8290D492C3C4820857F654FE`; that primary fingerprint is already recorded in `config/source-pin.sh` and the 7.3.1 provenance evidence. GPG reports trust undefined because this is fingerprint pinning, not a local web-of-trust certification. Do not conflate the CachyOS archive signer with the locally generated module-signing certificate.
- Source `make -s kernelversion` returned `7.3.4`. It was extracted and patch-tested under `/var/tmp`; no source/cache/config/pin file in the repository was modified.

## Replay and upstream overlap

The current `targets/sp121-arm64/inputs.json` declares 51 ordered entries and passed `python3 tools/verify-sp121-inputs.py`. A pristine extraction of the verified CachyOS archive was replayed in manifest order using `git apply --check --no-index` followed by `git apply --no-index` in scratch. Entries 1–45 and 47–51 passed. Entry 46, `iris-context-bank-devices` (`patches/r2/video/02-iris-context-bank-devices.patch`), fails against `drivers/media/platform/qcom/iris/iris_probe.c`; its four probe-file hunks are rejected. The two `iris_core.h` field hunks apply, but that does not make the patch complete. A `--reject` diagnostic was confined to the scratch extraction.

This is a real driver reconciliation, not a routine offset refresh. The 7.3.4 base already defines `IRIS_NP_RESERVE_IOVA_START/SIZE`, `iris_reserve_iova_region()` and `iris_unreserve_iova_region()`, reserves the low 0x25800000 non-pixel IOVA range on the Iris parent device during probe, and frees it on remove/error. The overlay patch instead creates child platform devices for `non-pixel` and `pixel`, sets up/unregisters those children in the same probe/remove/error paths, and expects the older surrounding probe layout. 7.3.4 also has `np_dev`/`p_dev` consumers in `iris_hfi_queue.c` and `iris_resources.c` in the pristine source tree; resolve how the existing consumers, new child-device lifetime, and upstream parent-device IOVA reservation compose before changing or dropping either mechanism. The source grep and failed hunks are reproducible with the commands below.

Because the active ordered series does not apply end to end, there is no qualified 7.3.4 post-patch source tree. Do not call the downstream 50 successful applications a replay pass and do not build from that partial tree.

## Config, security, drivers, DT, and identity impact

- Existing 7.3.1 r2 seed and all its resolved-config evidence are pinned to source hash `3dba29aa…`; seed hash is `cd502794…`, resolved-config hash `cd8938fa…`, and the old identity is `7.3.1-psycachy-sp121-r2` / `7.3.1-1psycachy2`. `olddefconfig` and both release-policy/SP12 config audits must be rerun only after a complete 7.3.4 patch series exists. Review every new, dropped, or changed config symbol; preserve release-policy requirements including lockdown, module-signature enforcement, and forced signed ARM64 kexec policy.
- The new stable base includes post-7.3.1 upstream changes; CachyOS’s 7.3.4 release notes also enumerate vendor branch changes (including scheduler, zram, DRM, Bluetooth, USB, and Wi-Fi deltas). The source authentication does not constitute a security review. Compare the exact 7.3.1-to-7.3.4 kernel.org changelog and CachyOS release delta against the target config, enabled drivers, and locally carried patches before compiling.
- The one observed high-risk overlap is Iris DMA/IOMMU behavior. Other platform, CAMSS/camera, USB/eUSB2, PCI/ath12k, SoundWire, RPMB/UFS, timer, and video/Iris patches passed textual applicability, but that says nothing about API/semantic compatibility or compilation. Re-review those areas against the changed source, especially shared struct/API consumers and resource lifetime.
- Re-run binding validation for the active camera, CSI-2 PHY, Iris/Venus context-bank schemas, plus `dtbs_check` and direct `dt-validate` against the rebuilt Surface Pro 12 DTB. The schema/config/DT evidence recorded for 7.3.1 is not evidence for 7.3.4.
- A release refresh requires a new authoritative kernel identity and package version/release, image and headers filenames, source and post-patch tree digests, resolved-config digest, package and payload digests, DTB digest and injected build ID, module-signing certificate fingerprint, bundle/ISO pins, and installer/live-media references. Choose a unique package identity only after review; do not reuse current package hashes. Rebuild/verify image and headers as a matched pair. Keep the module-signing private key outside source/media/repository; recheck required module signatures and Secure Boot trust against the exact new candidate.

## Bounded continuation plan

1. In a fresh scratch source extraction, compare the 7.3.4 Iris driver flow with the target's required context-bank child devices and the upstream reserved-I/O-VA mechanism. Produce a reviewed rebase or justified replacement for patch 46; preserve all other patches unchanged until individually reviewed. Do not disable either upstream or target DMA protection as a shortcut.
2. Re-run the full 51-entry sequential apply check and apply from pristine authenticated 7.3.4 source. Record per-patch outcomes, the exact manifest hash, source archive hash/signer, pristine tree digest, and final patched-tree digest. A full-series clean replay is the stop/go gate.
3. Resolve config with the patched 7.3.4 Kconfig, run `tools/audit-release-policy.py --arch arm64` and `tools/audit-sp121-config.py`, inspect the entire config delta, and freeze an approved config before compile.
4. After the replay/config gates, first compile only changed C objects/directories with the target config, ARM64 cross toolchain, and bounded parallelism; explicitly include Iris and all camera/PHY/USB/PCI/audio/RPMB/UFS paths whose patches or APIs changed. Then run Iris/camera binding checks, target DTB compile, `dtbs_check`, and `dt-validate` on the generated DTB.
5. Only after focused compile and schema/DT review should the owner decide whether to schedule the clean ARM64 package build. That later build must create and verify the refreshed kernel/header pair, all required modules/signatures, package identity, DTB build ID, and downstream bundle/media pins; it is outside this compatibility assessment.

Suggested isolated commands (run in a clean scratch after reconciling patch 46):

```bash
# Authenticate exact release archive against the pre-existing pinned signer.
GNUPGHOME=/var/tmp/sp12-cachyos-7.3.4-compat/gpghome \
  gpg --status-fd=1 --verify \
  /var/tmp/sp12-cachyos-7.3.4-compat/cachyos-7.3.4-1.tar.gz.asc \
  /var/tmp/sp12-cachyos-7.3.4-compat/cachyos-7.3.4-1.tar.gz
sha256sum /var/tmp/sp12-cachyos-7.3.4-compat/cachyos-7.3.4-1.tar.gz
b2sum /var/tmp/sp12-cachyos-7.3.4-compat/cachyos-7.3.4-1.tar.gz

# Validate target inputs and replay, sequentially, into a newly extracted scratch tree.
python3 tools/verify-sp121-inputs.py
git -C "$SRC" apply --check --no-index "$ROOT/targets/sp121-arm64/$patch"
git -C "$SRC" apply --no-index "$ROOT/targets/sp121-arm64/$patch"

# Config and policy gates only after complete replay.
make -s -C "$SRC" O="$OUT/config" ARCH=arm64 LLVM=-22 olddefconfig
python3 tools/audit-release-policy.py --arch arm64 "$OUT/config/.config"
python3 tools/audit-sp121-config.py "$OUT/config/.config" --output "$OUT/config-audit.json"

# Candidate-focused checks after patch/config approval; keep output/source disposable.
make -C "$SRC" O="$OUT/config" ARCH=arm64 LLVM=-22 -j2 \
  drivers/bluetooth/hci_qca.o drivers/clocksource/arm_arch_timer.o \
  drivers/i2c/busses/i2c-qcom-cci.o drivers/iommu/of_iommu.o \
  drivers/media/i2c/ov02c10.o drivers/media/i2c/ov13858.o \
  drivers/media/platform/qcom/camss/camss-csiphy.o \
  drivers/media/platform/qcom/camss/camss-vfe.o \
  drivers/media/platform/qcom/camss/camss.o \
  drivers/media/platform/qcom/iris/iris_buffer.o \
  drivers/media/platform/qcom/iris/iris_hfi_queue.o \
  drivers/media/platform/qcom/iris/iris_probe.o \
  drivers/media/platform/qcom/iris/iris_resources.o \
  drivers/media/platform/qcom/iris/iris_vidc.o \
  drivers/misc/rpmb-core.o drivers/net/wireless/ath/ath12k/core.o \
  drivers/net/wireless/ath/ath12k/pci.o drivers/pci/pcie/aspm.o \
  drivers/pci/quirks.o drivers/phy/phy-snps-eusb2.o \
  drivers/phy/qualcomm/phy-qcom-mipi-csi2-3ph-dphy.o \
  drivers/phy/qualcomm/phy-qcom-mipi-csi2-core.o \
  drivers/phy/qualcomm/phy-qcom-qmp-combo.o \
  drivers/phy/qualcomm/phy-qcom-uniphy-pcie-28lp.o \
  drivers/platform/surface/aggregator/controller.o \
  drivers/platform/surface/surface_aggregator_registry.o \
  drivers/rtc/rtc-surface.o drivers/soundwire/qcom.o \
  drivers/ufs/core/ufs-rpmb.o \
  drivers/usb/dwc3/core.o drivers/usb/dwc3/dwc3-qcom.o \
  drivers/usb/dwc3/host.o
make -C "$SRC" O="$OUT/config" ARCH=arm64 LLVM=-22 -j2 \
  qcom/x1p42100-microsoft-sp12in.dtb
make -C "$SRC" O="$OUT/config" ARCH=arm64 LLVM=-22 dtbs_check \
  DT_SCHEMA_FILES='Documentation/devicetree/bindings/media/qcom,iris.yaml'
```

The object list above is derived from the current 51-entry patch set's changed C files; recheck it after the patch-46 reconciliation. Compile it only after the complete replay/config gates pass. Do not use the partial scratch tree from this audit.

## Exact commands run and outcome

- `gpg --show-keys --with-colons output/.phase1-closeout-20261110T192001-0700/policy/cachyos-signer.asc` confirmed primary fingerprint `E8B9AA39F054E30E8290D492C3C4820857F654FE`.
- `curl -fL ...` fetched the CachyOS release archive and `.asc` into `/var/tmp/sp12-cachyos-7.3.4-compat/`; `gpg --verify` produced the `VALIDSIG` above, and `sha256sum`/`b2sum` produced the recorded hashes.
- `git ls-remote https://github.com/CachyOS/linux.git refs/tags/cachyos-7.3.4-1 'refs/tags/cachyos-7.3.4-1^{}'` recorded the tag object and peeled commit above.
- `make -s -C /var/tmp/sp12-cachyos-7.3.4-compat/cachyos-7.3.4-1 kernelversion` returned `7.3.4`.
- A Python loop read `targets/sp121-arm64/inputs.json`, then invoked `git apply --check --no-index` and `git apply --no-index` sequentially for each current patch. Results: 50 pass, patch 46 fails; a scratch-only `git apply --reject --no-index` confirmed all four `iris_probe.c` hunks rejected while the two `iris_core.h` hunks applied.
- `python3 tools/verify-sp121-inputs.py` passed input, policy fragment, and patch hash checks.
- No config resolution, compile, schema validation, package build, signing, pin/config/patch edits, or candidate integration was performed.

## Archive and closeout

The signed source archive and detached signature are retained under
`phase0-work/authenticated-sources/cachyos-7.3.4-1/`; their SHA-256 values
remain `695c641edd5df9848f931c06bf97a30734e5f28910367937d5fea235cfd39535`
and `ec286ac98c4fae149dfb97f88505e80ed54a9e96f867f678107875e47f5e21c6`.
The full per-entry ordered log is in
[`cachyos-7.3.4-ordered-replay-20261114.md`](cachyos-7.3.4-ordered-replay-20261114.md).
After preserving the archive, signature result, and replay log, open-file and
mount checks were clear and the dedicated GPG agent was stopped. The shell
safety guard rejected recursive removal of the temporary extractions and GPG
home under `/var/tmp`; they remain intact. They contain only reproducible
audit scratch, not an approved candidate or unique project inputs.

## Budget

Compatibility effort used approximately 20 minutes of the 120-minute cap. Work stopped at the concrete series incompatibility; no heavy build ran. The 7.3.4 archive remains in `/var/tmp` as scratch audit input, not as a repository cache or release pin.
