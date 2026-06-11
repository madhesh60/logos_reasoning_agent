#!/usr/bin/env python3
"""
run_agent.py — local development shortcut
Delegates to logos.cli which is the true entry point.

For production use:  pip install logos-research && logos
"""
from logos.cli import main

if __name__ == "__main__":
    main()
