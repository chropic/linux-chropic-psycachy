# Targeted generated-artifact cleanup — 2026-11-15

**As of:** 2026-11-15 18:33 UTC / 11:33 MST
**Scope:** Retire selected superseded generated binaries and redundant staging copies while keeping active media, signed inputs, recovery records, and VM evidence intact. One old, unqualified SP12 candidate binary was retired by the user's cleanup decision; its identity and source records remain. No VM, build, hardware write, or firmware change was performed.

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

The cleanup also pruned nine stale Git worktree registrations whose target paths no longer existed. No existing worktree or branch was removed; modified worktrees were left intact.

## Capacity after cleanup

| Host | Before | After | Change |
| --- | ---: | ---: | ---: |
| Local `/` | 86,578,343,936 B free | 111,558,193,152 B free | +24,979,849,216 B |
| SP12 `/` and `/var/tmp` | 19,247,431,680 B free | 37,314,920,448 B free | +18,067,488,768 B |

At the 18:33 UTC follow-up, local free space is 103.90 GiB: 23.90 GiB above the 80 GiB reserve and 16.10 GiB below the 120 GiB target. Repeating the recorded 12,715,630,592-byte disposable target allocation would leave about 12.05 GiB above the reserve. SP12 has 34.75 GiB free, about 2.94 GB below the current approximately 40.26 GB installer-snapshot/output planning floor, before extra build margin. Do not start that combined build on this measurement.

The local before/after free-space delta is the measured `df` change. The first unprivileged cleanup delta differed by 178,138,125 bytes from the sum of the listed file lengths and extracted-tree allocation; per-file allocated bytes were not captured for every deleted item, so the file-length sum is not a reclaim estimate. The 18:33 readings followed the two user-supervised ISO removals; intermediate readings were recorded during cleanup and documentation work.

## Preserved artifacts and completed supervised cleanup

The signed Ubuntu 26.10 ARM64 input ISO and signature/checksum files, final51 builder workspace and media, current Ventoy files, v4 fallback ISO, complete audit tree extracted from the experimental image, recovery inputs/evidence, extracted transfer evidence, source archive/signature/key, and historical installer QCOW evidence remain. In particular, the standalone AMD64 attempt-2 QCOW remains because it is unique historical installer-state evidence. The modified Codex worktrees also remain intact.

The user completed both remaining removals after the checksum checks returned `OK`. Read-only follow-up confirmed the two ISO paths are absent, the local `SHA256SUMS`/manifest/build log remain, and the SP12 `.iso.sha256` remains. The separate earlier physical USB image is preserved; its `fdt-fix` ISO sidecar still verifies `OK`.

The post-cleanup check found `/var/tmp/sp12-installer-2610/private-live-v2.l7kr0pl9` absent and no exact-size copy in accessible local or remote paths. The user confirmed that this old private-live-v2 candidate should remain retired; no rebuild was started. Its recorded hash and build provenance remain, but an exact binary cannot be recovered from them.
