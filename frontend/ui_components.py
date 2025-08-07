import streamlit as st
from typing import Dict, Any, Optional
import time

# Version number
VERSION = "0.1.0"


class ProgressTracker:
    """Simple progress tracker for LangGraph stream updates."""

    def __init__(self):
        self.progress_bar = None
        self.status_text = None
        self.current_step = 0
        self.total_steps = 13  # Total number of processing nodes

        # Node display names
        self.node_names = {
            "intent_analysis": "🧠 Analyzing Query Intent",
            "keyword_extraction": "🔍 Extracting Keywords",
            "domain_term_mapping": "🗺️ Mapping Business Terms",
            "query_rewrite": "✍️ Rewriting Query",
            "data_source_identification": "📊 Identifying Data Sources",
            "table_structure_analysis": "🏗️ Analyzing Table Structure",
            "feasibility_checking": "✅ Checking Feasibility",
            "query_example_retrieval": "📝 Retrieving Query Examples",
            "sql_generation": "⚡ Generating SQL Statement",
            "permission_control": "🔒 Applying Permissions",
            "sql_execution": "🚀 Executing SQL",
            "error_analysis": "🔧 Analyzing Errors",
            "result_generation": "📋 Generating Results"
        }

    def start(self):
        """Initialize progress display."""
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        self.current_step = 0

    def update(self, node_name: str):
        """Update progress for a node."""
        if node_name in self.node_names:
            self.current_step += 1
            progress = min(self.current_step / self.total_steps, 1.0)

            if self.progress_bar:
                self.progress_bar.progress(progress)

            if self.status_text:
                display_name = self.node_names[node_name]
                self.status_text.text(f"Processing: {display_name}")

    def complete(self):
        """Mark processing as complete."""
        if self.progress_bar:
            self.progress_bar.progress(1.0)
        if self.status_text:
            self.status_text.success("✅ Processing Complete")

    def error(self, message: str):
        """Display error message."""
        if self.status_text:
            self.status_text.error(f"❌ {message}")


def apply_common_styles():
    """Apply common CSS styles to the Streamlit application."""
    st.markdown(_get_common_styles(), unsafe_allow_html=True)


def display_project_info():
    """Display project information including author and repository links."""
    st.markdown(
        """
        <style>
        .project-info {
            background-color: rgba(240, 242, 246, 0.5);
            border-left: 4px solid #1E90FF;
            padding: 0.75rem 1rem;
            margin: 1rem 0;
            border-radius: 0 0.25rem 0.25rem 0;
            font-size: 0.9rem;
        }
        .project-info a {
            text-decoration: none;
            color: #1E90FF;
        }
        .project-info a:hover {
            text-decoration: underline;
        }
        .project-separator {
            color: #666;
        }
        @media (prefers-color-scheme: dark) {
            .project-info {
                background-color: rgba(33, 37, 41, 0.3);
                border-left-color: #3498DB;
            }
            .project-info a {
                color: #3498DB;
            }
            .project-separator {
                color: #999;
            }
        }
        </style>
        <div class="project-info">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <span>
                    <strong>🚀 Open Source Project</strong> by
                    <a href="https://github.com/i-richardwang" target="_blank">
                        <strong>Richard Wang</strong>
                    </a>
                </span>
                <span class="project-separator">•</span>
                <a href="https://github.com/i-richardwang/QueryBot" target="_blank"
                   style="display: flex; align-items: center; gap: 0.3rem;">
                    <span>📁</span> <strong>GitHub Repository</strong>
                </a>
                <span class="project-separator">•</span>
                <span class="project-separator">⭐ Star if you find it useful!</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_demo_data_info():
    """Display demo data source information and example queries."""
    st.info(
        """
        **📊 Demo Data Source**: This demo uses a recruitment management dataset with 3 main tables:
        - **Recruitment Activities** (50 records): Job postings, departments, success rates
        - **Interviewers** (100 records): Interview schedules, scores, expertise areas
        - **Candidates** (500 records): Applications, education, experience, interview results

        **💡 Try these example queries**:
        • "Show all Java Developer candidates"
        • "Calculate Engineering department recruitment success rate"
        • "List candidates from Stanford University"
        • "Find activities where James Smith was an interviewer"
        """
    )


def _get_common_styles():
    """Return common CSS styles for the application interface."""
    return """
    <style>
    .stTextInput>div>div>input {
        border-color: #E0E0E0;
    }
    .stProgress > div > div > div > div {
        background-color: #4F8BF9;
    }
    h2, h3, h4 {
        border-bottom: 2px solid !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    h2 {
        color: #1E90FF !important;
        border-bottom-color: #1E90FF !important;
        font-size: 1.8rem !important;
        margin-top: 1.5rem !important;
    }
    h3 {
        color: #16A085 !important;
        border-bottom-color: #16A085 !important;
        font-size: 1.5rem !important;
        margin-top: 1rem !important;
    }
    h4 {
        color: #E67E22 !important;
        border-bottom-color: #E67E22 !important;
        font-size: 1.2rem !important;
        margin-top: 0.5rem !important;
    }
    .workflow-container {
        background-color: rgba(248, 249, 250, 0.05);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.125);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    @media (prefers-color-scheme: dark) {
        .workflow-container {
            background-color: rgba(33, 37, 41, 0.05);
            border-color: rgba(255, 255, 255, 0.125);
        }
        h2 {
            color: #3498DB !important;
            border-bottom-color: #3498DB !important;
        }
        h3 {
            color: #2ECC71 !important;
            border-bottom-color: #2ECC71 !important;
        }
        h4 {
            color: #F39C12 !important;
            border-bottom-color: #F39C12 !important;
        }
    }
    .workflow-step {
        margin-bottom: 1rem;
    }
    </style>
    """

