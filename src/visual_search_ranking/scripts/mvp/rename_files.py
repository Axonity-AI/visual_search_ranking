"""
File Renaming Script

Renames files using MD5 hash of their content.
Useful for creating unique filenames and deduplication.
"""

import hashlib
import os
from pathlib import Path


def file_as_bytes(filepath: Path) -> bytes:
    """Read file as bytes."""
    with open(filepath, 'rb') as f:
        return f.read()


def hash_file(filepath: Path) -> str:
    """Generate MD5 hash of file content."""
    return hashlib.md5(file_as_bytes(filepath)).hexdigest()


def rename_files_with_hash(directory: Path, dry_run: bool = True):
    """
    Rename all files in a directory using their MD5 hash.

    Args:
        directory: Path to the directory containing files
        dry_run: If True, only print what would happen without renaming
    """
    for fname in os.listdir(directory):
        filepath = directory / fname
        if not filepath.is_file():
            continue

        name, ext = os.path.splitext(fname)
        file_hash = hash_file(filepath)
        new_name = file_hash + ext

        print(f"{fname} --> {new_name}")

        if not dry_run:
            new_path = directory / new_name
            os.rename(filepath, new_path)

    if dry_run:
        print("\n(Dry run - no files were renamed. Set dry_run=False to rename.)")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        print("Usage: python rename_files.py <directory>")
        print("Add --execute to actually rename files")
        sys.exit(1)

    dry_run = "--execute" not in sys.argv

    rename_files_with_hash(directory, dry_run=dry_run)
