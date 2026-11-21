#!/usr/bin/env bash
# Build a private AMD64 7.3.5 C candidate. No installation or media operations.
set -Eeuo pipefail
IFS=$'\n\t'

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
readonly candidate_inputs="$root/targets/b550i-amd64/inputs.json"
readonly build_context_lock="$root/targets/b550i-amd64/BUILD-CONTEXT.sha256"
readonly source_archive="$root/output/prestable-20261118/inputs/cachyos-7.3.5-2.tar.gz"
readonly source_signature="$source_archive.asc"
readonly signer_key="$root/output/prestable-20261118/inputs/cachyos-signer.asc"
readonly approved_config="$root/output/prestable-20261118/configs/b550i-C.config"
readonly toolchain_lock="$root/output/prestable-20261118/toolchain-debs/SHA256SUMS"
readonly bore_patch="$root/targets/sp121-arm64/patches/r2/scheduler/01-bore-cachy-7.3.5.patch"
readonly slub_patch="$root/targets/sp121-arm64/patches/r2/security/01-slub-canary-7.3.5.patch"
readonly cpu_target=znver3
readonly source_sha256=bb22ad99e1042fae883bab71366f8339367b74c045004fe92ad4923339092e07
readonly signer_fingerprint=E8B9AA39F054E30E8290D492C3C4820857F654FE
readonly config_sha256=3e6665aab949a1a7ac68d7d4620c339ff69abf7af5d0fe97fde46d3e98d79cb1
readonly bore_sha256=d2eaa8e8dbf1f56bfb304f8b437a7dc30a65408f90a93701367baf8adc2173b4
readonly slub_sha256=ef912876e259d95321778268f3ec448932f2f76778b3092d38b694e75aa51f17
readonly dkms_patch_sha256=1e543f84690f7935c7dcd927d785b032561e7caa789d5d114e91b3798b1b1663
readonly headers_patch_sha256=3fbfe37888f961f1cc3cd8278600851b56047b791270fc66f0b3d8fab33d60d9
readonly dependencies_patch_sha256=d938c88ddd54d285b44b0b0a7c352e0d77f568343edde9bd5b6708edbc842b55
readonly pkg_version=7.3.5-1psycachy1~prestable20261119.1
readonly expected_release=7.3.5-psycachy-b550i-c

die() { echo "error: $*" >&2; exit 1; }
usage() {
  echo "Usage: $0 OUTPUT_DIR STAGED_TOOLCHAIN_ROOT|native [JOBS]"
}

