import streamlit as st
import sys
import os

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

# Initialize configuration (auto-detect .env locally or Streamlit Cloud secrets)
from utils.core.streamlit_config import settings
from vector_db_management import run_vector_db_management

# Set page configuration
st.set_page_config(
    page_title="QueryBot - Admin Tools",
    page_icon="🔧",
    layout="wide"
)

# Apply basic styles
st.markdown("""
<style>
h1 {
    color: #1E90FF;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}
/* Hide streamlit default menu and footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🔧 QueryBot - Admin Tools")
st.markdown("---")
st.info("This tool is for development and maintenance personnel only, used to manage vector databases and system configurations.")

# Run vector database management application
run_vector_db_management()