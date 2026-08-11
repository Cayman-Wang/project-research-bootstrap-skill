#!/usr/bin/env python3
"""Deprecated compatibility entrypoint for the v2 initializer."""

import sys
from init_research_workspace import main

if __name__ == "__main__":
    print("warning: bootstrap_research_workspace.py is deprecated; use init_research_workspace.py", file=sys.stderr)
    raise SystemExit(main())
