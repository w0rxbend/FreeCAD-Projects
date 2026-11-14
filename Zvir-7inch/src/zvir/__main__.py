"""zvir check | export | render | all | analyse  (the Zhalo engine, building this design)."""

from pathlib import Path

from zhalo.__main__ import main as engine_main

import zvir  # noqa: F401, I001 - configures the engine; must come before any other engine import

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    engine_main(root=ROOT, prog="zvir")


if __name__ == "__main__":
    main()
