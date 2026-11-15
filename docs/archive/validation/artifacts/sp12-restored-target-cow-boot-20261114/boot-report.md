# Disposable restored-target boot attempt — 2026-11-13

## Result

The single authorized 600-second QEMU TCG run **did not establish restored-target userspace**. It exited with timeout status `124`; `qemu.stderr` says QEMU was terminated by the timeout with signal 15. Serial shows firmware loading and starting `Boot0007` from GPT partition GUID `9F85B3C4-7D20-4BA4-9955-ABC860EB2026`, path `\EFI\BOOT\BOOTAA64.EFI`, then no further serial text. It provides no captured GRUB menu, kernel, initrd, userspace proof, or guest poweroff.

This is an absence of proof, not a diagnosis that GRUB or the kernel failed: the target GRUB configuration has no serial terminal and the run used `-display none`. No other userspace signal was found. The recorded pre-run hashes are persisted in `pre-run-cow-hashes.txt` (SHA-256 `21c305e98e3518cd11fd9bb0acacf90370352213c931297270ea2098755ae8f5`) and match the final COW hashes shown below; `qemu-img map` also reports zero depth-0 data bytes in each. The hash values were captured before QEMU in the tool result transcript and added to the output packet during this reconciliation because they were omitted from the original manifest. Do not infer boot success from QEMU CPU use or infer its precise stop point from those unchanged overlays.

## Run and safety record

One VM was run with QEMU 11.0.3, `virt,accel=tcg,gic-version=3`, `-cpu max -smp 4 -m 4096`, `-nic none`, a new root COW child, a new data COW child, a new disposable vars copy, the corrected wrapper ESP copy, and a read-only NoCloud seed ISO. The seed was intended to emit runtime uname, root/ESP/data mount identities, package audit, and restored-payload checks, then power off. The boot never produced this report. No second VM was started.

The wrapper copy changes only the GRUB stub path from `configfile /grub.cfg` to `configfile ($root)/grub/grub.cfg`. The parsed post-run FAT copy confirms that line and still contains the restored `SP12BOOT`, kernel, initrd, and DTB. `fsck.vfat -n -v` passed on a read-only extracted copy of the ESP partition: 13 files, 24,892/130,811 clusters, with no reported FAT errors. GPT verification also passed. This is a filesystem integrity check after an unclean VM timeout, not proof of a clean guest shutdown; the guest did not report its planned poweroff.

All supplied baseline hashes were rechecked before and after the run. The root QCOW chain, data raw fixture, existing data COW, original ESP wrapper, original vars file, and AAVMF code stayed unchanged. `qemu-img check` passed for both new COW overlays and the root/data QCOW chain. The existing data COW was attached only through the authorized new child overlay; the raw fixture and existing COW were not attached writable, and no user files in that data image were inspected.

A read-only in-guest journal/log/package audit was not possible after timeout. `/dev/nbd*` was unavailable, and `sudo -n modprobe nbd` failed because interactive authentication is required. `guestfish`, `guestmount`, and a QCOW-aware ext4 reader are not installed. I did not try a writable NBD attach, convert the full disk, or start another VM. This leaves the required clean `dpkg --audit`, running kernel, root/ESP mount evidence, and in-guest payload comparison unverified.

Peak allocated scratch measured during the run was 1,001,230,336 bytes. Current run-directory usage at this report correction is 1,001,242,624 bytes. Both measurements are below the 2 GiB cap. No project/workspace source file or status document was modified; all new run artifacts are under this directory.

## Input identities

`pre-run-inputs.sha256` contains each pinned hash, and all entries passed the pre- and post-run `sha256sum -c` checks. The exact reference identities were:

| Input | SHA-256 |
|---|---|
| target root top | `45730eecd602ea92afe4c441ca1ce243549072056221b3f7ba2e422faba636de` |
| root backing 1 | `ed5543a9c27fd15a1305662fcbd3821265eb944fea059a1a83b28c83feeef43d` |
| root backing 2 | `79012dcd334bc252cf85c3be45315459fab1417bb15416e00517a8ddd4e256e6` |
| root backing 3 | `94bf7970a97a635cb7e06a498ca59fd3403634081cf5b14a00abad3e86db0d9e` |
| root backing 4 | `90c07f4b58d7a06bc5525a41db4d32501e36fbab3e6ae05405b81e38c406d7a8` |
| allowed data raw fixture | `4c9bc9f49f6e710115dceb0a41c90bbeeeeb5d33609200dd24a655ee205ab6cf` |
| existing disposable data COW | `addae43aa8036169fb0737d9cb4e639195283b9d06779df39398620cb702a77a` |
| original ESP wrapper | `188a88e5eaa04d7304dc1f2937a533b490fec51e6e493bcf95c93ca880b46b3e` |
| original disposable vars | `17d1404e39c996491d0e4f4cffced32f91aaa8a41c3eb7a449409c192c8d1d2c` |
| AAVMF code | `e58a9508f0d1d0891526680d44625f44550dcb12be8b9e8331dd2c2aae7d61e5` |

The pre-run input manifest SHA-256 is `fce4668eed4cdbc1e1f6c4920f0f2b94089752fb84c90e81d1417c12cbd825bb`. All the above source hash values also appear in `post-run-input-hash-check.txt` as `OK`.

## New output hashes

The complete output inventory is `output-manifest.sha256` (SHA-256 `f5d7dad801f99daafd550e92d7c85ea8a24b59682b5ac76c470d3a3f16fbbf45`). Key outputs:

| Output | SHA-256 |
|---|---|
| root child COW, pre/post identical | `ca06595c5241d89d36f3c33a742444bf975ef3bf2e743920ce464f4a6af863ba` |
| data child COW, pre/post identical | `c737376ae16f256744ae7316b43f5f1a33670492508944a0269365533bea388d` |
| patched ESP wrapper copy | `5fadd7ab894bd9065814104a75dfb67e2f5887983ebd2f7d8221c4c3fbc2c402` |
| disposable vars after run | `7f352e4cd5e720efe498a45eac0b948e689512c8653ff7fa60cd66e1573d7be3` |
| serial log | `ab4fcf1d49052218d89c6639c076d6cf2b77f5aff252b468dcf36af099f804a6` |
| QEMU stderr | `e89b849aa5b9f21a63ee826834f1a411a63e8a671e5cefa24b1b1fbb83192caf` |
| QEMU exit status file (`124`) | `ca2ebdf97d7469496b1f4b78958f9dc8447efdcb623953fee7b6996b762f6fff` |
| read-only extracted FAT volume | `58fb9a1ae4925084299e46dbbe8ddb8a0abf1aeb53d89c5599b30729db2659a1` |
| NoCloud seed ISO | `61150bc7cce50147531726f4c01c88103fe80c1a55f8976c2c332c85847d9d39` |
| QEMU command text | `628929653578442d6d741ed71f72e82b483d0923d5d7d66a617f907e130a01a4` |

The SHA-256 for `fsck-fat-final.txt` is `0d2475f11cb37ef254c78b5aa36eeedb145372f98eb87e518f6dedca05da4a62`; the parsed patched wrapper inspection is `080ed6b55883fb4545ae1e8eac3be15b82809a6380f9965533cf7a1825dc4e5f`. The output manifest lists hashes for every run artifact present before report finalization, including scripts and logs; it excludes itself and this report.

## Disposition

The GRUB path edit and EFI selection are demonstrated only through the UEFI loader-start record and parsed wrapper content. Restored-target userspace remains unqualified in this run. A later attempt would need a capture path that observes the target display or adds an approved serial console while preserving the same COW-only disk/vars controls; that is not part of this completed bounded run.
