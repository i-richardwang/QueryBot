import io
import os
import sys
import json
from typing import List, Dict, Tuple, Optional

import streamlit as st
import pandas as pd
from pymilvus import Collection, utility

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

# Factory class imports
from utils.factories.embedding import EmbeddingFactory
from utils.factories.milvus import MilvusFactory

# Service function imports
from utils.services.milvus_service import (
    create_milvus_collection,
    insert_to_milvus,
    get_collection_stats,
    update_milvus_records,
)
# Removed UI component calls as this is a standalone admin tool

# Load configuration file
with open("data/config/collections_config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


def insert_examples_to_milvus(
    examples: List[Dict], collection_config: Dict, db_name: str, overwrite: bool
):
    """Insert examples into Milvus database"""
    milvus_connection = MilvusFactory.create_connection(
        db_name=db_name,
        auto_connect=True
    )

    embeddings = EmbeddingFactory.get_default_embeddings()

    data = []
    vectors = {}

    for example in examples:
        row_data = {}
        for field in collection_config["fields"]:
            if field["name"] != "id":  # Exclude id field
                # Convert based on field type
                if field["type"] == "str":
                    value = str(example[field["name"]])
                elif field["type"] == "int":
                    value = int(example[field["name"]])
                elif field["type"] == "float":
                    value = float(example[field["name"]])
                else:
                    value = example[field["name"]]
                row_data[field["name"]] = value

        data.append(row_data)

        for field_name in collection_config["embedding_fields"]:
            if field_name not in vectors:
                vectors[field_name] = []
            embedding_text = str(example[field_name])
            vector = embeddings.embed_query(embedding_text)
            vectors[field_name].append(vector)

    if not utility.has_collection(collection_config["name"]):
        collection = create_milvus_collection(
            collection_config, len(next(iter(vectors.values()))[0])
        )
    else:
        collection = Collection(collection_config["name"])

    if overwrite:
        update_milvus_records(
            collection, data, vectors, collection_config["embedding_fields"]
        )
    else:
        insert_to_milvus(collection, data, vectors)

    return len(examples)


def process_csv_file(file, collection_config: Dict):
    """Process uploaded CSV file"""
    examples = []
    csv_file = io.StringIO(file.getvalue().decode("utf-8"))
    df = pd.read_csv(csv_file)

    required_columns = [field["name"] for field in collection_config["fields"]]

    # Check if all required columns are present
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"CSVFile missing the following columns: {', '.join(missing_columns)}")

    for _, row in df.iterrows():
        example = {col: row[col] for col in required_columns}
        examples.append(example)

    return examples


def get_existing_records(
    collection_config: Dict, db_name: str
) -> Optional[pd.DataFrame]:
    """Get existing records，Return None if collection does not exist"""
    milvus_factory = MilvusFactory()
    milvus_factory.connect(db_name)
    if not utility.has_collection(collection_config["name"]):
        return None

    collection = milvus_factory.get_collection(collection_config["name"])

    # Get all field names
    field_names = [field["name"] for field in collection_config["fields"]]

    # Query all records
    results = collection.query(expr="id >= 0", output_fields=field_names)

    return pd.DataFrame(results)


def dedup_examples(
    new_examples: List[Dict],
    existing_records: Optional[pd.DataFrame],
    collection_config: Dict,
) -> Tuple[List[Dict], int]:
    """Deduplicate new uploaded data，Based on all fields used for vector generation"""
    if existing_records is None:
        return new_examples, 0

    new_df = pd.DataFrame(new_examples)

    # Ensure column name consistency
    new_df.columns = new_df.columns.str.strip().str.lower()
    if existing_records is not None:
        existing_records.columns = existing_records.columns.str.strip().str.lower()

    # Use all fields for vector generation comparison
    embedding_fields = collection_config["embedding_fields"]

    # Merge using these fields
    merged = pd.merge(
        new_df,
        existing_records,
        on=embedding_fields,
        how="left",
        indicator=True,
        suffixes=("", "_existing"),
    )

    # Find unmatched records（New data）
    new_records = merged[merged["_merge"] == "left_only"]

    # Calculate duplicate record count
    duplicate_count = len(new_examples) - len(new_records)

    # Keep only original columns
    original_columns = new_df.columns
    new_records = new_records[original_columns]

    # Convert back to dictionary list
    new_examples = new_records.to_dict("records")

    return new_examples, duplicate_count


