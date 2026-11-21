# 7.3.5 C release backlog

**Private release queue · 2026-11-20**

| Target | First blocked gate | Next action | Evidence |
|---|---|---|---|
| B550I · AMD64 | HOLD · 1: patch selection | Lead with the DAW workload: prepare one bounded shortlist for owner review, with pinned revisions, expected benefit, rejection tests and explicit deferrals. | [B550I and shared enhancement leads](production-7.3.5-patch-contract-review.md#enhancement-leads-exclusions-and-unresolved-owner-decisions) |
| SP12 · ARM64 | HOLD · 1: patch selection | Audit restore-only ASPM; pin and review the Wi-Fi counter fix for an isolated trial. Include SP12 selections in the same owner shortlist. | [ASPM policy and restart evidence](production-7.3.5-patch-contract-review.md#enhancement-leads-exclusions-and-unresolved-owner-decisions) |

Greenlight means the owner accepts an exact ISO digest for private use on its
named machine after installation, recovery, hardware and performance tests.
Each target earns its own verdict. Public distribution is a separate decision.
**Each ISO must run its patched target kernel in Try, Install and default installed boot.**
C is the baseline: integrate required hardware fixes, including userspace and
support files, on the target that needs them.

## Selected inputs and patch decisions

Use CachyOS `cachyos-7.3.5-2` with BORE on
both. Start from the [patch review](production-7.3.5-patch-contract-review.md)
for source identity, patch order, config hashes, and a test per change.

| Machine | C manifest | Kernel config | Package pin |
|---|---|---|---|
| B550I · Ryzen 7 5800X3D / RTX 4070 | [inputs.json](../targets/b550i-amd64/inputs.json) | [b550i-C](../config/kernel/b550i-C.config) | [AMD64 C](../config/amd64-iso-kernel-prestable-c.json) |
| SP12 · X1P-42-100 / Purwa | [52-entry manifest](../targets/sp121-arm64/inputs.camera-lanes-candidate.json) | [sp12-C](../config/kernel/sp12-C.config) | [ARM64 C](../config/arm64-iso-kernel-prestable-c.json) |

- **B550I baseline:** C packages were built and audited. The [test ISO](archive/README.md#b550i-boot) embeds them but boots Ubuntu's live kernel. A [physical Ventoy boot panicked](archive/README.md#b550i-boot); the failing stage is unknown.
- **SP12 baseline:** C live kernel and DTB booted on hardware. Neither the older 51-entry manifest nor the 54-entry CSID/Iris diagnostic build is selected C. The latter's [fix1 generic installer path](archive/README.md#surface-boot-and-recovery) reached disk selection only.
- **SP12 Wi-Fi (owner decision):** retain ath12k's restore of previously active ASPM states only. Verify the restored mask adds no states and Wi-Fi works across resume. Trial the absent restart-counter fix separately: review exact bytes and provenance, compare channel switches and counters against C on SP12, then decide inclusion. Trial approval is not a pass.
- **Other SP12 fixes:** panel `0007` and PCIe PHY reset `0011` are already in source: verify runtime binding. Test the CSID lane fix, Iris firmware name and OV02C10 userspace helper separately.
- **Scope cutoff (owner decision):** present one evidence-backed shortlist covering both targets. Document deferred speculative leads, then freeze the approved scope except for qualification failures. Mandatory fixes and the full performance suite remain in scope. Close patch provenance, license/DCO and firmware-use review; corroborating the source signer does not clear downstream inputs. Preserve C and give changed bytes a new candidate ID.

**Starting ISO SHA-256s (evidence only):** B550I C `aa6df67db295b5040ff521fed4bd7f2c5bea69669c1510bc845c72e6359181c2`; SP12 C `0ecc8f51c111581db79536d76b07623cf6b7e42a8b683ce3c8bd7b7b85ad8c03`; SP12 fix1 `c5f060b009b343d56f5896e1f2be6ffb8ca97e831b1333c0fbb3d2c7245a2e5b`.

## Gates — in order, per target

1. **Patch contract:** owner reviews manifests, configs, support files, selection decisions and tests. Account for every mandatory fix.
2. **Packages:**
   - Record clean inputs, toolchain, applied series, resolved config, ABI, module trust, headers and SP12 DTB. Verify B550I znver3 and SP12 EL1/4 KiB.
   - Reconfirm source digest; independently verify a changed source/key. Record package versions and recipe, compare rebuilt unsigned payloads, explain signing/time differences and use repeatable signing for updates rather than C's ephemeral module key.
   - SP12 build scratch is authorized in a new isolated internal directory only; preserve existing data and exclude the Apple HDD. Check native builder, `xorriso`, initramfs tools, namespaces, space and attended privilege. Missing trust or access means BLOCKED.
3. **ISO:**
   - B550I: change the live builder and validator together. SP12: integrate the Surface kernel/initramfs/DTB, usable firmware/userspace and guarded offline installer.
   - Independently unpack the final ISO. Record ISO digest, package manifest and boot map. Verify EFI chain, every supported entry → actual kernel/initramfs, squashfs modules, root/storage drivers, offline package closure and a distinctly labelled known-good fallback. B550I's current `/casper/vmlinuz` is Ubuntu's, not C.
4. **Disposable VM:**
   - Start offline UEFI (AMD64 KVM; ARM64 `virt`) with fresh variables, read-only ISO/sentinel and writable child disk. Verify Linux serial output before testing.
   - Cold-boot Try and Install separately. Refuse invalid disks, complete installation, reboot **from that installer session**, eject media and boot patched default twice.
   - Exercise update interruption, trial/rollback and recovery; return to default. At each boot capture `uname -r`, build/boot ID, cmdline and root source. Save continuous console, installer logs and matching before/after sentinel hashes.
   - Compare direct ISO/Ventoy where applicable. [Surface Try diagnostics](archive/README.md#surface-boot-and-recovery) reached a PSCI/SMC panic with the Surface DTB; fix1 corrected the generic installer config path but selected no disk. Test payload, layout and installer in a compatible guest. Only a named, accepted emulation gap can defer exact boot to hardware; installer defects still block.
5. **Physical test card:** after VM checks, agree operator, machine, media and expendable disk model/serial/UUID, allowed writes, boot paths, trust/Secure Boot policy, capture, backup and restore with owner. Prior staging grants no device writes, firmware changes or key enrollment. Verify policy in VM where emulable; return to gates 2–4 if keys or bytes change.
6. **Physical lifecycle:** with operator present, read back staged digest and cold-boot Try and Install separately. Install only to the named disk; capture same-session reboot/eject, patched default, power-cycle, second default, recovery and return to default. Verify kernel, modules, root, Surface DTB and effective Secure Boot. Stop on panic and preserve preceding console. Boot, corruption, wrong-target or fallback defects block.
7. **Function and performance:** close the mandatory items below on the final candidate. Identify each tuning change, repeat affected tests and record failed or inconclusive runs alongside passes.
8. **Private greenlight:** rerun boot/install/recovery on final bytes. Obtain independent review of build, trust, boot, recovery, hardware and measurements, then owner sign-off with signed checksums and evidence for the **tested digest**.

## Hardware and performance work

### B550I

- **Boot:** distinguish physical `0x00000100` from historical VM installer-shutdown `0x0000000b`. Capture entry, cmdline and preceding Linux console; inspect the generated `grub_platform` diagnostic. Replay same-session shutdown, then compare direct/Ventoy on identical bytes. A separate overlay boot to login did not replay installation.
- **Desktop:** verify signed NVIDIA DKMS rebuild/load and acceleration, virtualization, network and USB.
- **DAW:** freeze Ardour, Wine, Windows VST3 via yabridge and DX1 routing. Compare known-good BORE vs candidate at equal load: proposed 48 kHz/128 frames for 30 min, then 64 frames/load sweep. Check plugin GUI, automation, reopen, audible stereo, xruns and latency. Reject new repeatable dropouts.

### SP12

- **Cameras:** both sensors yielded zero frames; CAMSS internal pattern gave 30/30. Userspace A/B did not restore streams. Compare C vs CSID lane-map change with userspace fixed; verify built DT/config and log lanes and graph per sensor. Require ≥30 consecutive real buffers from **each** sensor, changing images in the desktop app, switching/reopening and correct privacy LED behavior, cold and after resume.
- **Audio:** named nodes exist but the default sink pointed at absent `auto_null`; mic retry yielded zero bytes. Run the [explicit PipeWire vs ALSA test](archive/README.md#surface-peripherals) as the desktop user. Require audible L/R, changing intelligible built-in mic signal and browser-call input, plus XM5 A2DP stereo, reconnect and replay. Repeat after resume. XM5 headset mic is preferred; report separately.
- **Video:** Iris init `-22` does not establish a signature problem. Verify firmware identity, issuer and usage rights before staging. Require successful initialization and hardware decode without software fallback.
- **Resume:** two deep resumes returned with PCIe L2/hwmon warnings. Trace devices across repeated deep cycles with the same boot ID; recheck power, display/GPU, touch, keyboard, Wi-Fi, charging and media. Resolve warnings or document reviewed evidence they are benign.
- **Storage:** correlate resets and filesystem errors by device and time. Vary one component at a time; checksum approved expendable media across cold boot/resume. Unexplained errors on a required install path block. Verify UFS RPMB registration/lifetime read-only on target.

### Both targets: performance and tuning

- **Run:** all six [fixed scenarios](archive/README.md#performance-fixtures): idle, interactive editor, local video, interactive compile, batch compile, suspend. Use ≥3 interleaved reference/candidate pairs per scenario with matched conditions and completed work. Test SP12 AC responsiveness separately from battery.
- **Accept:** ≥10% less whole-system energy where measurable, ≤10% longer completion and ≤5% worse p95 latency. Investigate repeatable primary-workload loss >3%; reject loss >10% or new storage/watchdog/resume or functional failures.
- **Measurement limits (owner decision):** B550I UPS Wh is estimated. If approved SP12 whole-system telemetry remains unavailable, matched battery/runtime and responsiveness trials are still mandatory. Private sign-off may explicitly except the missing measurement once all other gates pass. Record **unmeasured**, not PASS; claim no energy saving.

**Recording rule:** update the target's status here with `gate · candidate ID /
ISO SHA-256 · PASS/FAIL/BLOCKED · evidence link · next action · operator/date`.
Older passes are controls only. For a failure capture the first divergence and
vary one thing. Reuse evidence only for unchanged inputs; rerun affected gates
and the final boot/install/recovery sequence on the exact bytes being promoted.
For audio tests use a consented stimulus and retain signal metrics rather than private recordings.
