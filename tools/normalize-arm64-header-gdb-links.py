#!/usr/bin/env python3
"""Make packaged ARM64 kernel GDB helper files relocatable."""

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import sys
import tempfile


def _package_regular_files(stage: pathlib.Path):
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(stage)
        if relative.parts[0] != "DEBIAN":
            yield path, relative


def _write_md5sums(stage: pathlib.Path) -> int:
    records = []
    for path, relative in _package_regular_files(stage):
        name = relative.as_posix()
        if "\n" in name or "\r" in name:
            raise ValueError(f"unsupported newline in package path: {name!r}")
        digest = hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()
        records.append(f"{digest}  {name}\n")

    control_dir = stage / "DEBIAN"
    if control_dir.is_symlink() or not control_dir.is_dir():
        raise ValueError("package stage lacks a regular DEBIAN directory")
    md5sums = control_dir / "md5sums"
    if md5sums.is_symlink():
        raise ValueError("DEBIAN/md5sums must not be a symlink")
    fd, temporary = tempfile.mkstemp(prefix=".md5sums.", dir=control_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
            output.writelines(records)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, md5sums)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return len(records)


def normalize_header_gdb_links(
    stage: pathlib.Path,
    source_root: pathlib.Path,
    release: str,
    source_date_epoch: int,
    expected_links: int | None = None,
) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9._+~-]+", release):
        raise ValueError("invalid kernel release")
    if not isinstance(source_date_epoch, int) or source_date_epoch < 0:
        raise ValueError("SOURCE_DATE_EPOCH must be a non-negative integer")
    if expected_links is not None and expected_links < 0:
        raise ValueError("expected link count must not be negative")
    if stage.is_symlink():
        raise ValueError("package stage must not be a symlink")
    stage = stage.resolve(strict=True)
    if not stage.is_dir():
        raise ValueError("package stage must be a regular directory")
    source_root = source_root.resolve(strict=True)
    if not source_root.is_dir():
        raise ValueError("kernel source root must be a directory")

    header_root = stage / "usr/src" / f"linux-headers-{release}"
    current = stage
    for component in pathlib.PurePosixPath(f"usr/src/linux-headers-{release}").parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("symlink in headers package path")
    if not header_root.is_dir():
        raise ValueError("headers package tree is missing")
    helper_root = header_root / "scripts/gdb/linux"
    source_helpers = source_root / "scripts/gdb/linux"
    current = header_root
    for component in pathlib.PurePosixPath("scripts/gdb/linux").parts:
        current = current / component
        if current.is_symlink():
            raise ValueError("symlink in headers package GDB helper path")
    if not helper_root.is_dir():
        raise ValueError("headers package GDB helper directory is missing or unsafe")
    if source_helpers.is_symlink() or not source_helpers.is_dir():
        raise ValueError("kernel source GDB helper directory is missing or unsafe")
    source_helpers = source_helpers.resolve(strict=True)
    if not source_helpers.is_relative_to(source_root):
        raise ValueError("kernel source GDB helpers resolve outside the pinned source tree")

    symlinks = []

    def inspect(directory: pathlib.Path):
        for path in sorted(directory.iterdir()):
            if path.is_symlink():
                raw_target = pathlib.Path(os.readlink(path))
                target = raw_target if raw_target.is_absolute() else path.parent / raw_target
                target = target.resolve(strict=True)
                if not target.is_file() or not target.is_relative_to(source_helpers):
                    raise ValueError(
                        f"GDB helper symlink escapes the pinned source tree: "
                        f"{path.relative_to(stage).as_posix()}"
                    )
                symlinks.append((path, target))
            elif path.is_dir():
                inspect(path)
            elif not path.is_file():
                raise ValueError(f"unsupported GDB helper entry: {path.relative_to(stage)}")

    inspect(helper_root)
    if expected_links is not None and len(symlinks) != expected_links:
        raise ValueError(
            f"expected {expected_links} GDB helper symlinks, found {len(symlinks)}"
        )

    report_links = []
    for path, target in symlinks:
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        os.close(fd)
        try:
            shutil.copyfile(target, temporary)
            source_mode = stat.S_IMODE(target.stat().st_mode)
            os.chmod(temporary, source_mode)
            os.utime(temporary, (source_date_epoch, source_date_epoch))
            os.replace(temporary, path)
        except BaseException:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise
        report_links.append({
            "path": path.relative_to(stage).as_posix(),
            "source_relative_path": target.relative_to(source_helpers).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
            "mode": stat.S_IMODE(path.stat().st_mode),
        })

    remaining = []
    def check(directory: pathlib.Path):
        for path in sorted(directory.iterdir()):
            if path.is_symlink():
                remaining.append(path.relative_to(stage).as_posix())
            elif path.is_dir():
                check(path)

    check(helper_root)
    if remaining:
        raise ValueError("GDB helper symlinks remain after normalization")

    md5_count = _write_md5sums(stage)
    return {
        "schema": 1,
        "status": "normalized-relocatable-gdb-helpers",
        "kernel_release": release,
        "source_date_epoch": source_date_epoch,
        "dereferenced_symlink_count": len(report_links),
        "remaining_symlink_count": 0,
        "md5sums_regular_file_count": md5_count,
        "files": report_links,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=pathlib.Path, required=True,
                        help="dpkg-deb -R package staging directory")
    parser.add_argument("--source-root", type=pathlib.Path, required=True,
                        help="exact extracted kernel source tree")
    parser.add_argument("--release", required=True)
    parser.add_argument("--source-date-epoch", type=int, required=True)
    parser.add_argument("--expected-links", type=int,
                        help="fail unless exactly this many source links are normalized")
    parser.add_argument("--output-report", type=pathlib.Path, required=True)
    args = parser.parse_args()

    report = normalize_header_gdb_links(
        args.stage, args.source_root, args.release, args.source_date_epoch,
        args.expected_links,
    )
    fd = os.open(args.output_report, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    print(
        f"Normalized {report['dereferenced_symlink_count']} ARM64 headers GDB helpers; "
        f"report: {args.output_report}"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
