# I-7 SP12 installer integration report

## Result

Implemented the opt-in guarded installer path in the isolated worktree `/tmp/luna-sp12-installer-integration-20261114`. Only `iso/build-sp12-live.py` and `tests/test_sp12_live_builder.py` differ from baseline `bb3fc379862271bcfdd8715564990f1073b7df83`. No ISO was built and no device or VM was used.

With `--installer-iso` and its required exact `--installer-iso-sha256`, the builder copies the source through a private no-follow snapshot, hashing the copied bytes in the same pass. The snapshot is created in an exclusive mode-0700 directory as a mode-0600 file, fsynced, checked as a regular file against source identity before/after the copy, and rejected unless its SHA-256 equals the supplied pin. Metadata and full payload extraction use only the snapshot. Apply mode accounts for the snapshot size in addition to the existing 24 GiB builder reserve. A 16-test small-file regression mutates and replaces the source after snapshot creation, then confirms the extraction consumer still receives the snapshot bytes. No large installer ISO snapshot was created in this task.

The builder validates the embedded installer pin and image/headers package pair against the selected r2 pin. It adds two explicitly selected install entries: the Surface entry uses the generated r2 kernel/initrd and pinned Surface DTB; the generic-QEMU installer diagnostic uses the preserved stock kernel/initrd, consumes the same guarded autoinstall payload, and has no Surface DTB. The default Try/Rescue entry remains first and carries no `autoinstall`. The installer config retains `interactive-sections: ['*']`, its exact-device early selector, and guarded target late-install script.

The builder copies the validated four machine files and files from the two commit-pinned support source trees into the target payload. A generated tab-separated path/hash manifest is pinned by the generated late command; the command checks the manifest hash, source and destination file hashes, path containment, regenerated target initramfs, synchronized ESP initramfs, and clean target dpkg audit. The full target-support manifest SHA-256 is recorded in buildinfo. Source-tree symlink directories and escaping/non-file links are rejected. The final-ISO audit checks menu separation, kernel/DTB selection, support manifest and payload hashes.

## Verification

- `python3 tests/test_sp12_live_builder.py`: 16 tests passed.
- `python3 -m py_compile iso/build-sp12-live.py tests/test_sp12_live_builder.py`: passed.
- `git diff --check`: passed.
- `bash tests/static-check.sh`: passed, including the repository test suite and build dry-run.
- Earlier read-only extraction and validation of the retained final51 installer ISO confirmed its r2 pin, package pair, and guarded interactive autoinstall flow. The validated values are recorded in `installer-payload-validation.log`; ISO SHA-256 `2d8b4588a7397aa9a297866fc24cafde45fd867eecc05fa377c1c71b5d42abb1`, pin SHA-256 `6fb4104b0bc4e8ed3c4211d4cf62331a32436a9b422326542a17533fcbee7c90`, package version `7.3.1-1psycachy2`, image package SHA-256 `a1398ad1445d0a712aece65fbb2aa129a8afece4011e54773b6940616cae40bd`, headers SHA-256 `80139be7bc17a3ab5034f2deafb220bd6373bd33b23ddd8e5032f98bf89dccf3`. That earlier extraction preceded this snapshot hardening; no 5 GiB snapshot or post-hardening real-ISO extraction was run.

## Open integration dependency

The exact local support checkout pinned at commit `ea0f07e66beea95898d96fbeb6daa472f4735af3` and the four expected machine files are unavailable in this environment. The nearby `sp121-reference/` checkout is at a different commit and was not used. Source-tree handling is covered with synthetic fixtures and validates the pinned archive when an apply run is available, but real private support payload extraction and complete ISO build/audit remain unverified until the exact checkout and files are supplied. The configured builder requires at least 24 GiB free in the output filesystem, plus the installer snapshot size during apply; no build was attempted.

No source edit, ISO generation, physical/EFI write, firmware change, or publication occurred.