def display_collection_info(collection_config: Dict):
    """DisplayCollectionInformation"""
    with st.container(border=True):
        st.subheader("Collection Information")
        st.write(f"**Name:** {collection_config['name']}")
        st.write(f"**Description:** {collection_config['description']}")
        st.write("**Fields:**")
        for field in collection_config["fields"]:
            st.write(f"- {field['name']}: {field['description']}")


def display_collection_stats(collection_config, selected_db):
    """DisplayCollectionStatisticsInformation"""
    try:
        # Ensure connection exists
        milvus_factory = MilvusFactory()
        milvus_factory.connect(selected_db)
        
        with st.container(border=True):
            st.subheader("Data Statistics")
            if utility.has_collection(collection_config["name"]):
                collection = milvus_factory.get_collection(collection_config["name"])
                stats = get_collection_stats(collection)
                st.write(f"**Entity Count:** {stats['Entity Count']}")
                st.write(f"**FieldsCount:** {stats['FieldsCount']}")
                st.write(f"**Index Type:** {stats['Index Type']}")
            else:
                st.info("ThisCollectionNot yet created")
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")


def display_data_preview(
    new_examples: List[Dict], duplicate_count: int, collection_exists: bool
):
    """Display data preview"""
    with st.container(border=True):
        st.subheader("Data Preview")
        st.write(f"**Total uploaded records:** {len(new_examples) + duplicate_count}")
        if collection_exists:
            st.write(f"**Records already exist in database:** {duplicate_count}")
            st.write(f"**New records to insert:** {len(new_examples)}")
        else:
            st.write("**New records to insert:** All uploaded records（CollectionNot yet created）")

        if len(new_examples) > 0:
            st.write("**New Records Preview:**")
            new_df = pd.DataFrame(new_examples)
            st.dataframe(new_df)
        elif collection_exists:
            st.info("All uploaded records already exist in the database，NoNew dataneed to insert。")


def run_vector_db_management():
    st.title("🗄️ Milvus Database Management")
    st.markdown("---")

    # Display feature introduction
    display_db_management_info()

    # Database Selection
    st.header("Select Database")
    from utils.core.streamlit_config import settings
    db_names = [settings.vector_db.database, "data_cleaning"]
    selected_db = st.selectbox("Select the database to operate on", db_names)

    # Collection Select
    st.header("Select Collection")
    collection_names = list(CONFIG["collections"].keys())
    selected_collection = st.selectbox("Selectto operate onCollection", collection_names)
    collection_config = CONFIG["collections"][selected_collection]

    # Use selected database when connecting to Milvus
    milvus_factory = MilvusFactory()
    milvus_factory.connect(selected_db)

    # DisplayCollectionInformation
    display_collection_info(collection_config)

    # DisplayCollectionStatistics
    display_collection_stats(collection_config, selected_db)

    st.header("Upload and insert data")

    # File Upload
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    # Add option to overwrite duplicate data
    overwrite_option = st.checkbox(
        "Overwrite duplicate data", value=False, help="Check this to update existing records，instead of ignoring them"
    )

    if uploaded_file is not None:
        try:
            examples = process_csv_file(uploaded_file, collection_config)
            st.success(f"Successfully read {len(examples)} records")

            # Get existing records
            existing_records = get_existing_records(collection_config, selected_db)
            collection_exists = existing_records is not None

            # Deduplication
            new_examples, duplicate_count = dedup_examples(
                examples, existing_records, collection_config
            )

            # Display data preview
            display_data_preview(new_examples, duplicate_count, collection_exists)

            if len(new_examples) > 0 or (overwrite_option and duplicate_count > 0):
                if st.button("Insert into Milvus database"):
                    with st.spinner("Inserting data..."):
                        if overwrite_option:
                            inserted_count = insert_examples_to_milvus(
                                examples, collection_config, selected_db, True
                            )
                            st.success(
                                f"Successfully inserted or updated {inserted_count} recordstoMilvusdatabase"
                            )
                        else:
                            inserted_count = insert_examples_to_milvus(
                                new_examples, collection_config, selected_db, False
                            )
                            st.success(
                                f"Successfully inserted {inserted_count} newrecordstoMilvusdatabase"
                            )

        except ValueError as ve:
            st.error(f"CSVFile format error: {str(ve)}")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.error("Please ensure CSV file format is correct，and contains all required columns。")




def display_db_management_info():
    st.info(
        """
    Milvus Database Managementtool for efficient management and updating of vectordatabasedata。
    SupportsCSVFile Upload、Data Previewand batch insertion，facilitating maintenance and expansion of vector datasets。
    """
    )


# If running this file directly，start application
if __name__ == "__main__":
    run_vector_db_management()
