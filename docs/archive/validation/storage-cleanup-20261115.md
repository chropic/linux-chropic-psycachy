# Targeted generated-artifact cleanup — 2026-11-15

**As of:** 2026-11-15 18:57 UTC / 11:57 MST
**Scope:** Retire superseded generated binaries and large generated build outputs while keeping active media, signed inputs, source changes, recovery records, and VM evidence intact. One old, unqualified SP12 candidate binary was retired by the user's cleanup decision; its identity and source records remain. The original 18:57 UTC snapshot preceded the later combined ISO build; its no-build/no-write status is historical. Follow-up work is timestamped below.

## Checks and removals

Before deletion, local process and mount checks found no running QEMU/build job or project image mount. Ventoy remained mounted and untouched; its AMD64 image hash `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c` had been read back and verified. The SP12 connection used the already-authorized Tailscale SSH path and matched the previously verified `cs-sp12` peer identity; no remote build/QEMU process or project mount was active.

The following generated copies were retired after checking their identity:

| Host | Retired artifact | Identity / verification | Retention |
| --- | --- | --- | --- |
| Local | `output/amd64-iso-reconstructed-20261113/psycachy-ubuntu-26.10-desktop-amd64.iso` | 8,052,146,176 bytes; adjacent `SHA256SUMS` check returned `OK`; SHA-256 `73610dc5848d48a9379177fce5af8bae43cd089a7f4223ec163fa6a96f55be9e` | User removed the root-owned ISO after verification; `SHA256SUMS`, manifest, and build log remain. |
| Local | `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso` | 8,052,277,248 bytes; SHA-256 `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c` | Exact copy remains on Ventoy; build sidecars and review records remain. This is the known pre-fix artifact and is not eligible for qualification. |
| Local | `output/.unattended-luna-20261111210910Z/qemu-hosting/sp12-live-build-20261112/sp12-ubuntu-26.10-arm64-live-private.iso` | 4,810,289,152 bytes; SHA-256 `dfd9c3e081a002a8a9ad572750d4998da06255dd7a51cb223b5271f07b210523` | Local build metadata remains. Its exact-match remote copy was also removed after the sidecar check returned `OK` (see SP12 row below); distinct from the earlier physical USB image and final51. |
| Local | `output/.unattended-luna-20261111210910Z/qemu-hosting/fat-delay-qualification-20261112/sp12-runtime-evidence.tar.gz` | 3,193,310,221 bytes; SHA-256 `a9da552f68cb62e6d72d53a83210cd44559fb45e493abdaf94ea2b330fdda8d8` | A streaming comparison had matched all 52 archive files to the extracted evidence tree; two additional local manifests remain in that tree. |
| Local | `output/.unattended-luna-20261111210910Z/qemu-hosting/source/extracted/qemu-11.1.3/` | About 1,084,145,664 allocated bytes | Re-creatable from the retained `qemu-11.1.3.tar.xz`; its detached signature and public key also remain. |
| SP12 | `/var/tmp/sp12-installer-2610/output/sp12-ubuntu-26.10-arm64-experimental.iso` | 4,739,092,480 bytes; sidecar check passed; SHA-256 `99f817b1e82b414ce2ecbc999409cf43b63622736c29041dbce111032c448725` | `.iso.sha256`, `.buildinfo`, source, signed base ISO, and candidate records remain. |
| SP12 | `/var/tmp/sp12-installer-2610/output/sp12-ubuntu-26.10-arm64-private-live-v2.iso` | 4,971,847,680 bytes; sidecar check passed before removal; SHA-256 `d550c05575196069bd458f3a97c04acfc6660ceb4cdb5e7b7dab37879b6b6ec5` | Sidecar, buildinfo, source, signed base ISO, and candidate records remain. Earlier storage review marked it as a unique unqualified candidate; after the root-only temp path was found absent and no exact copy was located, the user chose to leave this old iteration retired rather than rebuild it. Its exact bytes are no longer retained. The experimental ISO audit tree is not a substitute. |
| SP12 | `/var/tmp/sp12-live-output-20261112/sp12-ubuntu-26.10-arm64-live-private.iso` | 4,810,289,152 bytes; sidecar check returned `OK`; SHA-256 `dfd9c3e081a002a8a9ad572750d4998da06255dd7a51cb223b5271f07b210523` | User removed this pre-final51 test ISO; its `.iso.sha256` remains. The separate earlier physical USB image is preserved. |
| SP12 | `/var/tmp/sp12-installer-2610/audit/minimal.squashfs` | 3,546,411,008 bytes; SHA-256 `dbd668a75a974192d29c9bc82671084533e0b266d8b67d30b572d4424f36b7dd` | Exact byte match to `candidate-audit/tree/casper/minimal.squashfs`; retained the complete candidate audit tree and the smaller audit records. |
| SP12 | Generated Kbuild outputs in `/home/charlie/src/linux-7.2-final-sp12`, `/home/charlie/src/linux-7.2-sp12`, `/home/charlie/src/sp12-extra-test`, and `/home/charlie/src/sp12-panel-worktree` | Sequential `ARCH=arm64 make -j1 clean` after dry-run and independent review; combined allocated tree size fell from 192,715,358,208 B to 11,225,079,808 B | All four dirty checkouts remain. Tracked-diff and untracked-source fingerprints are unchanged; `.config`, signing keys, `.orig` source backups, and package archives remain. |
| SP12 | Six `/home/charlie/src/linux-image-*-dbg_*.deb` debug-symbol packages | All six exact SHA-256 checks returned `OK` before removal; 10,598,694,912 allocated bytes total | Removed the uninstalled Linux 7.2/7.2-rc7 debug packages. Their `.changes` and `.buildinfo` records remain, along with every non-debug image and header package. |

