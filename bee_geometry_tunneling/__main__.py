# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""Run the laboratory and print the measured claims table.

    python -m bee_geometry_tunneling
"""

from __future__ import annotations

import sys

from .lab import evaluate_all, report


def main(argv: list[str] | None = None) -> int:
    results = evaluate_all()
    print(report(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
