"""shershen check | export | render | all  (the Zhalo engine, building this design)."""

from pathlib import Path

from zhalo.__main__ import main as engine_main

import shershen  # noqa: F401 - registers the design

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    engine_main(root=ROOT, prog="shershen")


if __name__ == "__main__":
    main()
