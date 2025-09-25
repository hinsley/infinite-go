#!/usr/bin/env python3
"""Utility for creating timestamped SQLite backups with simple retention."""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sqlite3
import sys
from pathlib import Path
from typing import Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "database.db"
DEFAULT_BACKUP_DIR = PROJECT_ROOT / "data" / "backups"
DEFAULT_RETENTION = 30


def positive_int(value: str) -> int:
    """Parse a string as a non-negative integer."""

    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("Value must be zero or positive.")
    return parsed


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Create a timestamped backup of the Infinite Go SQLite database."
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to the live SQLite database (default: {DEFAULT_DB_PATH}).",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_BACKUP_DIR,
        help=f"Directory for storing backups (default: {DEFAULT_BACKUP_DIR}).",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="",
        help="Optional suffix for the backup filename (letters, numbers, dash, underscore).",
    )
    parser.add_argument(
        "--retention",
        type=positive_int,
        default=DEFAULT_RETENTION,
        help="Number of most recent backups to keep (0 disables pruning).",
    )
    return parser.parse_args(argv)


def sanitize_label(label: str) -> str:
    """Return a filesystem-safe label derived from the user provided suffix."""

    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", label).strip("-")
    return cleaned


def compute_backup_path(destination: Path, label: str) -> Path:
    """Generate a timestamped backup filename."""

    timestamp = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    suffix = f"-{label}" if label else ""
    return destination / f"database-{timestamp}{suffix}.db"


def create_backup(source: Path, destination: Path, label: str) -> Path:
    """Perform a SQLite online backup to the destination path."""

    if not source.exists():
        raise FileNotFoundError(f"Database not found at {source}.")
    destination.mkdir(parents=True, exist_ok=True)
    sanitized_label = sanitize_label(label)
    backup_path = compute_backup_path(destination, sanitized_label)
    with sqlite3.connect(source) as live_db:
        with sqlite3.connect(backup_path) as backup_db:
            live_db.backup(backup_db)
    return backup_path


def prune_backups(destination: Path, keep: int) -> List[Path]:
    """Remove old backup files beyond the retention limit."""

    if keep <= 0:
        return []
    backups = sorted(
        destination.glob("database-*.db"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    removed: List[Path] = []
    for stale in backups[keep:]:
        stale.unlink()
        removed.append(stale)
    return removed


def main(argv: Iterable[str] | None = None) -> int:
    """Script entry point."""

    args = parse_args(argv)
    try:
        backup_path = create_backup(args.db_path, args.destination, args.label)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Backup failed: {exc}", file=sys.stderr)
        return 1
    removed = prune_backups(args.destination, args.retention)
    print(f"Backup written to {backup_path}.")
    if removed:
        print(f"Pruned {len(removed)} old backup(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

