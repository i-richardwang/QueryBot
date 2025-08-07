import os
import sys
import streamlit as st
import uuid
import time

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from frontend.ui_components import apply_common_styles, display_project_info, display_demo_data_info


def initialize_query_bot():
    """Initialize QueryBot application"""
    # Apply custom styles
    apply_common_styles()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


def run_query_bot():
    """Main function to run QueryBot application"""
    initialize_query_bot()

    st.title("💬 QueryBot")
    st.markdown("---")

    display_project_info()

    display_architecture_diagram()

    display_info_message()

    display_demo_data_info()

    process_user_query()


def display_info_message():
    """Display information message for QueryBot."""
    st.info(
        """
    This tool leverages the semantic understanding capabilities of large language models to analyze and generate SQL queries through natural language interaction.

    The system can understand and analyze users' natural language query requirements, automatically identify relevant data tables, generate standard SQL statements and execute queries, and finally present query results in an understandable way.
    """
    )


def display_architecture_diagram():
    """Display system architecture diagram in an expander."""
    with st.expander("🏗️ System Architecture", expanded=False):
        # Load and display the architecture diagram
        try:
            architecture_path = os.path.join(project_root, "frontend", "assets", "architecture_diagram.png")
            if os.path.exists(architecture_path):
                st.image(architecture_path, caption="QueryBot System Architecture", use_container_width=True)
            else:
                st.warning("Architecture diagram not found.")
        except Exception as e:
            st.error(f"Error loading architecture diagram: {str(e)}")


def process_user_query():
    """Process user queries and display results."""
    st.markdown("## SQL Query Conversation")

    chat_container = st.container(border=True)
    input_placeholder = st.empty()

    display_conversation_history(chat_container)
    user_query = input_placeholder.chat_input("Please enter your query:")

    if user_query:
        display_user_input(chat_container, user_query)
        process_and_display_response(chat_container, user_query)


def display_conversation_history(container):
    """Display conversation history."""
    with container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # If it's an assistant reply and contains SQL statement, display SQL code block
                if message["role"] == "assistant" and "sql_query" in message:
                    st.code(message["sql_query"], language="sql")

                # If it contains query results, display data table
                if "results" in message:
                    st.dataframe(message["results"])


def display_user_input(container, user_query):
    """Display user input and save to conversation history."""
    with container:
        with st.chat_message("user"):
            st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})


def process_and_display_response(container, user_query):
    """Process user query and display response with real-time progress."""
    # Call backend to process query (now with progress display)
    response = process_query_with_backend(user_query)

    display_assistant_response(container, response)


def extract_table_from_markdown(text):
    """Extract table data from markdown text"""
    import re
    import pandas as pd

    # Find markdown table
    table_pattern = r"\|.*\|\n\|[-:| ]+\|\n(\|.*\|\n)+"
    table_match = re.search(table_pattern, text)

    if not table_match:
        return None

    # Extract table text
    table_text = table_match.group(0)

    try:
        # Parse markdown table using pandas
        lines = table_text.strip().split('\n')
        # Process header
        header_line = lines[0]
        headers = [col.strip() for col in header_line.split('|')[1:-1]]

        # Skip separator line (|---|---|)
        data_lines = lines[2:]
        data = []
        for line in data_lines:
            if line.strip():
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                data.append(row)

        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Only return when table actually has data
        if not df.empty:
            return df
        return None
    except Exception:
        return None


def process_query_with_backend(query):
    """Process query with backend."""
    from utils.core.streamlit_config import settings

    if settings.app.frontend_direct_call:
        return process_query_direct(query)
    else:
        return process_query_via_api(query)


