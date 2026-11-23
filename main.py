"""make.fun entry copier: copies the pre-rendered entry.png to the output dir.
Standard library only. Deterministic: the shipped bytes are copied verbatim.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"), os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
