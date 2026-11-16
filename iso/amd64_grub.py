#!/usr/bin/env python3
"""Build a fail-closed Try/Rescue and guarded-install GRUB menu."""
from __future__ import annotations

import re
import os
import stat
import sys
import tempfile
from pathlib import Path


class GrubMenuError(ValueError):
    """The pinned Ubuntu GRUB menu is missing or has an unsafe layout."""


ENTRY_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)menuentry[ \t]+(?P<quote>['\"])(?P<title>.*?)(?P=quote)[ \t]*\{"
)
KERNEL_RE = re.compile(r"^[ \t]*(?:linux|linuxefi)[ \t]+")
INITRD_RE = re.compile(r"^[ \t]*initrd(?:efi)?[ \t]+")
AUTOINSTALL_PATH = "subiquity.autoinstallpath=/cdrom/psycachy/autoinstall.yaml"
TRY_TITLE = "Try PsyCachy (live/rescue)"
SAFE_TITLE = "Try PsyCachy (safe graphics)"
INSTALL_TITLE = "Install PsyCachy (guarded)"


def _block_end(text: str, opening: int) -> int:
    """Return the exclusive end of a GRUB block, respecting quotes/comments."""
    depth = 0
    quote = None
    escaped = False
    comment = False
    for index in range(opening, len(text)):
        char = text[index]
        if comment:
            if char in "\r\n":
                comment = False
            continue
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char == "#":
            comment = True
        elif char in "'\"":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
            if depth < 0:
                break
    raise GrubMenuError("pinned GRUB menu contains an unbalanced menuentry block")


def _entries(text: str) -> list[tuple[str, int, int, str]]:
    result = []
    for match in ENTRY_RE.finditer(text):
        end = _block_end(text, match.end() - 1)
        result.append((match.group("title"), match.start(), end, text[match.start():end]))
    return result


def _only_entry(entries: list[tuple[str, int, int, str]], title: str) -> tuple[str, int, int, str]:
    matches = [entry for entry in entries if entry[0] == title]
    if len(matches) != 1:
        raise GrubMenuError(f"expected exactly one {title!r} menuentry")
    return matches[0]


def _commands(block: str, matcher: re.Pattern[str]) -> list[tuple[int, str]]:
    lines = block.splitlines(keepends=True)
    return [(index, line) for index, line in enumerate(lines) if matcher.match(line)]


def _rename_entry(block: str, title: str) -> str:
    match = ENTRY_RE.search(block)
    if match is None:
        raise GrubMenuError("cannot rename a malformed GRUB menuentry")
    return block[:match.start("title")] + title + block[match.end("title"):]


def _install_kernel_line(line: str) -> str:
    newline = ""
    if line.endswith("\r\n"):
        newline, line = "\r\n", line[:-2]
    elif line.endswith("\n"):
        newline, line = "\n", line[:-1]

    match = re.match(r"^(?P<indent>[ \t]*)(?P<command>linux(?:efi)?)(?P<gap>[ \t]+)(?P<args>.*)$", line)
    if match is None:
        raise GrubMenuError("pinned Try entry has a malformed kernel command")
    args = match.group("args")
    if args.count("---") != 1:
        raise GrubMenuError("pinned GRUB kernel command must contain exactly one --- separator")
    before, after = args.split("---", 1)
    tokens = before.split()
    if "autoinstall" in tokens or any(token.startswith("subiquity.autoinstallpath=") for token in tokens):
        raise GrubMenuError("pinned Try entry already contains an autoinstall directive")
    updated = (
        match.group("indent") + match.group("command") + match.group("gap")
        + before.rstrip() + " autoinstall " + AUTOINSTALL_PATH + " ---" + after + newline
    )
    return updated


def _kernel_lines(block: str) -> list[str]:
    return [line.rstrip("\r\n") for _, line in _commands(block, KERNEL_RE)]


def _has_autoinstall(line: str) -> bool:
    tokens = line.split()
    return "autoinstall" in tokens or any(token.startswith("subiquity.autoinstallpath=") for token in tokens)


def build_menu(text: str) -> str:
    """Return the guarded menu, refusing layouts outside the signed-base pin."""
    if re.search(r"(?m)^[ \t]*set[ \t]+default[ \t]*=", text):
        raise GrubMenuError("pinned GRUB config already defines a default entry")
    timeout_matches = list(re.finditer(r"(?m)^[ \t]*set[ \t]+timeout[ \t]*=[^\r\n]*(?:\r?\n|$)", text))
    if len(timeout_matches) != 1:
        raise GrubMenuError("pinned GRUB config must define exactly one timeout")

    entries = _entries(text)
    try_entry = _only_entry(entries, "Try or Install Ubuntu")
    safe_entry = _only_entry(entries, "Ubuntu (safe graphics)")
    for title, _, _, block in entries:
        kernels = _commands(block, KERNEL_RE)
        if title not in {"Try or Install Ubuntu", "Ubuntu (safe graphics)"} and any(
            _has_autoinstall(line) for _, line in kernels
        ):
            raise GrubMenuError(f"unexpected autoinstall directive in menuentry {title!r}")
    try_kernels = _commands(try_entry[3], KERNEL_RE)
    safe_kernels = _commands(safe_entry[3], KERNEL_RE)
    if len(try_kernels) != 1 or len(_commands(try_entry[3], INITRD_RE)) != 1:
        raise GrubMenuError("pinned Try entry must contain exactly one kernel and initrd command")
    if len(safe_kernels) != 1 or len(_commands(safe_entry[3], INITRD_RE)) != 1:
        raise GrubMenuError("pinned safe-graphics entry must contain exactly one kernel and initrd command")
    if _has_autoinstall(try_kernels[0][1]) or _has_autoinstall(safe_kernels[0][1]):
        raise GrubMenuError("pinned Try paths must not already load autoinstall")
    if any("---" in line for line in text.splitlines() if not KERNEL_RE.match(line)):
        raise GrubMenuError("pinned GRUB config contains --- outside a kernel command")

    try_lines = try_entry[3].splitlines(keepends=True)
    try_kernel_index = try_kernels[0][0]
    install_lines = list(try_lines)
    install_lines[try_kernel_index] = _install_kernel_line(install_lines[try_kernel_index])
    try_block = _rename_entry(try_entry[3], TRY_TITLE)
    install_block = _rename_entry("".join(install_lines), INSTALL_TITLE)
    safe_block = _rename_entry(safe_entry[3], SAFE_TITLE)

    updated = text
    edits = [
        (try_entry[1], try_entry[2], try_block + ("\r\n" if "\r\n" in text else "\n") + install_block),
        (safe_entry[1], safe_entry[2], safe_block),
    ]
    for start, end, replacement in sorted(edits, reverse=True):
        updated = updated[:start] + replacement + updated[end:]

    timeout = re.search(r"(?m)^[ \t]*set[ \t]+timeout[ \t]*=[^\r\n]*(?P<newline>\r?\n|$)", updated)
    if timeout is None:
        raise GrubMenuError("could not place the default after the timeout")
    line_ending = timeout.group("newline") or "\n"
    updated = updated[:timeout.end()] + "set default=0" + line_ending + updated[timeout.end():]

    final_entries = _entries(updated)
    live = _only_entry(final_entries, TRY_TITLE)
    install = _only_entry(final_entries, INSTALL_TITLE)
    safe = _only_entry(final_entries, SAFE_TITLE)
    if final_entries[0][0] != TRY_TITLE:
        raise GrubMenuError("Try/Rescue must remain the first and default menuentry")
    install_kernels = _commands(install[3], KERNEL_RE)
    if len(install_kernels) != 1:
        raise GrubMenuError("guarded install entry must contain exactly one kernel command")
    tokens = install_kernels[0][1].split()
    if tokens.count("autoinstall") != 1 or tokens.count(AUTOINSTALL_PATH) != 1:
        raise GrubMenuError("guarded install entry lacks its unique autoinstall config path")
    for entry in (live, safe):
        if any(_has_autoinstall(line) for line in _kernel_lines(entry[3])):
            raise GrubMenuError(f"{entry[0]!r} must not load autoinstall")
    if sum(_has_autoinstall(line) for _, _, _, block in final_entries for line in _kernel_lines(block)) != 1:
        raise GrubMenuError("only the guarded install entry may load autoinstall")
    if len(re.findall(r"(?m)^[ \t]*set[ \t]+default[ \t]*=0[ \t]*$", updated)) != 1:
        raise GrubMenuError("GRUB default must be explicitly set to Try/Rescue entry 0")
    return updated


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {Path(sys.argv[0]).name} GRUB_CONFIG")
    path = Path(sys.argv[1])
    try:
        updated = build_menu(path.read_text(encoding="utf-8"))
        mode = stat.S_IMODE(path.stat().st_mode)
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                output.write(updated)
                output.flush()
                os.fsync(output.fileno())
            os.chmod(temporary, mode)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    except (OSError, GrubMenuError) as error:
        raise SystemExit(f"PsyCachy GRUB menu: {error}") from error
    print("Built Try/Rescue default and guarded-install GRUB entries.")


if __name__ == "__main__":
    main()
