"""
Business logic and data processing functions for RFQ Dashboard.
"""

import os
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from rfq_tracker.db_manager import DBManager

logger = logging.getLogger(__name__)


def filter_projects(
    projects: List[Dict[str, Any]],
    search_term: str,
    selected_suppliers: List[str] = None,
    date_range_start: datetime = None,
    date_range_end: datetime = None,
    db_manager: DBManager = None
) -> List[Dict[str, Any]]:
    """
    Filter projects by search term, suppliers, and date range.

    Args:
        projects: List of project dictionaries
        search_term: Search string for project number
        selected_suppliers: List of supplier names to filter by
        date_range_start: Start date for filtering (last_scanned)
        date_range_end: End date for filtering (last_scanned)
        db_manager: Database manager for supplier lookups

    Returns:
        Filtered list of projects
    """
    filtered = projects

    # Filter by search term
    if search_term:
        search_lower = search_term.lower()
        filtered = [p for p in filtered if search_lower in p['project_number'].lower()]

    # Filter by suppliers (if project has at least one selected supplier)
    if selected_suppliers and db_manager:
        projects_with_suppliers = set()
        for supplier_name in selected_suppliers:
            # Find all projects that have this supplier
            supplier_docs = db_manager.db.suppliers.find(
                {"supplier_name": supplier_name},
                {"project_number": 1}
            )
            projects_with_suppliers.update(doc['project_number'] for doc in supplier_docs)

        filtered = [p for p in filtered if p['project_number'] in projects_with_suppliers]

    # Filter by date range (last_scanned)
    if date_range_start or date_range_end:
        date_filtered = []
        for p in filtered:
            if 'last_scanned' not in p or not p['last_scanned']:
                continue

            try:
                project_date = datetime.fromisoformat(p['last_scanned'].replace('Z', '+00:00'))

                if date_range_start and project_date < date_range_start:
                    continue
                if date_range_end and project_date > date_range_end:
                    continue

                date_filtered.append(p)
            except:
                continue

        filtered = date_filtered

    return filtered


def sort_projects(projects: List[Dict[str, Any]], sort_option: str) -> List[Dict[str, Any]]:
    """Sort projects based on selected option."""
    if sort_option == "Project Number (Ascending)":
        return sorted(projects, key=lambda p: p['project_number'])
    elif sort_option == "Project Number (Descending)":
        return sorted(projects, key=lambda p: p['project_number'], reverse=True)
    elif sort_option == "Last Scanned (Newest First)":
        return sorted(projects, key=lambda p: p.get('last_scanned', ''), reverse=True)
    elif sort_option == "Last Scanned (Oldest First)":
        return sorted(projects, key=lambda p: p.get('last_scanned', ''))

    return projects


def calculate_folder_statistics(files: List[str]) -> Dict[str, Any]:
    """
    Calculate statistics for a list of files.

    Args:
        files: List of file paths

    Returns:
        Dictionary with file_count and total_size
    """
    total_size = 0
    existing_files = 0

    for file_path in files:
        try:
            path = Path(file_path)
            if path.exists():
                total_size += path.stat().st_size
                existing_files += 1
        except:
            continue

    return {
        'file_count': len(files),
        'existing_count': existing_files,
        'total_size': total_size
    }


def calculate_supplier_statistics(transmissions: List[Dict], receipts: List[Dict]) -> Dict[str, Any]:
    """
    Calculate aggregate statistics for a supplier (all sent + received).

    Args:
        transmissions: List of transmission documents
        receipts: List of receipt documents

    Returns:
        Dictionary with sent_count, received_count, total_files, total_size
    """
    sent_files = []
    received_files = []

    for trans in transmissions:
        sent_files.extend(trans.get('files', []))

    for receipt in receipts:
        received_files.extend(receipt.get('files', []))

    sent_stats = calculate_folder_statistics(sent_files)
    received_stats = calculate_folder_statistics(received_files)

    return {
        'sent_count': sent_stats['file_count'],
        'received_count': received_stats['file_count'],
        'total_files': sent_stats['file_count'] + received_stats['file_count'],
        'total_size': sent_stats['total_size'] + received_stats['total_size']
    }


def group_events_by_folder_name(events: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group events by their exact folder_name to track versions.
    Multiple entries with the same folder_name represent different versions.

    Args:
        events: List of transmission or receipt dictionaries

    Returns:
        Dictionary mapping folder names to lists of versions (sorted by date descending)
    """
    grouped = defaultdict(list)

    for event in events:
        folder_name = event.get('folder_name', 'Unknown')
        grouped[folder_name].append(event)

    # Sort each group by date (newest first)
    for folder_name in grouped:
        grouped[folder_name].sort(key=lambda x: x.get('date', ''), reverse=True)

    return dict(grouped)


def build_folder_tree(file_paths: List[str], base_path: str) -> Dict[str, Any]:
    """
    Build nested folder structure from flat file list.

    Args:
        file_paths: List of absolute file paths
        base_path: Root folder path to remove from display

    Returns:
        Nested dict representing folder hierarchy
    """
    tree = {}

    for path in file_paths:
        try:
            relative_path = path.replace(base_path, '').lstrip('/').lstrip('\\')
            parts = relative_path.split(os.sep)

            current_level = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # File
                    if '__files__' not in current_level:
                        current_level['__files__'] = []
                    current_level['__files__'].append({
                        'name': part,
                        'path': path
                    })
                else:  # Folder
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
        except Exception as e:
            logger.error(f"Error parsing path {path}: {e}")
            continue

    return tree
