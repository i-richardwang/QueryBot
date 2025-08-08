import streamlit as st
import sys
import os

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Initialize configuration (auto-detect .env locally or Streamlit Cloud secrets)
from utils.core.streamlit_config import settings
from page.sql_assistant import run_query_bot

# Set page configuration
st.set_page_config(
    page_title="QueryBot",
    page_icon="💬",
)

# Run QueryBot application
run_query_bot()