def process_query_direct(query):
    """Call backend logic directly with streamlined progress display."""
    try:
        from backend.sql_assistant.graph.assistant_graph import build_query_bot_graph
        from langgraph.checkpoint.memory import MemorySaver
        from backend.sql_assistant.utils.user_mapper import UserMapper
        from utils.core.streamlit_config import settings
        from langchain_core.messages import HumanMessage
        from frontend.ui_components import ProgressTracker

        # Initialize progress tracker
        progress_tracker = ProgressTracker()
        progress_tracker.start()

        # Initialize components
        from backend.sql_assistant.graph.assistant_graph import stream_query_bot
        from langgraph.checkpoint.memory import MemorySaver

        checkpoint_saver = MemorySaver()
        user_mapper = UserMapper()

        user_id = None
        username = "anonymous"
        if settings.app.user_auth_enabled:
            user_id = user_mapper.get_user_id(username)


        # Stream execution with native LangGraph updates
        final_result = None
        try:
            # Use the new streaming function with native LangGraph stream_mode="updates"
            for chunk in stream_query_bot(
                query=query,
                thread_id=st.session_state.session_id,
                checkpoint_saver=checkpoint_saver,
                user_id=user_id
            ):
                # Handle error chunks
                if "error" in chunk:
                    progress_tracker.error(f"Execution failed: {chunk['error']['error']}")
                    break

                # Each chunk is a dict: {node_name: node_output}
                for node_name, node_output in chunk.items():
                    # Update progress tracker
                    progress_tracker.update(node_name)

                    # Capture final result from the last node
                    if isinstance(node_output, dict) and 'messages' in node_output:
                        final_result = node_output

            # Mark processing as complete if no errors
            if final_result:
                progress_tracker.complete()

        except Exception as stream_error:
            progress_tracker.error(f"Streaming execution failed: {str(stream_error)}")

            # Fallback to traditional execution if streaming fails
            with st.spinner("🔄 Switching to traditional execution mode..."):
                from backend.sql_assistant.graph.assistant_graph import run_query_bot

                result = run_query_bot(
                    query=query,
                    thread_id=st.session_state.session_id,
                    checkpoint_saver=checkpoint_saver,
                    user_id=user_id,
                )
                final_result = result
                progress_tracker.complete()
        
        # Process final result
        if final_result and 'messages' in final_result:
            messages = final_result['messages']
            if messages:
                last_message = messages[-1].content
                
                response_data = {
                    "message": last_message,
                    "session_id": st.session_state.session_id
                }
                
                table_data = extract_table_from_markdown(last_message)
                if table_data is not None:
                    response_data["results"] = table_data
                
                return response_data
            else:
                return {"error": "No assistant reply received"}
        else:
            return {"error": "No valid result obtained"}

    except Exception as e:
        # Clean up progress display (if error occurs)
        try:
            current_step_info.empty()
        except:
            pass
        return {"error": f"Direct call failed: {str(e)}"}


def process_query_via_api(query):
    """Call backend API to process query."""
    import requests

    from utils.core.streamlit_config import settings
    api_base_url = f"http://{settings.app.base_host}:8000"
    try:
        response = requests.post(
            f"{api_base_url}/api/query-bot",
            json={"text": query, "session_id": st.session_state.session_id, "username": "anonymous"},
        )
        result = response.json()

        message_text = result.get("text", "")

        response_data = {
            "message": message_text,
            "session_id": result.get("session_id", st.session_state.session_id)
        }

        table_data = extract_table_from_markdown(message_text)
        if table_data is not None:
            response_data["results"] = table_data

        return response_data
    except Exception as e:
        return {"error": f"API call failed: {str(e)}"}


def display_assistant_response(container, response):
    """Display assistant response."""
    with container:
        with st.chat_message("assistant"):
            if "error" in response:
                st.error(response["error"])
                message_content = f"Sorry, an error occurred while processing the query: {response['error']}"
            else:
                message_content = response["message"]

                # Parse message content, try to extract SQL and results
                # SQL is usually between ```sql and ```
                sql_query = None
                if '```sql' in message_content:
                    try:
                        sql_start = message_content.find('```sql') + 6
                        sql_end = message_content.find('```', sql_start)
                        if sql_end > sql_start:
                            sql_query = message_content[sql_start:sql_end].strip()
                            # Remove SQL code block to avoid displaying twice in markdown
                            message_content = message_content.replace(f"```sql\n{sql_query}\n```", "")
                    except Exception as e:
                        st.warning(f"Failed to extract SQL: {str(e)}")

                # Display message content
                st.markdown(message_content)

                # If SQL was extracted, display as code block
                if sql_query:
                    st.code(sql_query, language="sql")
                    response["sql_query"] = sql_query

                # Only display data table when there is actually non-empty result data
                if "results" in response and not response["results"].empty:
                    st.dataframe(response["results"])

            # Save to conversation history
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": message_content,
                    **response,  # Include other response information
                }
            )


# If running this file directly, start the application
if __name__ == "__main__":
    run_query_bot()
