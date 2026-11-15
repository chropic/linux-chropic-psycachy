# AMD64 lifecycle ISO live boot smoke

**Recorded:** 2026-11-14 03:57 UTC  
**Reviewed:** 2026-11-14 04:10 UTC  
**Candidate:** `output/amd64-iso-lifecycle-20261114-build2/psycachy-ubuntu-26.10-desktop-amd64.iso`  
**SHA-256:** `e81c6d16740849e6b0b85eedf011a2317b0ae0ce42965a43134068ad87c6aa1c`  
**Result:** UEFI boot reached the guarded graphical disk selector; no installation was started.

## Run and observations

A bounded, network-disabled QEMU 11.0.3/KVM run used the existing
`tests/iso-vm.sh` harness with fresh `init-insecure` firmware variables,
OVMF's non-Secure-Boot code, 2 vCPUs, 4 GiB RAM, one writable 64 GiB virtual
QCOW target (`psycachy-linux`), and one read-only 64 GiB sentinel QCOW. The
candidate ISO was attached as read-only CD-ROM media.

UEFI started the ISO and GRUB 2.14 displayed its normal Ubuntu menu. The
serial capture included `error: can't find command 'grub_platform'`. The same
bare `grub_platform` line is present at line 18 of the signed base ISO's
`/boot/grub/grub.cfg`; the candidate inherited it, and it did not prevent this
observed boot. The default Try or Install entry reached the Ubuntu live desktop
and the PsyCachy disk selector. The captured selector listed only `/dev/vda`,
serial `psycachy-linux`, size 68.7 GB. It warned that the selected disk would
be erased; its checkbox remained empty. No disk, install mode, or `ERASE`
confirmation was selected. The VM stopped at this screen via the QEMU HMP
`quit` command and the wrapper reported exit status 0. The status and monitor
action are preserved as lead-recorded tool results; the bundle does not
contain a raw QEMU exit-status file or full monitor transcript, so that part
is not independently re-verifiable from raw output.

The target COW passed `qemu-img check` and its map reports the complete virtual
range as not present, with no data blocks. The sentinel COW passed its check,
pre-run SHA-256 verification, and 1 MiB read test. The exact candidate
`SHA256SUMS` also passed after the run. No guest installation,
installed-system login, activation, acknowledgement, promotion, reboot, or
rollback was attempted. The live desktop auto-logged in; no installed-system
login was tested. This was not a Secure Boot run and does not establish B550I
GPU or hardware behavior.

## Storage boundary

At 03:55 UTC after the smoke and checks, `/` and `/var/tmp` had 97,450,049,536
bytes free. That is 11,550,703,616 bytes (10.76 GiB) above the plan's 80 GiB
reserve. A retained earlier AMD64 installer VM target used 12,715,630,592
bytes of actual allocation. Repeating an install at that observed scale would
exceed current above-reserve headroom by 1,164,926,976 bytes (about 1.08 GiB).
The `/tmp` tmpfs also had only 12,805,242,880 bytes free and would place the
allocation on memory-backed storage. A full disposable install was therefore
not started. Re-measure after freeing or adding space before scheduling that
qualification.

## Evidence

The [checksummed evidence bundle](artifacts/amd64-lifecycle-iso-liveboot-20261114/)
contains the GRUB, splash, and disk-selector screenshots; raw serial and QEMU
logs; disposable COWs and firmware variables; candidate checksum check;
post-run QCOW/sentinel checks; QEMU invocation; and tool/input hashes. The
outer evidence-manifest file (`SHA256SUMS`) SHA-256 is
`fb43243df0f109fd53c390bc6d6c4fe412aac2561704607dab56f95e722d8de9`. An
independent reviewer approved the no-write and storage claims; the review is
at [independent-review/review.md](artifacts/amd64-lifecycle-iso-liveboot-20261114/independent-review/review.md)
(SHA-256 `d5ce7d350376249450f1769b3054240af95f55ef6264e01eab7ce1396c5427eb`;
separate checksum-manifest SHA-256 `a7a205529a09b65318b9e7917fe352104a3df3b710d44c8d564f3568f649e72d`).
It confirms the reserve arithmetic and local links, and notes the wrapper exit
status is recorded but not independently verifiable from raw retained QEMU
output. The build, package closure, and selected embedded payload audit are
recorded in the [ISO build record](amd64-lifecycle-iso-build-20261114.md).

This result establishes boot through the guarded disk-selection screen only.
The disposable installation, activation lifecycle, Secure Boot, NVIDIA, and
physical B550I gates remain open.
