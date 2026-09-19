#!/usr/bin/env python3
"""Usage: uv run python tools/export_freecad.py frame.step frame.FCStd."""

import argparse
from pathlib import Path

from fpv_frame.export.freecad import convert_step


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert STEP to FCStd and verify reopening")
    parser.add_argument("step", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(convert_step(args.step, args.output))


if __name__ == "__main__":
    main()
