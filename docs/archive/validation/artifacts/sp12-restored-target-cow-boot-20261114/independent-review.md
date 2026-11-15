# Final review: recovery boot report correction

The final report hash matches the supplied `b6fd49ad455334173c0896dc50de60e3ecc6f48fa584de93fca21482ccb12208`. The output manifest hash matches `f5d7dad801f99daafd550e92d7c85ea8a24b59682b5ac76c470d3a3f16fbbf45`, and its `sha256sum -c` check passes.

The pre/post COW identity claim now has persisted pre-run evidence: `pre-run-cow-hashes.txt` is included in the output manifest, and its two recorded digests match both final overlay files and their manifest entries exactly:

- Root child: `ca06595c5241d89d36f3c33a742444bf975ef3bf2e743920ce464f4a6af863ba`
- Data child: `c737376ae16f256744ae7316b43f5f1a33670492508944a0269365533bea388d`

The scratch wording now distinguishes the run-time peak (`1,001,230,336` bytes) from current usage at report correction (`1,001,242,624` bytes). My current `du -sB1` measurement is `1,001,242,624` bytes, matching the latter. Both are below the 2 GiB cap. No remaining issue found in this correction.
