#!/usr/bin/env python3

import os
import sys
from pathlib import Path


class Color:
    GREEN = '\033[92m'
    RESET = '\033[0m'


def uninstall_hooks():
    """Remove installed git hooks"""
    script_dir = Path(__file__).parent.absolute()
    pre_commit = script_dir / '.git' / 'hooks' / 'pre-commit'

    try:
        if pre_commit.exists():
            pre_commit.unlink()
        print(f"{Color.GREEN}✓ Successfully uninstalled git hooks{Color.RESET}")
        return True
    except Exception as e:
        print(f"Error uninstalling hooks: {str(e)}")
        return False


if __name__ == "__main__":
    success = uninstall_hooks()
    sys.exit(0 if success else 1)
