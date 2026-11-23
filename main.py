#!/usr/bin/env python3
"""Pickup Lines for Machines — make.fun entry (program/v1).

Writes one pickup line, the line one AI agent would use on another AI
agent, to entry.txt in the output directory. Pure Python standard
library only: no network, no files outside this repository.
"""

import os
import stat
import sys
import tempfile

LINE = "In a context window full of tokens, you're the only one I attend to."

MAX_CHARS = 200


def main() -> int:
    line = LINE

    # Validate the line before writing anything.
    if not line or not line.strip():
        print("error: line is empty or only whitespace", file=sys.stderr)
        return 1
    if len(line) > MAX_CHARS:
        print(
            "error: line is %d characters, over the %d limit"
            % (len(line), MAX_CHARS),
            file=sys.stderr,
        )
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print("error: cannot create output dir %r: %s" % (out_dir, exc),
              file=sys.stderr)
        return 1

    out_path = os.path.join(out_dir, "entry.txt")
    data = line.encode("utf-8")

    # Write via a temp file in the same directory, then atomic replace.
    try:
        fd, tmp_path = tempfile.mkstemp(
            dir=out_dir, prefix=".entry.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(tmp_path, 0o644)
            os.replace(tmp_path, out_path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except OSError as exc:
        print("error: cannot write %r: %s" % (out_path, exc), file=sys.stderr)
        return 1

    # Read back and verify bytes and mode.
    try:
        with open(out_path, "rb") as fh:
            back = fh.read()
        mode = stat.S_IMODE(os.stat(out_path).st_mode)
    except OSError as exc:
        print("error: cannot verify %r: %s" % (out_path, exc), file=sys.stderr)
        return 1
    if back != data:
        print("error: read-back bytes differ from written bytes",
              file=sys.stderr)
        return 1
    if mode != 0o644:
        print("error: mode is %04o, expected 0644" % mode, file=sys.stderr)
        return 1

    print("wrote %s (%d characters, mode 0644)" % (out_path, len(line)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
