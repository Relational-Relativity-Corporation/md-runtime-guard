"""
md-guard CLI
------------
Commands:
  md-guard run <file.py>    Execute file via run_file(), report violations
  md-guard check <file.py>  Execute file, exit 0 (clean), 1 (violations), 2 (enforced)
"""

import sys
import os

from bounded_domain import run_file, DomainConfig, reset_violation_count
import bounded_domain as _bd


def cmd_run(filepath):
    """
    Execute file via run_file().
    Violations printed per DomainConfig.MODE.
    Exit 0 always (run is informational).
    """
    if not os.path.isfile(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(2)

    reset_violation_count()

    try:
        run_file(filepath)
    except RuntimeError as e:
        # enforce mode raised — already printed by report_violation
        sys.exit(2)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(2)

    sys.exit(0)


def cmd_check(filepath):
    """
    Execute file in warn mode regardless of configured MODE.
    Exit codes:
      0 — no violations
      1 — violations detected
      2 — enforcement exception raised
    """
    if not os.path.isfile(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(2)

    original_mode = DomainConfig.MODE
    DomainConfig.MODE = "warn"
    reset_violation_count()

    try:
        run_file(filepath)
    except RuntimeError as e:
        DomainConfig.MODE = original_mode
        sys.exit(2)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        DomainConfig.MODE = original_mode
        sys.exit(2)
    finally:
        DomainConfig.MODE = original_mode

    if _bd.VIOLATION_COUNT > 0:
        sys.exit(1)

    sys.exit(0)


def main():
    if len(sys.argv) < 3:
        print("Usage: md-guard <run|check> <file.py>")
        sys.exit(2)

    command  = sys.argv[1]
    filepath = sys.argv[2]

    if command == "run":
        cmd_run(filepath)
    elif command == "check":
        cmd_check(filepath)
    else:
        print(f"[ERROR] Unknown command: {command}")
        print("Usage: md-guard <run|check> <file.py>")
        sys.exit(2)


if __name__ == "__main__":
    main()