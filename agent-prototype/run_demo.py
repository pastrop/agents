#!/usr/bin/env python3
"""Quick demo runner script."""

import subprocess
import sys

if __name__ == "__main__":
    try:
        subprocess.run([sys.executable, "main.py", "--demo"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Demo failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        sys.exit(0)