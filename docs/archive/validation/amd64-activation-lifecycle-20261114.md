# AMD64 activation lifecycle integration

**Baseline:** `bb3fc379862271bcfdd8715564990f1073b7df83`  
**Integrated patch SHA-256:** `539d668a00a667930a29e954a3301818c507822253894d50fb40c8c8973bebb4`

The isolated implementation was independently reviewed and integrated into
the workspace. The launcher now uses the trial helper for a one-boot candidate
test, acknowledgement, explicit promotion, and rollback. The installer records
an explicit first-install/replacement choice before erase, ties it to the
selected disk serial, and rechecks an independent displaced-payload backup
before a replacement trial. Candidate and fallback identities, per-install
signing-certificate fingerprints, NVIDIA package identity, and runtime module
trust are checked by the helper. The fallback remains the saved default until
promotion.

## Verification

- `python3 tests/test_phase2_kernel_trial.py`: 37 passed.
- `python3 tests/test_iso_select_disk.py`: 8 passed.
- `python3 tests/test_iso_late_logging.py`: 1 passed.
- Shell syntax checks and Python bytecode compilation: passed.
- `bash tests/static-check.sh`: passed; 71 recorded configuration changes
  verified. The root-only `mokutil` check was skipped in this non-root test
  context.
- `git diff --check`: passed.
- Independent review: approved with no code-level blocker.

The [review](artifacts/amd64-activation-lifecycle-20261114/independent-review.md)
notes one assurance limit: the local health attestation is unsigned and
root-controlled. It binds review assertions to the candidate and machine but
does not cryptographically prove reviewer identity or physical tests. Treat it
as an auditable operator workflow record.

Patch, reconciliation, worker and lead test outputs, review, and their
checksums are archived in
[`artifacts/amd64-activation-lifecycle-20261114/`](artifacts/amd64-activation-lifecycle-20261114/).

## Remaining qualification

No ISO was rebuilt and no disposable reboot/rollback, Secure Boot enrollment,
NVIDIA runtime, external-backup persistence, or physical B550I check was run.
The code and focused tests establish the software interface only. The exact
candidate must still be rebuilt and pass its UEFI trial/rollback and hardware
gates before promotion or private-pilot completion.
