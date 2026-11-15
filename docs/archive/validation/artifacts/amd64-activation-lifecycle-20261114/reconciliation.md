# AMD64 activation lifecycle implementation evidence

## Scope
Implemented in isolated worktree `/tmp/luna-amd64-activation-bb3fc37`, based on `bb3fc379862271bcfdd8715564990f1073b7df83`. No shared files or status documents were edited. Only the owned lifecycle files and tests changed. Diff SHA-256: `539d668a00a667930a29e954a3301818c507822253894d50fb40c8c8973bebb4`.

The implementation integrates prepare, one-boot trial, acknowledgement, explicit reviewed health-attested promotion, and explicit rollback. It requires a root-owned pre-erase installation-mode record bound to the chosen disk serial. First-install is explicitly confirmed as “no prior PsyCachy candidate payload is displaced” and does not certify the disk as blank or preserve its other contents. Replacement requires a verified archive/manifest/hash on a separately serial-identified physical disk, validates direct disk ancestry and exact volume UUID, and carries that proof into target state so reboot-time prepare re-verifies the same reachable backup. Unknown/LVM/mapper ancestry and missing backup paths fail closed.

Prepare persists machine ID and local enrollment certificate fingerprints separately from package pins. The B550I package pin remains static. NVIDIA package identity is derived from verified offline repository packages, and loaded/pinned module signatures plus runtime kernel trust flags replace signer-name and version literals. The launcher enters the helper lifecycle instead of calling GRUB directly. Promotion retains fallback as saved default until a tied local attestation passes; rollback is available from acknowledged or promoted state.

## Hash-linked inputs
The baseline evidence manifest is `/tmp/luna-evidence-baseline-bb3fc37/evidence-manifest.txt`, SHA-256 `f77e85dbca4b6764ebd52a563f75ec3499073a2fe0002e7043988fb85b57b74a`. It identifies the reconciled candidate artifacts and historical status scope. Current AMD64 pin SHA-256 is `d91598eb8ab0f5c31d6d496d20046e417bd16b33d59dc5694137eaed79b610c1`. Exact AMD64 image and headers package hashes are `a3e89bb7091640abad457a55184555533a6cde72d6b79a78c97f1b25dc111fa6` and `cccd88818bdcbae2789d98725b754a9253744b42a2ec16458dbc0a424cb0b872`, respectively; paths are listed in `manifest.txt`.

## Acceptance checks
All focused and project validation passed:

- phase2 activation helper tests: 37 passed
- selector tests: 8 passed
- late installer lifecycle test: 1 passed
- shell syntax, Python bytecode compilation, diff whitespace check: passed
- full `bash tests/static-check.sh`: passed; reports 71 recorded configuration changes verified, root-only `mokutil` test skipped

Full captured output is `/tmp/luna-amd64-activation-evidence-bb3fc37/test-output.log`.

## Unresolved limits
No physical installation, actual reboot/trial, Secure Boot enrollment, GPU module loading, local health attestation, promotion, rollback, or external backup-volume persistence was exercised. Those depend on a target machine, operator review, and physically independent backup media. No root ISO build was run. Runtime hardware and BIOS/UEFI behavior remain unverified.

Worktree usage measured 32 MiB; no build or physical write was performed.
