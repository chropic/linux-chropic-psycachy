# Pilot artifact retention

Use the dated [current artifact keep list](archive/validation/current-artifact-keep-list-20261116.md)
before removing any generated file. Treat pins and SHA-256 manifests as the
authority; filenames, release labels, and old report links do not establish
that a binary is current.

The keep list is a short-lived snapshot, not a permanent archive allowlist.
Revalidate it after each completed qualification step. Remove the child
overlay and copied firmware variables as soon as a run ends; remove the base
fixture after its last dependent test and after all process/monitor references
are released. A VM that remains active because its monitor is connected stays
listed until clean shutdown.

## Keep

- Current checksummed AMD64 and SP12 pilot images, their signed Ubuntu bases,
  exact pinned package pairs, complete offline dependencies, authenticated
  source archives, private support files, current source changes, signing
  material, compact reports, manifests, and recovery/fallback payloads.
- At most the two explicitly listed temporary VM fixtures, and only until
  their remaining tests finish. Use fresh child overlays and copied firmware
  variables for each run. Delete each child and its fixture immediately after
  the test; retain compact logs, screenshots that prove a result, and hashes.
- At least 80 GiB free on the local filesystem before starting a build or VM
  that allocates more than 1 GiB. Stop before a projected run crosses that
  reserve. Run one heavy job at a time and remove its disposable output when
  the report is complete.

## Remove

- Superseded ISO candidates and package generations after verifying their
  sidecars and retaining the compact build/audit records.
- Completed or abandoned VM families, sparse raw/QCOW disks, firmware-vars
  copies, extracted audit/source copies, generated Kbuild outputs, duplicate
  offline repositories, and replay/cache trees after checking there is no
  active process, mount, required backing chain, or unique source change.
- Do not create binary archives as a cleanup substitute. Preserve unique
  source changes as source/patches and keep concise evidence in `docs/`.

## Before deletion

1. Read active config pins and manifests and write the keep list first.
2. Check running build/VM processes, open file references, mounts, backing
   chains, and source diffs. Never repair or fully hash a large VM that is
   already superseded and scheduled for removal.
3. Verify that required recovery and fallback data remain on distinct paths.
4. Record allocated bytes reclaimed (`du`/`stat`) and `df -B1` free space
   before and after. Treat the `df` delta as a measured net change because
   other filesystem activity can move the value between samples.
5. Update the qualification ledger, implementation queue, and ship checklist
   with the exact remaining gates and local/remote capacity.
