#!/usr/bin/env python3

import os
import sys
import shutil
from pathlib import Path


class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'


def install_hooks():
    """Install git hooks from .hooks directory"""
    script_dir = Path(__file__).parent.absolute()
    hooks_dir = script_dir / '.hooks'
    git_hooks_dir = script_dir / '.git' / 'hooks'

    # Create .git/hooks directory if it doesn't exist
    git_hooks_dir.mkdir(parents=True, exist_ok=True)

    # Install pre-commit hook
    source = hooks_dir / 'pre-commit'
    target = git_hooks_dir / 'pre-commit'

    try:
        # Copy hook file
        shutil.copy2(source, target)
        # Make executable
        target.chmod(0o755)
        print(f"{Color.GREEN}✓ Successfully installed pre-commit hook{Color.RESET}")
        return True
    except Exception as e:
        print(f"{Color.RED}Error installing hooks: {str(e)}{Color.RESET}")
        return False


if __name__ == "__main__":
    success = install_hooks()
    sys.exit(0 if success else 1)
