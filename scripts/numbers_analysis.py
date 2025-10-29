"""Utilities for extracting and analysing numbers hidden inside a text.

The source tasks this module targets describe a single long string containing
printable ASCII characters (codes 33-126).  Groups of consecutive digits that
are not immediately preceded or followed by another digit encode the numbers of
interest.  Example::

    "356xv@@4vdfvdfD#$%@@#245" -> ["356", "4", "245"]

The module exposes helper functions to extract the numbers as *tokens* (keeping
both the textual representation and the integer value) and several analysis
helpers that cover the most common questions appearing in contest tasks:

* How many numbers are hidden in the text?
* What is the sum / maximum of all numbers?
* Which number is the longest (i.e. contains the most digits)?

The :func:`main` entry-point offers a small command line utility that reads an
input file, runs a configurable subset of the analyses above and writes the
answers to individual text files inside an output directory.  The default set of
analyses mirrors the questions listed earlier, but users can request any subset
using the ``--tasks`` option.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List

_NUMBER_PATTERN = re.compile(r"(?<!\d)(\d+)(?!\d)")


@dataclass(frozen=True)
class NumberToken:
    """Representation of a single number extracted from the text.

    Attributes
    ----------
    text:
        The original text fragment consisting of digits only.  Keeping the raw
        text ensures we do not lose potential leading zeros when reporting the
        longest number.
    value:
        Integer value of the token.  It is derived lazily to keep the dataclass
        simple while providing the convenience of attribute-style access.
    """

    text: str

    @property
    def value(self) -> int:
        return int(self.text)

    @property
    def length(self) -> int:
        return len(self.text)


def extract_number_tokens(text: str) -> List[NumberToken]:
    """Extract digit-only tokens representing the hidden numbers.

    Parameters
    ----------
    text:
        Input string that potentially contains hidden numbers.

    Returns
    -------
    list[NumberToken]
        Number tokens in the order they appear in *text*.
    """

    return [NumberToken(match.group(0)) for match in _NUMBER_PATTERN.finditer(text)]


def count_tokens(tokens: Iterable[NumberToken]) -> str:
    """Return the number of detected tokens as a string."""

    token_list = list(tokens)
    return str(len(token_list))


def sum_tokens(tokens: Iterable[NumberToken]) -> str:
    """Return the sum of all token values as a string."""

    total = sum(token.value for token in tokens)
    return str(total)


def max_token(tokens: Iterable[NumberToken]) -> str:
    """Return the maximum token value as a string.

    The function gracefully handles the case when *tokens* is empty by returning
    the marker ``"BRAK"`` (Polish for "missing"), which is a common convention
    in the source contest tasks when the answer does not exist.
    """

    token_list = list(tokens)
    if not token_list:
        return "BRAK"
    return str(max(token.value for token in token_list))


def longest_token(tokens: Iterable[NumberToken]) -> str:
    """Return the textual representation and length of the longest token.

    The result is formatted as ``"<number> <length>"``.  When multiple numbers
    share the maximal length, the first occurrence is reported.  If *tokens* is
    empty the same ``"BRAK"`` marker as :func:`max_token` is returned.
    """

    token_list = list(tokens)
    if not token_list:
        return "BRAK"

    longest = token_list[0]
    for candidate in token_list[1:]:
        if candidate.length > longest.length:
            longest = candidate
    return f"{longest.text} {longest.length}"


TaskFunction = Callable[[Iterable[NumberToken]], str]


TASKS: Dict[str, TaskFunction] = {
    "count": count_tokens,
    "sum": sum_tokens,
    "max": max_token,
    "longest": longest_token,
}


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract numbers hidden inside a text and compute selected statistics "
            "for contest tasks."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the input text file (e.g. dane.txt).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory in which answer files will be created.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding used to read input and write outputs (default: utf-8).",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=sorted(TASKS),
        default=["count", "sum", "max", "longest"],
        help=(
            "Subset of analyses to perform.  Each task writes a <name>.txt file "
            "inside the output directory."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:
    args = _parse_args(argv)

    if not args.input.is_file():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    text = args.input.read_text(encoding=args.encoding)
    tokens = extract_number_tokens(text)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for task_name in args.tasks:
        task = TASKS[task_name]
        # Re-use the same token sequence for each task.
        result = task(tokens)
        output_path = output_dir / f"{task_name}.txt"
        output_path.write_text(result + "\n", encoding=args.encoding)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
