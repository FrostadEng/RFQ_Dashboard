#!/usr/bin/env python3
"""
Migration script to reorganize mock_projects from legacy to new folder structure.

Legacy: Projects/{project}/RFQ/{supplier}/{Received|Sent}/{date}/
New: Projects/{project}/1-RFQ/Supplier RFQ Quotes/{supplier}/{Received|Sent}/{date}/
"""

import shutil
import sys
from pathlib import Path


def migrate_project_folder(project_path: Path, dry_run: bool = False):
    """
    Migrate a single project folder from legacy to new structure.

    Args:
        project_path: Path to the project folder
        dry_run: If True, only print what would be done
    """
    project_number = project_path.name

    # Check if already migrated
    new_rfq_folder = project_path / "1-RFQ"
    if new_rfq_folder.exists():
        print(f"✓ Project {project_number} already migrated (1-RFQ exists)")
        return

    # Find legacy RFQ folder
    rfq_folder = None
    for folder_name in ["RFQ", "Supplier RFQ", "Contractor"]:
        candidate = project_path / folder_name
        if candidate.exists() and candidate.is_dir():
            rfq_folder = candidate
            break

    if not rfq_folder:
        print(f"✗ Project {project_number}: No RFQ folder found, skipping")
        return

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating project {project_number}...")
    print(f"  Legacy RFQ folder: {rfq_folder.name}")

    # Create new structure
    new_supplier_quotes_path = new_rfq_folder / "Supplier RFQ Quotes"

    if dry_run:
        print(f"  Would create: {new_rfq_folder}")
        print(f"  Would create: {new_supplier_quotes_path}")

        # List suppliers that would be moved
        suppliers = [
            d.name for d in rfq_folder.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        for supplier in suppliers:
            print(f"  Would move: {supplier} -> {new_supplier_quotes_path / supplier}")
    else:
        # Create new directory structure
        new_supplier_quotes_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created: {new_supplier_quotes_path}")

        # Move each supplier folder
        for supplier_folder in rfq_folder.iterdir():
            if supplier_folder.is_dir() and not supplier_folder.name.startswith('.'):
                new_supplier_path = new_supplier_quotes_path / supplier_folder.name

                # Move the supplier folder
                shutil.move(str(supplier_folder), str(new_supplier_path))
                print(f"  ✓ Moved: {supplier_folder.name} -> {new_supplier_path}")

        # Remove old RFQ folder if empty
        if not any(rfq_folder.iterdir()):
            rfq_folder.rmdir()
            print(f"  ✓ Removed empty legacy folder: {rfq_folder.name}")
        else:
            print(f"  ⚠ Legacy folder not empty, kept: {rfq_folder.name}")

    print(f"✓ Project {project_number} migration complete")


def migrate_all_projects(root_path: Path, dry_run: bool = False):
    """
    Migrate all project folders in the root path.

    Args:
        root_path: Root path containing project folders
        dry_run: If True, only print what would be done
    """
    if not root_path.exists():
        print(f"Error: Root path does not exist: {root_path}")
        sys.exit(1)

    print(f"{'=' * 70}")
    print(f"Mock Projects Migration Script")
    print(f"{'=' * 70}")
    print(f"Root path: {root_path}")
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (will modify files)'}")
    print(f"{'=' * 70}\n")

    # Find all project folders (numeric names)
    project_folders = [
        p for p in root_path.iterdir()
        if p.is_dir() and p.name.isdigit()
    ]

    if not project_folders:
        print("No project folders found (expected numeric folder names)")
        return

    print(f"Found {len(project_folders)} project(s) to migrate\n")

    for project_folder in sorted(project_folders):
        migrate_project_folder(project_folder, dry_run)

    print(f"\n{'=' * 70}")
    print(f"Migration {'simulation' if dry_run else 'process'} complete!")
    print(f"{'=' * 70}")

    if dry_run:
        print("\nTo perform the actual migration, run with --execute flag:")
        print(f"  python {sys.argv[0]} --execute")


def main():
    """Main entry point."""
    # Determine root path (default to mock_projects in current directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    mock_projects_path = project_root / "mock_projects"

    # Check for command line arguments
    dry_run = True
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--execute", "-e"]:
            dry_run = False
        elif sys.argv[1] in ["--help", "-h"]:
            print("Usage: python migrate_mock_projects.py [--execute|-e]")
            print("\nOptions:")
            print("  --execute, -e  Perform actual migration (default is dry run)")
            print("  --help, -h     Show this help message")
            sys.exit(0)

    migrate_all_projects(mock_projects_path, dry_run)


if __name__ == "__main__":
    main()
