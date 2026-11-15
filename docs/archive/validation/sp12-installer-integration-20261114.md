# SP12 installer integration record

**Recorded:** 2026-11-14 03:14 UTC  
**Baseline:** `bb3fc379862271bcfdd8715564990f1073b7df83`  
**Status:** Builder code integrated and independently approved; private media build and qualification remain open.

## Implementation and review

Integrated the reviewed I-7 patch in `iso/build-sp12-live.py` and
`tests/test_sp12_live_builder.py`. Patch SHA-256:
`99380ea7052f33043570435acc25771c3c3a053d2f5d234a8c4debd6ebe557cf`.

The builder accepts an opt-in installer ISO only with an exact lowercase
SHA-256 and selected r2 kernel pin. It snapshots the installer bytes into a
private no-follow file, hashes the copied bytes in the same pass, and uses that
snapshot for metadata and full-payload extraction. The default Try/Rescue
entry remains first and has no autoinstall. Separate guarded SP12 and generic
QEMU diagnostic entries use the pinned Surface kernel/DTB and stock generic
kernel/initrd respectively. The target support bundle is hashed and checked,
the full support manifest hash is recorded in buildinfo, and the installer
regenerates/synchronizes the target initramfs before its dpkg audit.

The [independent review](artifacts/sp12-installer-integration-20261114/independent-review.md)
approved integration and confirmed the earlier source-path replacement race is
closed. Its SHA-256 is
`66f8881e2ff1fa94796e6670f723e62ecb384e85044bbf79c805822e0f0916bb`.
The [worker report](artifacts/sp12-installer-integration-20261114/worker-report.md)
and [evidence manifest](artifacts/sp12-installer-integration-20261114/worker-manifest.json)
are archived with the exact patch and logs.

## Verification

- `python3 tests/test_sp12_live_builder.py`: 16 passed in the integrated workspace.
- `python3 -m py_compile iso/build-sp12-live.py tests/test_sp12_live_builder.py`: passed.
- `git diff --check`: passed.
- `bash tests/static-check.sh`: passed; 71 recorded configuration changes;
  root-only `mokutil` check skipped.
- The lead's post-integration command results are in the
  [verification record](artifacts/sp12-installer-integration-20261114/lead-verification.md).
- Worker validation of the retained final51 installer ISO confirmed its r2
  pin, package pair, and guarded interactive config before snapshot hardening.
  It was read-only and is recorded in the worker log. The 5 GiB ISO was not
  snapshotted/extracted again after the hardening change.

## Open gates

The exact private support checkout pinned at commit
`ea0f07e66beea95898d96fbeb6daa472f4735af3` and its four machine files were not
available. The nearby untracked `sp121-reference/` checkout has a different
commit and was not used. The last recorded `cs-sp12` root free-space values
were 18,940,235,776 and 18,939,600,896 bytes, below the native builder's
24 GiB minimum, plus the installer snapshot. No full private-support build,
final ISO audit, or sidecars were produced. No VM, physical device, or firmware
action was performed.

I-7 remains open until the exact support inputs are available, the native
builder has the required measured scratch space, and a full build/audit passes.
Physical SP12 functionality and fresh-install gates remain separate.
