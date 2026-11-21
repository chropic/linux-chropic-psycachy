# PsyCachy

Two private Ubuntu 26.10 desktop ISOs, built around patched CachyOS Linux
7.3.5: ARM64 for the Surface Pro 12 and AMD64 for the B550I. Each image must
run its target kernel in **Try**, **Install**, and the **default installed boot**.

Start with the [release backlog](docs/BACKLOG.md) for each target's status,
next decision, open hardware issues, and acceptance criteria. To review a patch, follow its link to the
target manifest. To check a checkout, run `bash tests/static-check.sh` from the
root on Linux with the project toolchain.

## Repository map

| Where | What lives there |
|---|---|
| [`config/kernel/`](config/kernel/) | Full kernel configs: `b550i-C` and `sp12-C` are the selected baselines; `sp12-R` is the comparison config |
| [`config/`](config/) | Builder inputs: package and ISO pins, shared packaging patches, legacy config fixtures |
| [`targets/`](targets/) | Per-machine manifests, platform patches, boot helpers and provenance |
| `build.sh` | Package-builder entry point. Its default source pin is historical; use the backlog to identify C inputs. |
| `iso/build.sh`, `iso/build-arm64.sh`, `iso/build-sp12-live` | AMD64 installer, ARM64 installer, and Surface live-image builders |
| `tests/`, `tools/` | Repository checks and fixtures; target audits, recovery and performance tools |
| `output/` | Local generated artifacts and run evidence; not included in Git |
| [`docs/archive/`](docs/archive/README.md) | Sanitized evidence summaries; look up by task |

Local-only checkouts and vendor or scratch files belong in ignored
`.local-work/`, separate from disposable build output. On the development
machine, `.local-work/checkouts/` contains `phase0-work` and `sp121-reference`;
older provenance records use their original root-relative names. Published
manifests and dated reports likewise retain the config paths used at build time.
