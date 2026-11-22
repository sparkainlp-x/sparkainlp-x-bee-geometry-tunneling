# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
.PHONY: test run clean

test:
	PYTHONPATH=. python3 -m pytest tests/ -q

run:
	PYTHONPATH=. python3 -m bee_geometry_tunneling

clean:
	rm -rf bee_geometry_tunneling/__pycache__ tests/__pycache__ .pytest_cache
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
