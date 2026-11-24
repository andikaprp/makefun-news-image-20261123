#!/usr/bin/env python3
"""Copier: entry.png -> $MAKEFUN_OUTPUT_DIR/entry.png (stdlib only)."""
import os
import shutil
import sys

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
