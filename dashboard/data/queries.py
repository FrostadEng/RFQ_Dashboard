"""
Database query functions for the RFQ Dashboard.
"""
import logging
from typing import List, Dict, Any, Optional
import streamlit as st

from rfq_tracker.db_manager import DBManager
from dashboard.config import load_config

logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_all_suppliers(_db_manager: DBManager) -> List[str]:
    """
    Fetch all unique supplier names from the database.

    Args:
        _db_manager: DBManager instance

    Returns:
        Sorted list of unique supplier names
    """
    try:
        suppliers = _db_manager.db.suppliers.distinct("supplier_name")
        return sorted(suppliers)
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_projects(_db_manager: DBManager) -> List[Dict[str, Any]]:
    """
    Fetch all projects from MongoDB with caching.

    Args:
        _db_manager: DBManager instance (underscore prefix prevents Streamlit from hashing)

    Returns:
        List of project dictionaries
    """
    try:
        projects = list(_db_manager.db.projects.find().sort("project_number", -1))
        logger.info(f"Loaded {len(projects)} projects from database")
        return projects
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        st.error(f"Error fetching projects: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_supplier_data(_db_manager: DBManager, project_number: str) -> List[Dict[str, Any]]:
    """
    Fetch all supplier data (suppliers, transmissions, receipts) for a project with caching.

    Args:
        _db_manager: DBManager instance (underscore prefix prevents Streamlit from hashing)
        project_number: Project number to fetch suppliers for

    Returns:
        List of dictionaries containing supplier data with transmissions and receipts
    """
    try:
        # Fetch all suppliers for the project, sorted alphabetically
        suppliers = list(_db_manager.db.suppliers.find(
            {"project_number": project_number}
        ).sort("supplier_name", 1))

        supplier_data = []

        for supplier in suppliers:
            supplier_name = supplier['supplier_name']

            # Fetch all submissions for this supplier, sorted by date descending (newest first)
            submissions = list(_db_manager.db.submissions.find({
                "project_number": project_number,
                "supplier_name": supplier_name
            }).sort("date", -1))

            # Separate into sent and received
            transmissions = [s for s in submissions if s.get('type') == 'sent']
            receipts = [s for s in submissions if s.get('type') == 'received']

            supplier_data.append({
                'supplier': supplier,
                'transmissions': transmissions,
                'receipts': receipts
            })

        logger.info(f"Loaded {len(supplier_data)} suppliers for project {project_number}")
        return supplier_data

    except Exception as e:
        logger.error(f"Error fetching supplier data for project {project_number}: {e}")
        st.error(f"Error loading supplier data: {e}")
        return []


def initialize_db_manager() -> Optional[DBManager]:
    """Initialize database connection with error handling."""
    config = load_config()

    try:
        db_manager = DBManager(config['mongo_uri'], config['mongo_db'])
        db_manager.connect()
        return db_manager
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        st.error("❌ Failed to connect to MongoDB. Please check the database is running.")
        st.info("**Troubleshooting:**\n- Verify MongoDB is running\n- Check config.json for correct connection settings\n- Ensure network connectivity")

        if st.button("🔄 Retry Connection"):
            st.rerun()

        return None