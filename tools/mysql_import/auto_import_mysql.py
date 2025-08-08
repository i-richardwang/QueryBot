import os
import sys
import argparse
import pandas as pd
from glob import glob
from pathlib import Path
import mysql.connector
from mysql.connector import Error

# Add project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

# Factory class imports
from utils.factories.database import DatabaseFactory

# Core infrastructure imports
from utils.core.streamlit_config import settings


def connect_to_mysql():
    """Connect to MySQL database"""
    try:
        # Get database connection information
        db_config = settings.database
        host = db_config.host
        port = db_config.port
        user = db_config.user
        password = db_config.password
        database = db_config.name

        print(f"Connecting to MySQL database: {host}:{port}/{database}")

        # Create connection
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection

    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None


def get_sqlalchemy_engine():
    """Get SQLAlchemy engine for pandas data import"""
    return DatabaseFactory.get_default_engine()


def process_csv_file(file_path, connection, overwrite=True):
    """Process single CSV file and import to MySQL"""
    try:
        # Get table name (use filename as table name)
        table_name = Path(file_path).stem
        print(f"\nProcessing file: {file_path}")
        print(f"Target table: {table_name}")

        # Read CSV file
        df = pd.read_csv(file_path)
        print(f"Read {len(df)} rows of data")

        # Print CSV file column names and first few rows
        print(f"Columns: {', '.join(df.columns)}")

        # Get SQLAlchemy engine
        engine = get_sqlalchemy_engine()

        # If table exists and needs to be overwritten, drop table first
        if overwrite:
            cursor = connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            connection.commit()
            print(f"Dropped existing table {table_name} (if exists)")

        # Use pandas to_sql method to create table and import data
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='replace',
            index=False,
            chunksize=1000
        )

        print(f"Successfully imported {len(df)} rows to table {table_name}")
        return True

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Automatically import CSV files to MySQL database")
    parser.add_argument("--table", type=str, help="Only process specified table, if not specified processes all CSV files")
    args = parser.parse_args()

    # Configuration is automatically loaded on import

    # Connect to MySQL database
    connection = connect_to_mysql()
    if not connection:
        print("Unable to connect to MySQL database, import process terminated")
        return

    try:
        # Get CSV file list
        csv_dir = os.path.join(project_root, "data", "demo_data_csv")
        csv_files = glob(os.path.join(csv_dir, "*.csv"))

        print(f"Found {len(csv_files)} CSV files")

        # Process CSV files
        success_count = 0
        for csv_file in csv_files:
            file_name = Path(csv_file).stem

            # If table name is specified, only process that table
            if args.table and file_name != args.table:
                continue

            if process_csv_file(csv_file, connection):
                success_count += 1

        print(f"\nImport completed, successfully imported {success_count}/{len(csv_files)} files")
        
    except Exception as e:
        print(f"Error during import process: {e}")

    finally:
        # Close database connection
        if connection and connection.is_connected():
            connection.close()
            print("MySQL database connection closed")


if __name__ == "__main__":
    main() 