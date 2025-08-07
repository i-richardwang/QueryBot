import os
import sys
import json
import pandas as pd
import argparse
from glob import glob
from pathlib import Path

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
    update_milvus_records,
)

# Core infrastructure imports
from utils.core.config import settings

from pymilvus import Collection, utility


def load_config():
    """Load collection configuration file"""
    config_path = os.path.join(project_root, "data/config/collections_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_csv_file(file_path, collection_config):
    """Process CSV file and return data list"""
    print(f"Processing file: {file_path}")

    try:
        df = pd.read_csv(file_path)

        required_columns = [field["name"] for field in collection_config["fields"]]

        # Check if all required columns are present
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            print(f"Error: CSV file missing the following columns: {', '.join(missing_columns)}")
            return None
        
        examples = []
        for _, row in df.iterrows():
            example = {col: row[col] for col in required_columns}
            examples.append(example)
            
        print(f"Read {len(examples)} records from CSV file")
        return examples

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None


def get_existing_records(collection_config, db_name):
    """Get existing records, return None if collection doesn't exist"""
    milvus_connection = MilvusFactory.create_connection(
        db_name=db_name,
        auto_connect=True
    )
    if not utility.has_collection(collection_config["name"]):
        return None

    collection = milvus_connection.get_collection(collection_config["name"])

    # Get all field names
    field_names = [field["name"] for field in collection_config["fields"]]

    # Query all records
    results = collection.query(expr="id >= 0", output_fields=field_names)

    return pd.DataFrame(results)


def dedup_examples(new_examples, existing_records, collection_config):
    """Deduplicate new uploaded data based on all fields used for vector generation"""
    if existing_records is None:
        return new_examples, 0

    new_df = pd.DataFrame(new_examples)

    # Ensure column name consistency
    new_df.columns = new_df.columns.str.strip().str.lower()
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

    # Find unmatched records (new data)
    new_records = merged[merged["_merge"] == "left_only"]

    # Calculate duplicate record count
    duplicate_count = len(new_examples) - len(new_records)

    # Keep only original columns
    original_columns = new_df.columns
    new_records = new_records[original_columns]

    # Convert back to dictionary list
    new_examples = new_records.to_dict("records")

    return new_examples, duplicate_count


def insert_examples_to_milvus(examples, collection_config, db_name, overwrite):
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


def process_collection(csv_file, collection_config, db_name, overwrite=False):
    """Process data import for single collection"""
    collection_name = collection_config["name"]
    print(f"\nStarting to process collection: {collection_name}")

    # Process CSV file
    examples = process_csv_file(csv_file, collection_config)
    if examples is None:
        print(f"Skipping processing for collection {collection_name}")
        return

    # Get existing records
    existing_records = get_existing_records(collection_config, db_name)
    collection_exists = existing_records is not None

    # Deduplicate
    new_examples, duplicate_count = dedup_examples(examples, existing_records, collection_config)

    # Display data statistics
    total_count = len(examples)
    print(f"Total uploaded records: {total_count}")
    if collection_exists:
        print(f"Records already exist in database: {duplicate_count}")
        print(f"New records to insert: {len(new_examples)}")
    else:
        print("New records to insert: All uploaded records (Collection not yet created)")

    # Insert data
    if len(new_examples) > 0 or (overwrite and duplicate_count > 0):
        try:
            if overwrite:
                print("Using overwrite mode, will update existing records")
                inserted_count = insert_examples_to_milvus(examples, collection_config, db_name, True)
                print(f"Successfully inserted or updated {inserted_count} records to Milvus database")
            else:
                print("Using incremental mode, will only insert new records")
                inserted_count = insert_examples_to_milvus(new_examples, collection_config, db_name, False)
                print(f"Successfully inserted {inserted_count} new records to Milvus database")
        except Exception as e:
            print(f"Error inserting data: {str(e)}")
    else:
        print("No new data to insert")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Auto import CSV files to Milvus vector database")
    parser.add_argument("--db", type=str, help="Database name to use, defaults to environment variable configuration")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing records")
    parser.add_argument("--collection", type=str, help="Process only specified collection, if not specified, process all matching collections")
    args = parser.parse_args()

    # Configuration is automatically loaded on import

    # Set database name
    if args.db:
        db_name = args.db
    else:
        # settings already imported at file beginning
        db_name = settings.vector_db.database
    print(f"Using database: {db_name}")

    # Load configuration
    config = load_config()
    collections_config = config["collections"]

    # Get CSV file list
    csv_dir = os.path.join(project_root, "data", "vector_db_csv")
    csv_files = glob(os.path.join(csv_dir, "*.csv"))

    print(f"Found {len(csv_files)} CSV files")

    # Match files with collection configuration based on filename
    for csv_file in csv_files:
        file_name = Path(csv_file).stem

        # If specific collection is specified, only process that collection
        if args.collection and file_name != args.collection:
            continue

        # Check if filename matches collection name
        if file_name in collections_config:
            collection_config = collections_config[file_name]
            process_collection(csv_file, collection_config, db_name, args.overwrite)
        else:
            print(f"Ignoring file {csv_file}, no matching collection configuration found")

    print("\nAll import tasks completed")


if __name__ == "__main__":
    main() 