[[ $# -ge 2 && $# -le 3 ]] || { usage >&2; exit 2; }
output_dir=$1
toolchain_mode=$2
jobs=${3:-4}
[[ $jobs =~ ^[1-9][0-9]*$ ]] || die 'JOBS must be a positive integer'
if [[ $toolchain_mode == native ]]; then
  native_mode=true
  toolchain_root=
else
  native_mode=false
  toolchain_root=$toolchain_mode
  [[ -d $toolchain_root/usr/bin ]] || die 'staged toolchain root is missing usr/bin'
fi

for command in python3 sha256sum gpg gpgv git make tar dpkg-deb dpkg-buildpackage \
  dpkg-gencontrol dpkg-architecture perl openssl; do
  command -v "$command" >/dev/null || die "missing required host command: $command"
done
[[ -s $build_context_lock ]] || die 'B550I build-context lock is missing'
(cd "$root" && sha256sum --check "$build_context_lock") \
  || die 'B550I build-context checksum verification failed'
build_context_lock_sha256=$(sha256sum "$build_context_lock" | cut -d ' ' -f 1)

mkdir -p -- "$output_dir"
output_dir=$(cd "$output_dir" && pwd)
shopt -s nullglob
[[ -z $(find "$output_dir" -mindepth 1 -maxdepth 1 -print -quit) ]] \
  || die 'output directory must be empty'

verify_hash() {
  local expected=$1 path=$2
  [[ -s $path ]] || die "missing input: $path"
  printf '%s  %s\n' "$expected" "$path" | sha256sum --check --status \
    || die "input hash mismatch: $path"
}

verify_hash "$source_sha256" "$source_archive"
verify_hash 3218a02b9229e0e395657fa8d9bc5559e507ad59cb0013c8c4035a4067c0e94b "$source_signature"
verify_hash 33fe90b5188545e7013fab56573419755ac35b7b50f50680c256b4927aac4fe9 "$signer_key"
verify_hash "$config_sha256" "$approved_config"
if ! $native_mode; then
  verify_hash af37002a2c974b151f2dd23342bb55e7ceef7fb4602dbd17831441b6693c14ec "$toolchain_lock"
  (
    cd "$(dirname "$toolchain_lock")"
    sha256sum --check SHA256SUMS
  ) || die 'staged toolchain package checksums failed'
fi
verify_hash "$bore_sha256" "$bore_patch"
verify_hash "$slub_sha256" "$slub_patch"
verify_hash "$dkms_patch_sha256" "$root/config/patches/dkms-clang.patch"
verify_hash "$headers_patch_sha256" "$root/config/patches/headers-config.patch"
verify_hash "$dependencies_patch_sha256" "$root/config/patches/ubuntu-package-dependencies.patch"
[[ -s $candidate_inputs ]] || die 'candidate input manifest is missing'
python3 - "$candidate_inputs" "$root" "$expected_release" "$pkg_version" \
  "$source_sha256" "$config_sha256" "$native_mode" <<'PY'
import json
from pathlib import Path
import sys

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
root = Path(sys.argv[2]).resolve()
if manifest.get("status") != "private-prestable-test-only-not-for-release":
    raise SystemExit("candidate manifest is not marked test-only")
if manifest.get("candidate") != "C" or manifest.get("cpu_target") != "znver3":
    raise SystemExit("candidate identity/CPU target mismatch")
source = manifest.get("source", {})
config = manifest.get("config", {})
toolchain = manifest.get("toolchain", {})
expected = {
    "kernel_release": sys.argv[3],
    "debian_version": sys.argv[4],
    "target": "B550I / AMD64 / Ryzen 7 5800X3D",
    "source.archive": "output/prestable-20261118/inputs/cachyos-7.3.5-2.tar.gz",
    "source.release": "cachyos-7.3.5-2",
    "source.sha256": sys.argv[5],
    "source.signer_key": "output/prestable-20261118/inputs/cachyos-signer.asc",
    "source.signer_fingerprint": "E8B9AA39F054E30E8290D492C3C4820857F654FE",
    "source.signer_trust": "not-established",
    "config.path": "output/prestable-20261118/configs/b550i-C.config",
    "config.sha256": sys.argv[6],
    "cpu_codegen.c": "KCFLAGS=-march=znver3",
    "cpu_codegen.rust": "KRUSTFLAGS=-Ctarget-cpu=znver3",
    "toolchain.debian_package_lock": "output/prestable-20261118/toolchain-debs/SHA256SUMS",
    "toolchain.debian_package_lock_sha256":
        "af37002a2c974b151f2dd23342bb55e7ceef7fb4602dbd17831441b6693c14ec",
}
actual = {
    "kernel_release": manifest.get("kernel_release"),
    "debian_version": manifest.get("debian_version"),
    "target": manifest.get("target"),
    "source.archive": source.get("archive"),
    "source.release": source.get("release"),
    "source.sha256": source.get("sha256"),
    "source.signer_key": source.get("signer_key"),
    "source.signer_fingerprint": source.get("signer_fingerprint"),
    "source.signer_trust": source.get("signer_trust"),
    "config.path": config.get("path"),
    "config.sha256": config.get("sha256"),
    "cpu_codegen.c": manifest.get("cpu_codegen", {}).get("c"),
    "cpu_codegen.rust": manifest.get("cpu_codegen", {}).get("rust"),
    "toolchain.debian_package_lock": toolchain.get("debian_package_lock"),
    "toolchain.debian_package_lock_sha256": toolchain.get("debian_package_lock_sha256"),
}
if sys.argv[7] == "true":
    native = toolchain.get("native_b550i", {})
    expected.update({
        "toolchain.native_b550i.clang": "Ubuntu clang version 22.1.8 (1ubuntu1)",
        "toolchain.native_b550i.lld": "Ubuntu LLD 22.1.8",
        "toolchain.native_b550i.rustc":
            "rustc 1.97.1 (8bab26f4f 2026-07-14) (built from a source tarball)",
        "toolchain.native_b550i.pahole": "1.31",
        "toolchain.native_b550i.effective_native_cpu_target": "znver3",
    })
    actual.update({
        "toolchain.native_b550i.clang": native.get("clang"),
        "toolchain.native_b550i.lld": native.get("lld"),
        "toolchain.native_b550i.rustc": native.get("rustc"),
        "toolchain.native_b550i.pahole": native.get("pahole"),
        "toolchain.native_b550i.effective_native_cpu_target":
            native.get("effective_native_cpu_target"),
    })
drift = [f"{key}: expected {value!r}, got {actual[key]!r}"
         for key, value in expected.items() if actual[key] != value]
if drift:
    raise SystemExit("candidate manifest differs from pinned build inputs: " + "; ".join(drift))
for section in ("patches", "packaging_patches"):
    for item in manifest[section]:
        path = (root / item["path"]).resolve(strict=True)
        if not path.is_relative_to(root):
            raise SystemExit(f"input escapes repository root: {item['path']}")
        import hashlib
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise SystemExit(f"manifest hash mismatch: {item['path']}")
print("Candidate manifest inputs verified.")
PY
input_manifest_sha256=$(sha256sum "$candidate_inputs" | cut -d ' ' -f 1)

work_parent=${B550I_WORK_ROOT:-/var/tmp/opencode}
mkdir -p -- "$work_parent"
work=$(mktemp -d "$work_parent/b550i-c-7.3.5.XXXXXXXX")
cleanup() { rm -rf -- "$work"; }
trap cleanup EXIT

log="$output_dir/build.log"
exec > >(tee "$log") 2>&1
echo "B550I C candidate build log: $log"
echo "Build scratch: $work"
echo "Build host: $(hostname) / $(uname -m)"
echo "Build CPU: $(grep -m1 '^model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ *//')"
echo "CPU code-generation target: $cpu_target"
echo "Package version: $pkg_version"

compat_bin="$work/compat-bin"
mkdir -p "$compat_bin"
if $native_mode; then
  toolchain_bin=/usr/bin
  toolchain_lib=/usr/lib/x86_64-linux-gnu
else
  toolchain_bin="$toolchain_root/usr/bin"
  toolchain_lib="$toolchain_root/usr/lib/x86_64-linux-gnu"
  if [[ ! -x $toolchain_bin/fakeroot ]]; then
    [[ -x $toolchain_bin/fakeroot-sysv ]] || die 'staged fakeroot backend is missing'
    ln -s "$toolchain_bin/fakeroot-sysv" "$compat_bin/fakeroot"
  fi
  export LD_LIBRARY_PATH="$toolchain_lib:$toolchain_root/usr/lib/llvm-22/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  export CPATH="$toolchain_root/usr/include${CPATH:+:$CPATH}"
  export LIBRARY_PATH="$toolchain_lib${LIBRARY_PATH:+:$LIBRARY_PATH}"
  export HOSTCFLAGS="-I$toolchain_root/usr/include"
  export HOSTLDFLAGS="-L$toolchain_lib"
fi
export PATH="$compat_bin:$toolchain_bin:$PATH"
export KBUILD_BUILD_TIMESTAMP="2026-11-19 00:00:00 +0000"
export KBUILD_BUILD_VERSION=1
export KBUILD_BUILD_USER=psycachy-builder
export KBUILD_BUILD_HOST=b550i-candidate

for command in clang-22 ld.lld-22 llvm-ar-22 llvm-nm-22 llvm-objcopy-22 \
  llvm-objdump-22 llvm-readelf-22 llvm-strip-22 fakeroot flex bison m4 gawk bc; do
  command -v "$command" >/dev/null || die "missing staged build command: $command"
done
clang_version=$(clang-22 --version | head -n 1)
if $native_mode; then
  [[ $clang_version == "Ubuntu clang version 22.1.8 (1ubuntu1)" ]] \
    || die "unexpected native B550I compiler: $clang_version"
  lld_version=$(ld.lld-22 --version | head -n 1)
  [[ $lld_version == "Ubuntu LLD 22.1.8 (compatible with GNU linkers)" ]] \
    || die "unexpected native B550I linker: $lld_version"
  rustc_version=$(rustc --version)
  [[ $rustc_version == "rustc 1.97.1 (8bab26f4f 2026-07-14) (built from a source tarball)" ]] \
    || die "unexpected native B550I Rust compiler: $rustc_version"
  native_probe=$(clang-22 -march=native -### -E -x c /dev/null 2>&1)
  python3 - "$native_probe" "$cpu_target" <<'PY'
import shlex
import sys

targets = []
for line in sys.argv[1].splitlines():
    if "-target-cpu" not in line:
        continue
    words = shlex.split(line)
    for i, word in enumerate(words):
        if word == "-target-cpu" and i + 1 < len(words):
            targets.append(words[i + 1])
if targets != [sys.argv[2]]:
    raise SystemExit(f"native B550I compiler target mismatch: {targets!r}")
print(f"Native B550I Clang target matches {targets[0]}.")
PY
  dpkg-query -W -f='${Package} ${Version}\n' \
    clang-22 llvm-22 lld-22 fakeroot dpkg-dev flex bison m4 gawk bc pahole \
    rustc bindgen libssl-dev libelf-dev zlib1g-dev \
    >"$output_dir/toolchain-packages.txt"
  toolchain_lock_sha256=not-used-native-system-toolchain
else
  [[ $clang_version == "Debian clang version 22.1.8 (1~deb13u4)" ]] \
    || die "unexpected staged compiler: $clang_version"
  toolchain_lock_sha256=$(sha256sum "$toolchain_lock" | cut -d ' ' -f 1)
fi
clang_target_probe=$(clang-22 -march="$cpu_target" -### -E -x c /dev/null 2>&1)
python3 - "$clang_target_probe" "$cpu_target" <<'PY'
import shlex
import sys

targets = []
for line in sys.argv[1].splitlines():
    if "-target-cpu" not in line:
        continue
    words = shlex.split(line)
    for i, word in enumerate(words):
        if word == "-target-cpu" and i + 1 < len(words):
            targets.append(words[i + 1])
if targets != [sys.argv[2]]:
    raise SystemExit(f"unexpected Clang effective target: {targets!r}")
print(f"Clang target probe passed: {targets[0]}")
PY

gnupg_home="$work/gnupg"
mkdir -m 0700 "$gnupg_home"
gpg --batch --homedir "$gnupg_home" --dearmor --output "$work/signer-keyring.gpg" "$signer_key"
gpgv --keyring "$work/signer-keyring.gpg" --status-fd 1 \
  "$source_signature" "$source_archive" >"$work/signature-status" 2>"$work/signature-check.log"
grep -q "^\\[GNUPG:\\] VALIDSIG $signer_fingerprint " "$work/signature-status" \
  || die 'source signature does not match the pinned signer fingerprint'
cp "$work/signature-status" "$output_dir/source-signature-status.txt"
echo "Source signature verified for pinned fingerprint $signer_fingerprint (trust not established)."

tar -xzf "$source_archive" -C "$work"
source_dir="$work/cachyos-7.3.5-2"
[[ -f $source_dir/Makefile ]] || die 'source archive has unexpected top-level layout'
[[ $(make -s -C "$source_dir" kernelversion) == 7.3.5 ]] || die 'source version mismatch'
for patch in "$bore_patch" "$slub_patch" \
  "$root/config/patches/dkms-clang.patch" \
  "$root/config/patches/headers-config.patch" \
  "$root/config/patches/ubuntu-package-dependencies.patch"; do
  git -C "$source_dir" apply --check --no-index "$patch"
  git -C "$source_dir" apply --no-index "$patch"
done
source_tree_sha256=$(python3 "$root/tools/hash-source-tree.py" "$source_dir")
echo "Patched source-tree SHA-256: $source_tree_sha256"

build_dir="$work/kbuild"
mkdir "$build_dir"
cp "$approved_config" "$build_dir/.config"
kernel_make() {
  make -C "$source_dir" O="$build_dir" ARCH=x86_64 LLVM=-22 \
    KCFLAGS="-march=$cpu_target" KRUSTFLAGS="-Ctarget-cpu=$cpu_target" "$@"
}
KCONFIG_NOSILENTUPDATE=1 kernel_make olddefconfig
if ! python3 - "$approved_config" "$build_dir/.config" "$native_mode" \
    >"$output_dir/config-resolution.txt" <<'PY'
from pathlib import Path
import sys

def values(path):
    result = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            key, value = line[2:-11], "n"
        else:
            continue
        if key in result:
            raise SystemExit(f"duplicate Kconfig symbol: {key}")
        result[key] = value
    return result

approved, generated = values(sys.argv[1]), values(sys.argv[2])
native = sys.argv[3] == "true"
allowed = {}
if native:
    allowed = {
        "CONFIG_CC_VERSION_TEXT": (
            '"Debian clang version 22.1.8 (1~deb13u4)"',
            '"Ubuntu clang version 22.1.8 (1ubuntu1)"',
        ),
      "CONFIG_PAHOLE_VERSION": ("0", "131"),
      "CONFIG_PAHOLE_HAS_BTF_TAG": ("n", "y"),
      "CONFIG_PAHOLE_HAS_LANG_EXCLUDE": ("n", "y"),
      "CONFIG_RUST_IS_AVAILABLE": ("n", "y"),
      "CONFIG_RUSTC_VERSION": ("0", "109701"),
      "CONFIG_RUSTC_LLVM_VERSION": ("0", "220106"),
      "CONFIG_RUSTC_LLVM_MAJOR_VERSION": ("0", "22"),
      "CONFIG_RUSTC_CLANG_LLVM_COMPATIBLE": ("n", "y"),
      "CONFIG_RUSTC_HAS_SPAN_FILE": ("n", "y"),
      "CONFIG_RUSTC_HAS_UNNECESSARY_TRANSMUTES": ("n", "y"),
      "CONFIG_RUSTC_HAS_FILE_WITH_NUL": ("n", "y"),
      "CONFIG_RUSTC_HAS_FILE_AS_C_STR": ("n", "y"),
      "CONFIG_RUSTC_HAS_APXF": ("n", "y"),
    }
changed = []
unexpected = []
for key in sorted(approved.keys() | generated.keys()):
    before, after = approved.get(key, "n"), generated.get(key, "n")
    if before == after:
        continue
    if allowed.get(key) != (before, after):
        unexpected.append((key, before, after))
    else:
        changed.append((key, before, after))
if unexpected:
    details = ", ".join(f"{key}: {before!r} -> {after!r}"
                        for key, before, after in unexpected)
    raise SystemExit("resolved config has unapproved differences: " + details)
for key, before, after in changed:
    print(f"accepted native host-probe delta {key}: {before!r} -> {after!r}")
print(f"resolved_config_sha256={__import__('hashlib').sha256(Path(sys.argv[2]).read_bytes()).hexdigest()}")
PY
then
  diff -u "$approved_config" "$build_dir/.config" >"$output_dir/config-resolution.diff" || true
  die 'resolved config differs beyond the reviewed native host probes'
fi
resolved_config_sha256=$(sha256sum "$build_dir/.config" | cut -d ' ' -f 1)
if ! $native_mode; then
  [[ $resolved_config_sha256 == "$config_sha256" ]] || die 'resolved config hash mismatch'
fi
cp "$build_dir/.config" "$output_dir/resolved-config.config"
python3 "$root/tools/audit-release-policy.py" --arch amd64 \
  --output "$output_dir/policy-audit.json" "$build_dir/.config"
python3 - "$build_dir/.config" "$expected_release" <<'PY'
from pathlib import Path
import sys

values = {}
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    if line.startswith("CONFIG_") and "=" in line:
        key, value = line.split("=", 1)
        values[key] = value
    elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
        values[line[2:-11]] = "n"
required = {
    "CONFIG_LOCALVERSION": '"-psycachy-b550i-c"',
    "CONFIG_SCHED_BORE": "y",
    "CONFIG_INIT_ON_FREE_DEFAULT_ON": "y",
    "CONFIG_KSTACK_ERASE": "y",
    "CONFIG_SLAB_CANARY": "y",
    "CONFIG_SLAB_MERGE_DEFAULT": "n",
    "CONFIG_KMALLOC_PARTITION_CACHES": "y",
    "CONFIG_KMALLOC_PARTITION_TYPED": "y",
    "CONFIG_IOMMU_DEFAULT_DMA_STRICT": "y",
    "CONFIG_RUST": "n",
    "CONFIG_X86_NATIVE_CPU": "y",
    "CONFIG_GENERIC_CPU": "n",
}
failures = [f"{symbol}: expected {wanted}, got {values.get(symbol, 'n')}"
            for symbol, wanted in required.items() if values.get(symbol, "n") != wanted]
if failures:
    raise SystemExit("\n".join(failures))
print(f"Candidate config feature audit passed for {sys.argv[2]}.")
PY
kernel_release=$(KCONFIG_NOSILENTUPDATE=1 kernel_make -s kernelrelease)
[[ $kernel_release == "$expected_release" ]] || die "unexpected kernel release: $kernel_release"

echo "Checking effective Kbuild compiler target on a representative object."
if ! KCONFIG_NOSILENTUPDATE=1 kernel_make V=1 kernel/sched/fair.o \
    >"$work/znver3-object-probe.log" 2>&1; then
  tail -n 100 "$work/znver3-object-probe.log"
  die 'representative znver3 object compilation failed'
fi
python3 - "$work/znver3-object-probe.log" "$cpu_target" <<'PY'
import re
import shlex
import subprocess
import sys

path, expected = sys.argv[1:]
commands = []
for line in open(path, encoding="utf-8", errors="replace"):
    if "clang-22" in line and re.search(r"(?:^|\s)-o\s+kernel/sched/fair\.o(?:\s|$)", line):
        commands.append(shlex.split(line.strip()))
if not commands:
    raise SystemExit("could not find the fair.o compiler command in verbose Kbuild output")
argv = commands[-1]
march = []
for i, word in enumerate(argv):
    if word.startswith("-march="):
        march.append(word.split("=", 1)[1])
    elif word == "-march" and i + 1 < len(argv):
        march.append(argv[i + 1])
if not march or march[-1] != expected:
    raise SystemExit(f"Kbuild compiler flags do not end in -march={expected}: {march!r}")
probe = subprocess.run(argv + ["-###"], text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=False)
if probe.returncode:
    raise SystemExit(f"Clang command-line target probe failed: {probe.stdout[-4000:]}")
targets = []
for line in probe.stdout.splitlines():
    if "-target-cpu" not in line:
        continue
    words = shlex.split(line)
    for i, word in enumerate(words):
        if word == "-target-cpu" and i + 1 < len(words):
            targets.append(words[i + 1])
if targets != [expected]:
    raise SystemExit(f"effective Kbuild compiler CPU is not {expected}: {targets!r}")
print(f"Representative Kbuild command and Clang backend both target {expected}.")
PY
cp "$work/znver3-object-probe.log" "$output_dir/znver3-object-probe.log"

echo "Building kernel image, modules, and Debian packages with $jobs workers."
DEB_BUILD_PROFILES=pkg.linux-psycachy-b550i.nokerneldbg \
DEBFULLNAME="PsyCachy Builder" DEBEMAIL="builder@example.invalid" \
KCONFIG_NOSILENTUPDATE=1 KBUILD_DEBARCH=amd64 KDEB_SOURCENAME=linux-psycachy-b550i \
  kernel_make -j"$jobs" bindeb-pkg KDEB_PKGVERSION="$pkg_version"

image_packages=("$work"/linux-image-"$kernel_release"_*.deb)
header_packages=("$work"/linux-headers-"$kernel_release"_*.deb)
(( ${#image_packages[@]} == 1 && ${#header_packages[@]} == 1 )) \
  || die 'expected exactly one image and one headers package'
image=${image_packages[0]}
headers=${header_packages[0]}
for package in "$image" "$headers"; do
  dpkg-deb --info "$package" >/dev/null
  [[ $(dpkg-deb -f "$package" Architecture) == amd64 ]] || die "wrong package architecture: $package"
  [[ $(dpkg-deb -f "$package" Version) == "$pkg_version" ]] || die "wrong package version: $package"
done
[[ $(dpkg-deb -f "$image" Package) == "linux-image-$kernel_release" ]] || die 'image package name mismatch'
[[ $(dpkg-deb -f "$headers" Package) == "linux-headers-$kernel_release" ]] || die 'headers package name mismatch'
image_depends=$(dpkg-deb -f "$image" Depends)
headers_depends=$(dpkg-deb -f "$headers" Depends)
python3 "$root/tools/deb_dependencies.py" amd64 "$image_depends" kmod linux-base \
  "linux-headers-$kernel_release" || die 'image package dependency audit failed'
header_requirement="linux-headers-$kernel_release (= $pkg_version)"
image_depends_clauses=$(printf '%s' "$image_depends" | tr '\n' ' ' | sed 's/, */\n/g')
grep -Fxq -- "$header_requirement" <<<"$image_depends_clauses" \
  || die 'image package does not require the matching headers version'
python3 "$root/tools/deb_dependencies.py" amd64 "$headers_depends" \
  build-essential clang-22 llvm-22 lld-22 pahole libelf1t64 libssl4 \
  || die 'headers package dependency audit failed'

header_stage="$work/header-stage"
image_stage="$work/image-stage"
mkdir "$header_stage" "$image_stage"
dpkg-deb --extract "$headers" "$header_stage"
dpkg-deb --extract "$image" "$image_stage"
header_dir="$header_stage/usr/src/linux-headers-$kernel_release"
for file in .config Module.symvers include/config/auto.conf include/generated/autoconf.h \
  scripts/sign-file scripts/mod/modpost; do
  [[ -s $header_dir/$file ]] || die "headers package missing $file"
done
cmp -s "$build_dir/.config" "$header_dir/.config" || die 'packaged headers config differs from resolved candidate config'
[[ -L $header_stage/lib/modules/$kernel_release/build ]] \
  || die 'headers package is missing its module build link'
[[ -s $image_stage/boot/vmlinuz-$kernel_release ]] || die 'image package is missing its kernel payload'
[[ -d $image_stage/lib/modules/$kernel_release/kernel ]] || die 'image package is missing its module tree'

certificate="$build_dir/certs/signing_key.x509"
[[ -s $certificate ]] || die 'generated module-signing certificate is missing'
cp "$certificate" "$output_dir/module-signing-cert.x509"
certificate_sha256=$(sha256sum "$certificate" | cut -d ' ' -f 1)
kernel_payload_sha256=$(sha256sum "$image_stage/boot/vmlinuz-$kernel_release" | cut -d ' ' -f 1)
image_sha256=$(sha256sum "$image" | cut -d ' ' -f 1)
headers_sha256=$(sha256sum "$headers" | cut -d ' ' -f 1)
cp "$image" "$headers" "$output_dir/"
(cd "$output_dir" && sha256sum ./*.deb module-signing-cert.x509 > SHA256SUMS)

{
  echo "candidate=C"
  echo "release_status=pre-stable; not shippable"
  echo "kernel_release=$kernel_release"
  echo "package_version=$pkg_version"
  echo "architecture=amd64"
  echo "cpu_target=$cpu_target"
  echo "c_codegen_flags=-march=$cpu_target (passed through KCFLAGS after -march=native)"
  echo "rust_codegen_flags=-Ctarget-cpu=$cpu_target (passed through KRUSTFLAGS)"
  echo "source_archive_sha256=$source_sha256"
  echo "source_signer_fingerprint=$signer_fingerprint"
  echo "source_signer_trust=not-established"
  echo "source_tree_sha256=$source_tree_sha256"
  echo "input_manifest_sha256=$input_manifest_sha256"
  echo "build_context_lock_sha256=$build_context_lock_sha256"
  echo "config_sha256=$resolved_config_sha256"
  echo "bore_patch_sha256=$bore_sha256"
  echo "slub_canary_patch_sha256=$slub_sha256"
  echo "dkms_clang_patch_sha256=$dkms_patch_sha256"
  echo "headers_config_patch_sha256=$headers_patch_sha256"
  echo "ubuntu_package_dependencies_patch_sha256=$dependencies_patch_sha256"
  echo "clang_version=$clang_version"
  echo "toolchain_package_lock_sha256=$toolchain_lock_sha256"
  if [[ -s $output_dir/toolchain-packages.txt ]]; then
    echo "toolchain_packages_sha256=$(sha256sum "$output_dir/toolchain-packages.txt" | cut -d ' ' -f 1)"
  fi
  echo "build_host=$(hostname) $(uname -m)"
  grep -m1 '^model name' /proc/cpuinfo || true
  echo "module_signing_certificate_sha256=$certificate_sha256"
  echo "module_signing_key_lifetime=ephemeral; private build key not retained"
  echo "kernel_payload_sha256=$kernel_payload_sha256"
  echo "image_package=$(basename "$image")"
  echo "image_package_sha256=$image_sha256"
  echo "headers_package=$(basename "$headers")"
  echo "headers_package_sha256=$headers_sha256"
} > "$output_dir/build-metadata.txt"

echo "Candidate package pair and audits written to $output_dir"
