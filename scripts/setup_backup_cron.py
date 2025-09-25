#!/usr/bin/env python3
"""Install a daily cron job that runs the Infinite Go backup script."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PYTHON = sys.executable or "/usr/bin/python3"
BACKUP_SCRIPT = PROJECT_ROOT / "scripts" / "backup_db.py"
DEFAULT_MINUTE = 30
DEFAULT_HOUR = 2
DEFAULT_LOG = PROJECT_ROOT / "data" / "backups" / "backup.log"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Configure crontab to run the Infinite Go database backup script daily."
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=DEFAULT_MINUTE,
        help=f"Minute of the hour for the cron job (default: {DEFAULT_MINUTE}).",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=DEFAULT_HOUR,
        help=f"Hour of the day (24h) for the cron job (default: {DEFAULT_HOUR}).",
    )
    parser.add_argument(
        "--python",
        type=Path,
        default=Path(DEFAULT_PYTHON),
        help="Path to the Python interpreter used to run the backup script.",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="",
        help="Optional label passed through to backup_db.py for backup filenames.",
    )
    parser.add_argument(
        "--retention",
        type=int,
        default=30,
        help="Number of backups to retain when the job runs (0 disables pruning).",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG,
        help=f"File to append cron output to (default: {DEFAULT_LOG}).",
    )
    return parser.parse_args()


def read_existing_crontab() -> str:
    """Return the user's current crontab as a string (may be empty)."""

    try:
        result = subprocess.run(
            ["crontab", "-l"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("crontab command not available on this system.") from exc

    if result.returncode != 0:
        # `crontab -l` returns exit code 1 and prints "no crontab" when empty.
        return ""
    return result.stdout


def write_crontab(cron_contents: str) -> None:
    """Write the provided cron contents to the user's crontab."""

    subprocess.run(["crontab", "-"], check=True, input=cron_contents, text=True)


def ensure_entry(existing: str, new_entry: str) -> str:
    """Return a cron string with the new entry appended if not already present."""

    lines = [line.rstrip() for line in existing.splitlines() if line.strip()]
    if new_entry.strip() in lines:
        return "\n".join(lines) + "\n"
    lines.append(new_entry.strip())
    return "\n".join(lines) + "\n"


def build_cron_entry(args: argparse.Namespace) -> str:
    """Generate the cron line for the backup job."""

    python_path = Path(args.python).resolve()
    backup_script = BACKUP_SCRIPT.resolve()
    log_path = Path(args.log_file).resolve()

    if not backup_script.exists():
        raise FileNotFoundError(f"Backup script not found at {backup_script}.")

    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Compose the command ensuring proper shell escaping for label parameter.
    cmd_parts = [
        shlex.quote(str(python_path)),
        shlex.quote(str(backup_script)),
        f"--retention {args.retention}",
    ]
    if args.label:
        cmd_parts.append(f"--label {shlex.quote(args.label)}")
    command = " ".join(cmd_parts) + f" >> {shlex.quote(str(log_path))} 2>&1"

    return f"{args.minute} {args.hour} * * * {command}"


def validate_schedule(minute: int, hour: int) -> None:
    if not (0 <= minute <= 59):
        raise ValueError("Minute must be between 0 and 59.")
    if not (0 <= hour <= 23):
        raise ValueError("Hour must be between 0 and 23.")


def main() -> int:
    args = parse_args()
    try:
        validate_schedule(args.minute, args.hour)
    except ValueError as exc:
        print(f"Invalid schedule: {exc}", file=sys.stderr)
        return 1

    try:
        cron_line = build_cron_entry(args)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to build cron entry: {exc}", file=sys.stderr)
        return 1

    try:
        existing = read_existing_crontab()
        updated = ensure_entry(existing, cron_line)
        write_crontab(updated)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to install cron job: {exc}", file=sys.stderr)
        return 1

    print("Cron job installed.")
    print(cron_line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