The cleanup also pruned nine stale Git worktree registrations whose target paths no longer existed. No existing worktree or branch was removed; modified worktrees were left intact.

## Capacity after cleanup

| Host | Before | After | Change |
| --- | ---: | ---: | ---: |
| Local `/` | 86,578,343,936 B free | 111,054,667,776 B free | +24,476,323,840 B |
| SP12 `/` and `/var/tmp` | 19,247,431,680 B free | 229,403,607,040 B free | +210,156,175,360 B |

At 18:57 UTC, local free space is 103.43 GiB: 23.43 GiB above the 80 GiB reserve and 16.57 GiB below the 120 GiB target. Repeating the recorded 12,715,630,592-byte disposable target allocation would leave about 11.58 GiB above the reserve. SP12 has 213.65 GiB free, about 189 GB above the approximately 40.26 GB installer-snapshot/output planning floor. Complete the exact-input preflight before starting the combined build; no build was started during cleanup.

The capacity-table deltas are measured `df` changes from the initial cleanup snapshots, not sums of file lengths. The first local unprivileged-cleanup delta differed by 178,138,125 bytes from the listed file lengths and extracted-tree allocation; file lengths are not a reclaim estimate. For the four SP12 trees, `du` showed a combined 192,715,358,208 B before and 11,225,079,808 B after; the `df` increase during those cleans was 181,490,237,440 B, within 40,960 B of the `du` delta. The six debug-package unlink operations freed another 10,598,662,144 B by `df`; their allocated block total was 10,598,694,912 B.

## Preserved artifacts and completed supervised cleanup

The signed Ubuntu 26.10 ARM64 input ISO and signature/checksum files, final51 builder workspace and media, current Ventoy files, v4 fallback ISO, complete audit tree extracted from the experimental image, recovery inputs/evidence, extracted transfer evidence, source archive/signature/key, runtime image/header package archives, and historical installer QCOW evidence remain. In particular, the standalone AMD64 attempt-2 QCOW remains because it is unique historical installer-state evidence. The four SP12 source worktrees remain at their original commits with their dirty tracked and untracked source unchanged; only generated Kbuild outputs were cleaned.

The user completed both remaining removals after the checksum checks returned `OK`. Read-only follow-up confirmed the two ISO paths are absent, the local `SHA256SUMS`/manifest/build log remain, and the SP12 `.iso.sha256` remains. The separate earlier physical USB image is preserved; its `fdt-fix` ISO sidecar still verifies `OK`.

The post-cleanup check found `/var/tmp/sp12-installer-2610/private-live-v2.l7kr0pl9` absent and no exact-size copy in accessible local or remote paths. The user confirmed that this old private-live-v2 candidate should remain retired; no rebuild was started. Its recorded hash and build provenance remain, but an exact binary cannot be recovered from them.

## Follow-up — exact-copy deduplication and combined-build staging

After the initial storage snapshot, duplicate local package data was
deduplicated with hardlinks while preserving both pathname trees and their
checksum sidecars:

- 120 `.deb` files in the old SP12 r2 offline-package tree now share data with
  exact package copies retained in the final51 or prior r2 package tree.
- 114 matching `.deb` files in the old v4 fallback closure share data with
  final51 package copies. Six v4-only packages remain separate.
- Two byte-identical FAT-delay qualification helper QCOW bases share one data
  inode. Both paths remain and the recorded remote-tree manifest still
  verifies; `qemu-img check` passed on both paths, and no QEMU process was
  running.

