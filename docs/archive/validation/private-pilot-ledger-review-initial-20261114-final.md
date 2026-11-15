# Final review: ledger/checklist corrections

## Resolved

- The physical-write statement is now scoped to “this qualification pass” and explicitly acknowledges the earlier guarded write of the distinct `e29dd59f…` USB image. This removes the conflict with the historical Apple HDD record.
- The raw installed GRUB config is now retained at `docs/archive/validation/artifacts/sp12-attempt7-grub-config-read-20261114/installed-grub.cfg`; its SHA-256 matches the ledger's `f672512098384c1bef1a16ac179ee8075bceb2791a6d417fb0ee379473e494ed`.
- The two SHIP-CHECKLIST recovery links now use `../output/...` and resolve to existing files. The local Markdown-link scan found no missing targets among the ledger, checklist, queue, and linked baseline/GRUB/recovery reports.
- Both `cs-sp12` free-space figures are now described as snapshots, with an explicit statement that no fresh remote measurement was taken. Both remain below the 24 GiB build requirement. Individual timestamps are not supplied, so their sequence is not independently auditable from this ledger alone.

## Remaining check issue

`git diff --check` passes for the tracked checklist/queue changes. The new ledger is untracked, so I also checked it with `git diff --no-index --check /dev/null docs/PRIVATE-PILOT-QUALIFICATION.md`; this reports trailing whitespace at lines 3 and 4 (two Markdown hard-break spaces after the `As of` and `Baseline` lines). If a clean `git diff --check` result is required for the new ledger, remove those trailing spaces or use another line-break format.

No VM, test, build, or workspace edit was performed.
