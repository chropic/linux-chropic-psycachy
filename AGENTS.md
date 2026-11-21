@RTK.md

# Working on PsyCachy

**Start with [the backlog](docs/BACKLOG.md)** for release work. Read the row for
your target (B550I AMD64 or SP12 ARM64) and its first open gate. For a scoped
code fix, go straight to the file and its test. The [README](README.md) is a
directory map, not another required read.

- **Inputs:** follow the backlog's exact manifest and package-pin links.
  `config/kernel/` holds both 7.3.5 C configs and the SP12 R comparison.
  Search for the `CONFIG_` symbol you need; don't load a whole kernel config.
  `build.sh` defaults to historical pins. Use the [patch review](docs/production-7.3.5-patch-contract-review.md)
  only for a specific patch, dependency, or selection decision.
- **Code:** start in `targets/<target>/` for hardware and boot, `iso/` for
  builders/installers, `tools/` for audits and benchmarks, `tests/` for checks.
  Search the relevant directory for a filename or symbol, then read the matching
  lines. Include untracked active files: this checkout contains work in progress.
- **Skip `docs/archive/` by default.** Use the [public evidence summaries](docs/archive/README.md) only to verify a
  specific claim. Original captures are private; never stage them. Don't recursively scan `output/` (local run
  artifacts) or `.local-work/` (private inputs, scratch, nested checkouts).
- **Verify and record:** run the focused test first; `bash tests/static-check.sh`
  is the repository check. When a gate or next action changes, update the
  backlog row and link the evidence once. Don't create a parallel checklist or
  handoff. A VM pass cannot stand in for physical qualification.