The estimated allocated saving is about 1.58 GB; measured local `df` free
space increased by 1,562,341,376 bytes from the post-cleanup snapshot. At
2026-11-15 13:05 MST, local `/` had 112,617,009,152 bytes free (104.9 GiB).
All linked package and QCOW contents were exact SHA-256 matches before
deduplication. The directories, individual filenames, adjacent package
metadata, and recovery paths remain available.

The native SP12 combined build and independent content audit then completed;
see the [build report](sp12-combined-build-20261115.md). The seven exact
staging and scratch directories listed above were removed by the user's
interactive run of the guarded cleanup script. It rechecked the final ISO
before and after cleanup and verified the host, canonical paths, mounts, and
processes. Its output reported 38,570,512,384 allocated bytes removed and
free space rising from 185,371,549,696 to 223,942,037,504 bytes. A subsequent
read-only check confirmed all seven paths absent, the final ISO, sidecar,
buildinfo, runner and log still present, and 223,941,722,112 bytes free on
`cs-sp12`. The old live-only recovery image and its metadata remain in the
separate `/var/tmp/sp12-r2-final51-build/output` tree.

After a separate user-approved checkpoint, the combined ISO replaced the
older live-only SP12 file on the existing Ventoy data partition. The full
destination hashes passed for the combined image and protected AMD64 image;
2,138,603,520 bytes remain free. No partition-table, VTOYEFI, firmware,
Apple HDD, or installation-target write occurred. See the
[Ventoy write record](sp12-combined-ventoy-write-20261115.md).

## Follow-up — local duplicate repository retirement

At 2026-11-15 21:48 UTC, a new read-only review found no safe large VM or
recovery artifact to retire. The 34 GB allocated QEMU tree contains required
backing images, recovery fixtures, and unique installer-state evidence; the
12,715,425,792-byte standalone AMD64 attempt-2 QCOW is explicitly retained as
unique evidence. Sparse raw placeholders do not account for their apparent
logical size. No active VM/build process, output-specific mount, or open file
was present during the review.

The one byte-identical generated tree was
`output/.unattended-luna-20261111135015Z/arm64-offline-repo/`. It contained
123 dereferenceable entries: 118 package symlinks to the separately retained
`output/arm64-offline-20261110b/` tree and five regular metadata files. Every
entry's SHA-256 and size matched the corresponding file in the retained
`output/.unattended-luna-20261111210910Z/iso-arm64-refreshed-v4/offline-packages/`
tree; that tree also retains `packages.tsv`. The old tree had no external
hardlinks. Only that duplicate directory was removed. Its measured allocated
size was 148,193,280 bytes, and local free space increased by the same amount
from 104,610,836,480 to 104,759,029,760 bytes. The retained v4 package
checksum manifest passed after removal.

The signed AMD64 and ARM64 base ISOs, corrected AMD64 prompt-fix candidate,
SP12 final51 installer, v4 fallback ISO, private inputs, and evidence trees
were all kept. No byte-identical full ISO copy was found. The project's
`.agents` and `.codex` directories are about 1.5 MB and 8 KB respectively and
remain intact.

## Follow-up — AMD64 failed iteration retirement (2026-11-15)

After the Secure Boot installation attempt failed on the parser bug, the
standalone disposable VM directory
`output/amd64-iso-lifecycle-vm-20261115-promptfix/` was removed after checking
that its target QCOW had no backing file, had a clean `qemu-img check`, was
not mounted or open, and had no active QEMU process. It contained a
10,711,855,104-byte partially written target QCOW, VM-local firmware
variables, and a small log; the separate screenshots, serial output, hash
records, manifest, protected sentinel, and retained VM bases were preserved.
The user-run cleanup increased `/` free space from 93,913,972,736 to
104,626,585,600 bytes.

The failed candidate ISO was then checksum-verified (`SHA256SUMS: OK`) before
its local binary was retired. It was never staged on Ventoy; its build
manifest, log, checksum identity, and failure report remain. No other ISO or
recovery artifact was removed. After this cleanup, local `/` had
104,619,188,224 bytes free. The new fixed-source candidate
`output/amd64-iso-lifecycle-20261115-nvidiafix/` is retained at its verified
SHA-256; it is the only local image for the next install attempt.

The independent ISO audit temporarily extracted 1.7 GB of ISO contents to
`/tmp/amd64-iso-audit.3XMyBJHE` on tmpfs. The extracted EFI files were
root-owned, so the user removed that exact scratch directory with `sudo`; the
`/tmp` tmpfs returned to about 16.16 GB available. The new Secure Boot VM
uses freshly initialized sparse target and sentinel QCOWs; no target data was
written when QEMU first reached the signed GRUB menu.
