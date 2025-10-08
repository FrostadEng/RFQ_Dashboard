"""
Database query functions for RFQ Dashboard.
"""

import logging
import streamlit as st
from typing import List, Dict, Any, Optional

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


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_suppliers_by_partner_type(
    _db_manager: DBManager,
    project_number: str,
    partner_type: str
) -> List[Dict[str, Any]]:
    """
    Fetch suppliers filtered by partner_type with backward compatibility.

    Args:
        _db_manager: DBManager instance
        project_number: Project number to fetch suppliers for
        partner_type: Partner type filter ('Supplier' or 'Contractor')

    Returns:
        List of supplier dictionaries matching the partner_type
    """
    try:
        # Build query with backward compatibility:
        # If partner_type field doesn't exist, treat as 'Supplier'
        if partner_type == "Supplier":
            query = {
                "project_number": project_number,
                "$or": [
                    {"partner_type": "Supplier"},
                    {"partner_type": {"$exists": False}}  # Backward compatibility
                ]
            }
        else:
            query = {
                "project_number": project_number,
                "partner_type": partner_type
            }

        suppliers = list(_db_manager.db.suppliers.find(query).sort("supplier_name", 1))
        logger.info(f"Loaded {len(suppliers)} {partner_type}s for project {project_number}")
        return suppliers

    except Exception as e:
        logger.error(f"Error fetching suppliers by partner_type for project {project_number}: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_submissions_by_partner_type(
    _db_manager: DBManager,
    project_number: str,
    partner_type: str,
    submission_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch submissions filtered by partner_type and optionally by direction (sent/received).

    Args:
        _db_manager: DBManager instance
        project_number: Project number to fetch submissions for
        partner_type: Partner type filter ('Supplier' or 'Contractor')
        submission_type: Optional direction filter ('sent' or 'received')

    Returns:
        List of submission dictionaries matching the filters
    """
    try:
        # Build query with backward compatibility
        if partner_type == "Supplier":
            query = {
                "project_number": project_number,
                "$or": [
                    {"partner_type": "Supplier"},
                    {"partner_type": {"$exists": False}}  # Backward compatibility
                ]
            }
        else:
            query = {
                "project_number": project_number,
                "partner_type": partner_type
            }

        # Add submission_type filter if provided
        if submission_type:
            query["type"] = submission_type

        submissions = list(_db_manager.db.submissions.find(query).sort("date", -1))
        logger.info(
            f"Loaded {len(submissions)} {partner_type} submissions "
            f"({'all' if not submission_type else submission_type}) for project {project_number}"
        )
        return submissions

    except Exception as e:
        logger.error(f"Error fetching submissions by partner_type for project {project_number}: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_project_statistics(
    _db_manager: DBManager,
    project_number: str,
    partner_type: str
) -> Dict[str, int]:
    """
    Compute project-level statistics using aggregation pipeline.

    Returns counts of unique partners contacted (sent) and partners with responses (received).

    Args:
        _db_manager: DBManager instance
        project_number: Project number to compute statistics for
        partner_type: Partner type filter ('Supplier' or 'Contractor')

    Returns:
        Dictionary with 'contacted_count' and 'response_count' keys
    """
    try:
        # Build match stage with backward compatibility
        if partner_type == "Supplier":
            match_stage = {
                "project_number": project_number,
                "$or": [
                    {"partner_type": "Supplier"},
                    {"partner_type": {"$exists": False}}
                ]
            }
        else:
            match_stage = {
                "project_number": project_number,
                "partner_type": partner_type
            }

        # Aggregation pipeline for contacted count (unique suppliers with sent submissions)
        contacted_pipeline = [
            {"$match": {**match_stage, "type": "sent"}},
            {"$group": {"_id": "$supplier_name"}},
            {"$count": "contacted_count"}
        ]

        # Aggregation pipeline for response count (unique suppliers with received submissions)
        response_pipeline = [
            {"$match": {**match_stage, "type": "received"}},
            {"$group": {"_id": "$supplier_name"}},
            {"$count": "response_count"}
        ]

        contacted_result = list(_db_manager.db.submissions.aggregate(contacted_pipeline))
        response_result = list(_db_manager.db.submissions.aggregate(response_pipeline))

        contacted_count = contacted_result[0]["contacted_count"] if contacted_result else 0
        response_count = response_result[0]["response_count"] if response_result else 0

        stats = {
            "contacted_count": contacted_count,
            "response_count": response_count
        }

        logger.info(
            f"Project {project_number} {partner_type} stats: "
            f"{contacted_count} contacted, {response_count} responses"
        )
        return stats

    except Exception as e:
        logger.error(f"Error computing project statistics for project {project_number}: {e}")
        return {"contacted_count": 0, "response_count": 0}


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_partner_statistics(
    _db_manager: DBManager,
    project_number: str,
    partner_type: str
) -> List[Dict[str, Any]]:
    """
    Compute partner-level statistics using aggregation pipeline.

    Returns sent and received counts per partner, sorted alphabetically.

    Args:
        _db_manager: DBManager instance
        project_number: Project number to compute statistics for
        partner_type: Partner type filter ('Supplier' or 'Contractor')

    Returns:
        List of dictionaries with supplier_name, sent_count, and received_count
    """
    try:
        # Build match stage with backward compatibility
        if partner_type == "Supplier":
            match_stage = {
                "project_number": project_number,
                "$or": [
                    {"partner_type": "Supplier"},
                    {"partner_type": {"$exists": False}}
                ]
            }
        else:
            match_stage = {
                "project_number": project_number,
                "partner_type": partner_type
            }

        # Aggregation pipeline for partner-level statistics
        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$supplier_name",
                    "sent_count": {
                        "$sum": {"$cond": [{"$eq": ["$type", "sent"]}, 1, 0]}
                    },
                    "received_count": {
                        "$sum": {"$cond": [{"$eq": ["$type", "received"]}, 1, 0]}
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "supplier_name": "$_id",
                    "sent_count": 1,
                    "received_count": 1
                }
            },
            {"$sort": {"supplier_name": 1}}  # Sort alphabetically
        ]

        partner_stats = list(_db_manager.db.submissions.aggregate(pipeline))

        logger.info(
            f"Computed statistics for {len(partner_stats)} {partner_type}s "
            f"in project {project_number}"
        )
        return partner_stats

    except Exception as e:
        logger.error(f"Error computing partner statistics for project {project_number}: {e}")
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
