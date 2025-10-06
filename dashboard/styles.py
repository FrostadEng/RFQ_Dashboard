"""
Custom CSS styles for the RFQ Dashboard two-panel layout.

Provides:
- Fixed left panel (30% width)
- Scrollable right panel (70% width)
- Responsive design for mobile (<768px)
- Badge styling for statistics
- Loading states and hover effects
"""


def get_custom_css() -> str:
    """
    Return custom CSS for polished dark theme with depth and hierarchy.

    Design System (Discord + Linear + Streamlit):
    - Canvas: #1E1E1E (very dark grey)
    - Card: #2C2F33 (medium grey with elevation)
    - Panel: #32363C (lightened for nesting)
    - Primary text: #E5E7EB
    - Secondary text/metadata: #9CA3AF
    - Links: #3B82F6 (blue)
    - Warnings: #F59E0B (amber)
    - Success: #10B981 (green)
    - Shadows: 0 2px 8px rgba(0,0,0,0.3) for depth

    Typography:
    - Section titles: 1.25rem, 600 weight
    - Body text: 0.875rem-1rem
    - Metadata: 0.75rem, #9CA3AF

    Returns:
        CSS string to be injected via st.markdown()
    """
    return """
    <style>
    /* Global dark theme canvas */
    .stApp {
        background-color: #1E1E1E !important;
    }

    /* Main layout container */
    .main-container {
        display: flex;
        height: calc(100vh - 100px);
        gap: 1rem;
    }

    /* Three-panel layout - Left panel (Projects) - Darker sidebar */
    [data-testid="column"]:first-child {
        background-color: #1E2124 !important;  /* Darker for sidebar */
        padding: 1.5rem !important;
        border-radius: 0.5rem !important;
        border: 2px solid #2C2F33 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
    }

    /* Primary text in left panel */
    [data-testid="column"]:first-child * {
        color: #E5E7EB !important;
        font-size: 0.875rem !important;
    }

    /* Section headers in left panel - larger, bolder */
    [data-testid="column"]:first-child h1,
    [data-testid="column"]:first-child h2,
    [data-testid="column"]:first-child h3 {
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-bottom: 1rem !important;
    }

    /* Input fields - refined styling */
    [data-testid="column"]:first-child input {
        color: #E5E7EB !important;
        background-color: #32363C !important;
        border: 1px solid #4A4D51 !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
    }

    [data-testid="column"]:first-child input:focus {
        background-color: #3A3E44 !important;
        border-color: #3B82F6 !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }

    /* Input labels - metadata grey */
    [data-testid="column"]:first-child label {
        color: #9CA3AF !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.025em !important;
    }

    /* Selectbox styling */
    [data-testid="column"]:first-child .stSelectbox > div > div {
        background-color: #32363C !important;
        border: 1px solid #4A4D51 !important;
        border-radius: 0.5rem !important;
        color: #E5E7EB !important;
        font-size: 0.875rem !important;
    }

    [data-testid="column"]:first-child .stSelectbox > div > div:hover {
        border-color: #3B82F6 !important;
    }

    /* Multiselect styling */
    [data-testid="column"]:first-child .stMultiSelect > div > div {
        background-color: #32363C !important;
        border: 1px solid #4A4D51 !important;
        border-radius: 0.5rem !important;
    }

    [data-testid="column"]:first-child .stMultiSelect input {
        background-color: #32363C !important;
        color: #E5E7EB !important;
    }

    /* Date input styling */
    [data-testid="column"]:first-child .stDateInput > div > div {
        background-color: #32363C !important;
        border: 1px solid #4A4D51 !important;
        border-radius: 0.5rem !important;
    }

    [data-testid="column"]:first-child .stDateInput input {
        background-color: #32363C !important;
        color: #E5E7EB !important;
        font-size: 0.875rem !important;
    }

    /* Center panel (55%) - Primary content area - Lighter for emphasis */
    [data-testid="column"]:nth-child(2) {
        background-color: #35393F !important;  /* Noticeably lighter than sidebars */
        padding: 1.5rem !important;
        border-radius: 0.5rem !important;
        border: 2px solid #4A4D51 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }

    /* Right panel (25%) - Supplier list - Darker sidebar */
    [data-testid="column"]:last-child {
        background-color: #1E2124 !important;  /* Same as left panel */
        padding: 1.5rem !important;
        border-radius: 0.5rem !important;
        border: 2px solid #2C2F33 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
    }

    /* Center panel section headers - larger with spacing */
    [data-testid="column"]:nth-child(2) h1 {
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
    }

    [data-testid="column"]:nth-child(2) h2 {
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        padding-top: 1rem !important;
        border-top: 1px solid #4A4D51 !important;
    }

    [data-testid="column"]:nth-child(2) h3 {
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 1.125rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }

    /* Center panel body text */
    [data-testid="column"]:nth-child(2) p {
        color: #E5E7EB !important;
        font-size: 0.875rem !important;
        line-height: 1.5 !important;
    }

    /* Center panel spans and divs */
    [data-testid="column"]:nth-child(2) span,
    [data-testid="column"]:nth-child(2) div {
        color: #E5E7EB !important;
    }

    /* Right panel text - lighter */
    [data-testid="column"]:last-child * {
        color: #E5E7EB !important;
    }

    /* Right panel headers */
    [data-testid="column"]:last-child h3 {
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 1.125rem !important;
        margin-bottom: 1rem !important;
    }

    /* Right panel supplier list - enhanced full-width items */
    [data-testid="column"]:last-child .stRadio > div > label {
        background-color: #2C2F33 !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        border-radius: 0.5rem !important;
        border: 1px solid rgba(74, 77, 81, 0.5) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: #E5E7EB !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        cursor: pointer !important;
        width: 100% !important;
        display: block !important;
    }

    [data-testid="column"]:last-child .stRadio > div > label:hover {
        background-color: #353A3E !important;
        border-color: #5A5D61 !important;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    }

    [data-testid="column"]:last-child .stRadio > div > label[data-checked="true"] {
        background-color: rgba(59, 130, 246, 0.2) !important;
        border-color: #3B82F6 !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4) !important;
    }

    /* Custom scrollbar styling - dark theme */
    *::-webkit-scrollbar {
        width: 8px;
    }

    *::-webkit-scrollbar-track {
        background: #2C2F33;
        border-radius: 4px;
    }

    *::-webkit-scrollbar-thumb {
        background: #4A4D51;
        border-radius: 4px;
    }

    *::-webkit-scrollbar-thumb:hover {
        background: #5A5D61;
    }

    /* Statistics badges - metadata styling */
    .stat-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem 0.25rem 0.25rem 0;
        background-color: transparent;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #9CA3AF;
    }

    .stat-badge.files {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .stat-badge.size {
        background-color: rgba(156, 163, 175, 0.15);
        color: #9CA3AF;
        border: 1px solid rgba(156, 163, 175, 0.3);
    }

    .stat-badge.date {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Project list items - cards with depth */
    .project-item {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(74, 77, 81, 0.5);
        background-color: #32363C;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .project-item:hover {
        background-color: #3A3E44;
        border-color: #5A5D61;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }

    .project-item.selected {
        background-color: rgba(59, 130, 246, 0.15);
        border-color: #3B82F6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }

    /* Streamlit radio buttons in left panel - card elevation */
    [data-testid="column"]:first-child .stRadio {
        background-color: transparent !important;
    }

    [data-testid="column"]:first-child .stRadio > div {
        gap: 0.5rem !important;
    }

    [data-testid="column"]:first-child .stRadio > div > label {
        background-color: #32363C !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        border-radius: 0.5rem !important;
        border: 1px solid rgba(74, 77, 81, 0.5) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: #E5E7EB !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        cursor: pointer !important;
    }

    [data-testid="column"]:first-child .stRadio > div > label:hover {
        background-color: #3A3E44 !important;
        border-color: #5A5D61 !important;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    }

    [data-testid="column"]:first-child .stRadio > div > label[data-checked="true"] {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border-color: #3B82F6 !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }

    /* Supplier dropdown headers */
    .supplier-header {
        transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .supplier-header:hover {
        background-color: #3A3E44;
    }

    /* Folder structure expanders - cards with depth and smooth transitions */
    .stExpander {
        background-color: #2C2F33 !important;
        border-radius: 0.5rem !important;
        border: 1px solid rgba(74, 77, 81, 0.5) !important;
        margin: 1rem 0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stExpander:hover {
        border-color: #5A5D61 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    }

    .stExpander > summary {
        background-color: #2C2F33 !important;
        padding: 1rem 1.25rem !important;
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stExpander > summary:hover {
        background-color: #32363C !important;
    }

    /* Folder structure content area - lightened panel for depth */
    .stExpander [data-testid="stExpanderDetails"] {
        background-color: #32363C !important;
        padding: 1rem 1.25rem !important;
        border-radius: 0 0 0.5rem 0.5rem !important;
    }

    /* Expander text - primary text color */
    .stExpander * {
        color: #E5E7EB !important;
        font-size: 0.875rem !important;
    }

    /* Expander labels and metadata - soft grey */
    .stExpander label,
    .stExpander .metadata {
        color: #9CA3AF !important;
        font-size: 0.75rem !important;
    }

    /* Metadata text (captions, file counts, dates) */
    .metadata-text,
    [data-testid="stCaptionContainer"] {
        color: #9CA3AF !important;
        font-size: 0.75rem !important;
        font-weight: 400 !important;
        margin: 0.25rem 0 !important;
    }

    /* Event cards for transmissions/receipts */
    .event-card {
        background-color: #2C2F33 !important;
        border: 1px solid rgba(74, 77, 81, 0.8) !important;
        border-radius: 0.5rem !important;
        padding: 0 !important;
        margin: 1rem 0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        overflow: hidden !important;
    }

    /* Event card header bar */
    .event-card-header {
        background-color: #23272A !important;
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid rgba(74, 77, 81, 0.5) !important;
    }

    .event-card-header strong {
        color: #E5E7EB !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* Event card body */
    .event-card-body {
        padding: 1rem !important;
    }

    /* File action icons alignment - close to filename */
    .file-row {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        margin: 0.25rem 0 !important;
    }

    .file-name {
        flex: 1 !important;
        min-width: 0 !important;
    }

    .file-actions {
        display: flex !important;
        gap: 0.25rem !important;
        flex-shrink: 0 !important;
    }

    /* Reduce gap between file columns for tighter icon alignment */
    .stExpander [data-testid="column"] {
        gap: 0.25rem !important;
        padding: 0 0.25rem !important;
    }

    /* Make action buttons more compact */
    .stExpander button {
        padding: 0.25rem 0.5rem !important;
        min-height: 2rem !important;
    }

    /* Pagination controls - dark theme card */
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0;
        padding: 1rem;
        background-color: #2C2F33;
        border-radius: 0.5rem;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
    }

    .pagination button {
        padding: 0.5rem 1rem;
        border: 1px solid #4A4D51;
        border-radius: 0.5rem;
        background-color: #3A3D41;
        color: #E0E0E0;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .pagination button:hover:not(:disabled) {
        background-color: rgba(59, 130, 246, 0.2);
        border-color: #3B82F6;
    }

    .pagination button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        color: #666;
    }

    .pagination .page-info {
        font-weight: 500;
        color: #A0A0A0;
    }

    /* Streamlit buttons - dark theme styling */
    .stButton > button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #2563EB !important;
        transform: translateY(-1px);
        box-shadow: 0px 4px 8px rgba(59, 130, 246, 0.3) !important;
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    /* Loading skeleton - dark theme */
    .skeleton {
        background: linear-gradient(90deg, #2C2F33 25%, #3A3D41 50%, #2C2F33 75%);
        background-size: 200% 100%;
        animation: loading 1.5s ease-in-out infinite;
        border-radius: 0.5rem;
        height: 60px;
        margin: 0.5rem 0;
    }

    @keyframes loading {
        0% {
            background-position: 200% 0;
        }
        100% {
            background-position: -200% 0;
        }
    }

    /* Filter controls - dark theme card */
    .filter-section {
        background-color: #2C2F33;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
    }

    /* File preview button - softened blue accent */
    .file-preview-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background-color: #3B82F6;
        color: #FFFFFF;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.3);
    }

    .file-preview-btn:hover {
        background-color: #2563EB;
        transform: translateY(-1px);
        box-shadow: 0px 4px 8px rgba(59, 130, 246, 0.3);
    }

    /* Date folder styling - muted orange accent */
    .date-folder {
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
        background-color: rgba(245, 158, 11, 0.15);
        padding: 0.5rem 0.75rem;
        border-radius: 0.5rem;
        border-left: 3px solid #F59E0B;
        color: #FCD34D;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }

    /* Error states - amber warning */
    .error-message {
        padding: 1rem 1.25rem;
        background-color: rgba(245, 158, 11, 0.15);
        color: #FCD34D;
        border-radius: 0.5rem;
        border-left: 4px solid #F59E0B;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-size: 0.875rem;
    }

    /* Success states - green accent */
    .success-message {
        padding: 1rem 1.25rem;
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border-radius: 0.5rem;
        border-left: 4px solid #10B981;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-size: 0.875rem;
    }

    /* Links - blue accent with glow on hover */
    a {
        color: #3B82F6 !important;
        text-decoration: none;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer !important;
        font-weight: 500 !important;
    }

    a:hover {
        color: #60A5FA !important;
        text-decoration: underline;
        text-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
    }

    /* Warning text (file not found) - amber accent */
    .warning,
    .error-text {
        color: #F59E0B !important;
        font-size: 0.75rem !important;
    }

    /* Success text - green accent */
    .success-text {
        color: #10B981 !important;
        font-size: 0.75rem !important;
    }

    /* Dividers between sections */
    hr {
        border: none;
        border-top: 1px solid #4A4D51;
        margin: 1rem 0;
    }

    /* Accessibility improvements */
    .visually-hidden {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }

    /* Focus states for keyboard navigation - softened blue */
    *:focus-visible {
        outline: 2px solid #3B82F6;
        outline-offset: 2px;
    }

    /* Responsive design for mobile */
    @media screen and (max-width: 768px) {
        .main-container {
            flex-direction: column;
            height: auto;
        }

        [data-testid="column"]:first-child,
        [data-testid="column"]:last-child {
            width: 100%;
            margin-bottom: 1rem;
        }

        .project-item:hover {
            transform: none;
        }
    }
    </style>
    """


def get_statistics_badge(label: str, value: str, badge_type: str = "default") -> str:
    """
    Generate HTML for a statistics badge.

    Args:
        label: Badge label (e.g., "Files", "Size")
        value: Badge value (e.g., "15", "23.4 MB")
        badge_type: Type of badge ("files", "size", "date", or "default")

    Returns:
        HTML string for the badge
    """
    return f'<span class="stat-badge {badge_type}">{label}: {value}</span>'


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted size string (e.g., "23.4 MB", "1.2 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
