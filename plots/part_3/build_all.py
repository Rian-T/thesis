from __future__ import annotations

import argparse
from importlib import import_module
import os
from pathlib import Path
import sys
from typing import Sequence

from plots.part_3.common import DEFAULT_OUTPUT, ProvisionalDataError

CHAPTER_MODULES = (
    "plots.part_3.plot_chapter9",
    "plots.part_3.plot_chapter8",
    "plots.part_3.plot_chapter7",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build all Part 3 plots.")
    parser.add_argument(
        "--allow-provisional",
        action="store_true",
        help="allow provisional observations in review renders",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="directory for generated PDF and PNG files",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_dir = args.output_dir.resolve()

    try:
        outputs = []
        for module_name in CHAPTER_MODULES:
            module = import_module(module_name)
            outputs.extend(module.build(output_dir, args.allow_provisional))
    except ProvisionalDataError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    for output in outputs:
        print(os.path.relpath(Path(output).resolve(), start=Path.cwd()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
