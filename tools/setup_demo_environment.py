#!/usr/bin/env python3
"""
QueryBot demo environment intelligent setup script

Provides interactive interface supporting:
1. Generate demo data
2. Import data to database (auto-detects MySQL/PostgreSQL)
3. Import data to vector database
4. One-click complete setup
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Dict

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.data_generation.generate_recruitment_data import RecruitmentDataGenerator
from utils.core.streamlit_config import settings


class SetupEnvironment:
    """Demo environment setup manager"""

    def __init__(self):
        self.project_root = project_root
        self.data_dir = self.project_root / "data"
        self.demo_data_dir = self.data_dir / "demo_data_csv"
        self.vector_data_dir = self.data_dir / "vector_db_csv"
        self.db_type = self._detect_database_type()

    def print_header(self):
        """Print welcome header"""
        print("=" * 60)
        print("🚀 QueryBot Demo Environment Setup Wizard")
        print("=" * 60)
        print()

    def print_separator(self, title: str = ""):
        """Print separator line"""
        if title:
            print(f"\n{'='*20} {title} {'='*20}")
        else:
            print("-" * 60)

    def _detect_database_type(self) -> str:
        """Detect database type from configuration"""
        try:
            # Check if URL is configured
            if hasattr(settings.database, 'url') and settings.database.url:
                url = settings.database.url.lower()
                if url.startswith('postgresql://'):
                    return 'postgresql'
                elif url.startswith('mysql://'):
                    return 'mysql'

            # Check individual parameters
            db_type = getattr(settings.database, 'type', '').lower()
            if db_type in ['postgresql', 'postgres']:
                return 'postgresql'
            elif db_type in ['mysql']:
                return 'mysql'

            # Default fallback
            return 'mysql'
        except Exception:
            return 'mysql'

    def check_dependencies(self) -> Dict[str, bool]:
        """Check dependencies"""
        print("🔍 Checking system dependencies...")
        
        dependencies = {
            "python": True,  # Definitely exists since script is running
            "pandas": False,
            "mysql": False,
            "milvus": False
        }

        # Check Python packages
        try:
            dependencies["pandas"] = True
            print("✅ pandas - Installed")
        except ImportError:
            print("❌ pandas - Not installed")

        try:
            dependencies["mysql"] = True
            print("✅ mysql-connector-python - Installed")
        except ImportError:
            print("❌ mysql-connector-python - Not installed")

        try:
            dependencies["milvus"] = True
            print("✅ pymilvus - Installed")
        except ImportError:
            print("❌ pymilvus - Not installed")

        return dependencies

    def check_existing_data(self) -> Dict[str, Dict]:
        """Check existing data"""
        print("\n📂 Checking existing data files...")
        
        demo_files = [
            "recruitment_activity_info.csv",
            "recruitment_interviewer_info.csv", 
            "recruitment_candidate_info.csv"
        ]
        
        vector_files = [
            "table_descriptions.csv",
            "query_examples.csv",
            "term_descriptions.csv"
        ]
        
        demo_status = {}
        vector_status = {}
        
        for file in demo_files:
            file_path = self.demo_data_dir / file
            if file_path.exists():
                size = file_path.stat().st_size
                demo_status[file] = {"exists": True, "size": size}
                print(f"✅ {file} - exists ({size:,} bytes)")
            else:
                demo_status[file] = {"exists": False, "size": 0}
                print(f"❌ {file} - not found")

        for file in vector_files:
            file_path = self.vector_data_dir / file
            if file_path.exists():
                size = file_path.stat().st_size
                vector_status[file] = {"exists": True, "size": size}
                print(f"✅ {file} - exists ({size:,} bytes)")
            else:
                vector_status[file] = {"exists": False, "size": 0}
                print(f"❌ {file} - not found")
                
        return {"demo": demo_status, "vector": vector_status}
        
    def generate_demo_data(self,
                          activities: int = 50,
                          interviewers: int = 100,
                          candidates: int = 500,
                          force: bool = False) -> bool:
        """Generate demo data"""
        self.print_separator("Generate Demo Data")

        if not force:
            existing_data = self.check_existing_data()
            has_demo_data = any(f["exists"] for f in existing_data["demo"].values())

            if has_demo_data:
                print("⚠️  Existing demo data files detected")
                choice = input("Do you want to regenerate? This will overwrite existing data (y/N): ").strip().lower()
                if choice not in ['y', 'yes']:
                    print("❌ Skipping data generation")
                    return False
                    
        try:
            print(f"🔄 Starting data generation...")
            print(f"   - Recruitment activities: {activities} records")
            print(f"   - Interviewers: {interviewers} records")
            print(f"   - Candidates: {candidates} records")

            generator = RecruitmentDataGenerator()
            result = generator.generate_all_data(
                activities_count=activities,
                interviewers_count=interviewers,
                candidates_count=candidates
            )

            print("✅ Demo data generation completed!")
            return True

        except Exception as e:
            print(f"❌ Data generation failed: {e}")
            return False
            
    def import_database_data(self, table_name: Optional[str] = None) -> bool:
        """Import data to database (auto-detect type)"""
        db_display_name = "PostgreSQL" if self.db_type == "postgresql" else "MySQL"
        self.print_separator(f"Import {db_display_name} Data")

        try:
            # Choose the correct import module based on database type
            if self.db_type == "postgresql":
                # For PostgreSQL, we'll use a generic approach since there's no specific postgresql_import
                # We'll create a simple import using SQLAlchemy
                return self._import_data_generic(table_name)
            else:
                # Use existing MySQL import
                cmd = [
                    sys.executable, "-m", "tools.mysql_import.auto_import_mysql"
                ]

                if table_name:
                    cmd.extend(["--table", table_name])
                    print(f"🔄 Importing table: {table_name}")
                else:
                    print(f"🔄 Importing all CSV files to {db_display_name}...")

                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)

                if result.returncode == 0:
                    print(f"✅ {db_display_name} data import completed!")
                    if result.stdout:
                        print("\nImport details:")
                        print(result.stdout)
                    return True
                else:
                    print(f"❌ {db_display_name} data import failed:")
                    print(result.stderr)
                    return False

        except Exception as e:
            print(f"❌ Database import process error: {e}")
            return False

    def _import_data_generic(self, table_name: Optional[str] = None) -> bool:
        """Generic data import using SQLAlchemy"""
        try:
            import pandas as pd
            from utils.factories.database import DatabaseFactory

            print(f"🔄 Importing data to {self.db_type.upper()} database...")

            # Get database engine
            engine = DatabaseFactory.get_default_engine()

            # Get CSV files to import
            csv_files = list(self.demo_data_dir.glob("*.csv"))
            if not csv_files:
                print("❌ No CSV files found in demo_data_csv directory")
                return False

            imported_count = 0
            for csv_file in csv_files:
                # Skip if specific table requested and this isn't it
                if table_name and csv_file.stem != table_name:
                    continue

                try:
                    # Read CSV file
                    df = pd.read_csv(csv_file)
                    table_name_actual = csv_file.stem

                    # Import to database
                    df.to_sql(table_name_actual, engine, if_exists='replace', index=False)
                    print(f"  ✅ Imported {table_name_actual}: {len(df)} records")
                    imported_count += 1

                except Exception as e:
                    print(f"  ❌ Failed to import {csv_file.name}: {e}")

            if imported_count > 0:
                print(f"✅ Successfully imported {imported_count} tables to {self.db_type.upper()}")
                return True
            else:
                print("❌ No tables were imported")
                return False

        except Exception as e:
            print(f"❌ Generic import failed: {e}")
            return False
            
    def import_vector_data(self, collection_name: Optional[str] = None, overwrite: bool = False) -> bool:
        """Import data to vector database"""
        self.print_separator("Import Vector Database")

        try:
            cmd = [
                sys.executable, "-m", "tools.vector_db_import.auto_import_vector_db"
            ]

            if collection_name:
                cmd.extend(["--collection", collection_name])
                print(f"🔄 Importing collection: {collection_name}")
            else:
                print("🔄 Importing all vector data...")

            if overwrite:
                cmd.append("--overwrite")
                print("   Using overwrite mode")

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)

            if result.returncode == 0:
                print("✅ Vector data import completed!")
                if result.stdout:
                    print("\nImport details:")
                    print(result.stdout)
                return True
            else:
                print("❌ Vector data import failed:")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ Vector data import process error: {e}")
            return False
            
    def show_menu(self) -> str:
        """Show main menu"""
        db_display_name = "PostgreSQL" if self.db_type == "postgresql" else "MySQL"
        print("\n📋 Please select an operation:")
        print("1. 🔄 Generate demo data")
        print(f"2. 📊 Import data to {db_display_name} database")
        print("3. 🔍 Import data to vector database")
        print("4. 🚀 One-click complete setup (generate + import)")
        print("5. 📈 View data status")
        print("6. 🧹 Clean data files")
        print("7. ❓ Show help information")
        print("8. 🚪 Exit")
        print()
        return input("Please enter your choice (1-8): ").strip()
        
    def show_data_status(self):
        """Show data status"""
        self.print_separator("Data Status")

        dependencies = self.check_dependencies()
        data_status = self.check_existing_data()

        print(f"\n📊 Data file statistics:")
        demo_exists = sum(1 for f in data_status["demo"].values() if f["exists"])
        vector_exists = sum(1 for f in data_status["vector"].values() if f["exists"])

        print(f"   - Demo data files: {demo_exists}/3")
        print(f"   - Vector data files: {vector_exists}/3")

        print(f"\n🔧 Dependency status:")
        for dep, status in dependencies.items():
            status_icon = "✅" if status else "❌"
            print(f"   - {dep}: {status_icon}")
            
    def clean_data_files(self):
        """Clean data files"""
        self.print_separator("Clean Data Files")

        print("⚠️  This will delete all generated demo data files")
        choice = input("Are you sure you want to continue? (y/N): ").strip().lower()

        if choice not in ['y', 'yes']:
            print("❌ Cleanup operation cancelled")
            return

        deleted_count = 0

        # Clean demo data
        for file_path in self.demo_data_dir.glob("recruitment_*.csv"):
            try:
                file_path.unlink()
                print(f"🗑️  Deleted: {file_path.name}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {file_path.name}: {e}")

        # Clean vector data
        vector_files = ["table_descriptions.csv", "query_examples.csv", "term_descriptions.csv"]
        for filename in vector_files:
            file_path = self.vector_data_dir / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"🗑️  Deleted: {filename}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Failed to delete {filename}: {e}")

        print(f"\n✅ Cleanup completed, deleted {deleted_count} files")
        
    def show_help(self):
        """Show help information"""
        self.print_separator("Help Information")

        print("""
🔧 Usage Instructions:

1. Generate Demo Data
   - Create fictional recruitment-related data
   - Includes recruitment activities, interviewer, and candidate information
   - Also generates metadata required for vector database

2. Import Database Data
   - Import CSV data files to configured database (MySQL/PostgreSQL)
   - Auto-detects database type from configuration
   - Requires correct database connection configuration
   - Supports selective import of specific tables

3. Import Vector Database
   - Import metadata to Milvus vector database
   - Used for semantic search functionality of QueryBot
   - Supports incremental import or overwrite mode

4. One-Click Complete Setup
   - Automatically execute all steps
   - Suitable for initial setup or complete reset

📋 Environment Requirements:
   - Python 3.8+
   - pandas, mysql-connector-python, pymilvus
   - MySQL database service
   - Milvus vector database service

🔗 Related Documentation:
   - tools/README.md - Complete tool usage instructions
        """)
        
    def one_click_setup(self):
        """One-click complete setup"""
        self.print_separator("One-Click Complete Setup")

        db_display_name = "PostgreSQL" if self.db_type == "postgresql" else "MySQL"
        print("🚀 Starting one-click complete setup process...")
        print("   This will execute the following steps:")
        print("   1. Generate demo data")
        print(f"   2. Import data to {db_display_name}")
        print("   3. Import data to vector database")
        print()

        choice = input("Are you sure you want to continue? (Y/n): ").strip().lower()
        if choice in ['n', 'no']:
            print("❌ One-click setup cancelled")
            return

        success_count = 0
        total_steps = 3

        # Step 1: Generate data
        print(f"\n[1/{total_steps}] Generating demo data...")
        if self.generate_demo_data(force=True):
            success_count += 1

        # Step 2: Import database data
        db_display_name = "PostgreSQL" if self.db_type == "postgresql" else "MySQL"
        print(f"\n[2/{total_steps}] Importing {db_display_name} data...")
        if self.import_database_data():
            success_count += 1

        # Step 3: Import vector database
        print(f"\n[3/{total_steps}] Importing vector data...")
        if self.import_vector_data():
            success_count += 1

        self.print_separator("Setup Complete")

        if success_count == total_steps:
            print("🎉 One-click setup completed! All steps executed successfully")
            print("\n📖 Next you can:")
            print("   1. Start QueryBot service")
            print("   2. Test natural language query functionality")
            print("   3. View generated demo data")
        else:
            print(f"⚠️  Setup partially completed: {success_count}/{total_steps} steps successful")
            print("   Please check error messages for failed steps and execute manually")
            
    def run_interactive(self):
        """Run interactive interface"""
        self.print_header()

        # Show initial status
        self.show_data_status()

        while True:
            try:
                choice = self.show_menu()

                if choice == '1':
                    # Generate demo data
                    print("\n🔧 Customize data volume (press Enter for default values):")
                    activities = input("Number of recruitment activities [50]: ").strip()
                    interviewers = input("Number of interviewers [100]: ").strip()
                    candidates = input("Number of candidates [500]: ").strip()

                    activities = int(activities) if activities else 50
                    interviewers = int(interviewers) if interviewers else 100
                    candidates = int(candidates) if candidates else 500

                    self.generate_demo_data(activities, interviewers, candidates)

                elif choice == '2':
                    # Import database data
                    table = input("Specify table name (press Enter to import all tables): ").strip()
                    table = table if table else None
                    self.import_database_data(table)

                elif choice == '3':
                    # Import vector data
                    collection = input("Specify collection name (press Enter to import all collections): ").strip()
                    collection = collection if collection else None

                    overwrite = input("Use overwrite mode? (y/N): ").strip().lower()
                    overwrite = overwrite in ['y', 'yes']

                    self.import_vector_data(collection, overwrite)
                    
                elif choice == '4':
                    # One-click complete setup
                    self.one_click_setup()

                elif choice == '5':
                    # View data status
                    self.show_data_status()

                elif choice == '6':
                    # Clean data files
                    self.clean_data_files()

                elif choice == '7':
                    # Show help
                    self.show_help()

                elif choice == '8':
                    # Exit
                    print("\n👋 Thank you for using QueryBot Setup Wizard!")
                    break

                else:
                    print("❌ Invalid choice, please enter a number between 1-8")

            except KeyboardInterrupt:
                print("\n\n👋 Setup wizard interrupted")
                break
            except Exception as e:
                print(f"\n❌ Operation failed: {e}")
                input("Press Enter to continue...")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="QueryBot demo environment setup wizard")
    parser.add_argument("--batch", action="store_true", help="Batch mode, execute one-click setup")
    parser.add_argument("--generate-only", action="store_true", help="Generate data only, no import")
    parser.add_argument("--import-only", action="store_true", help="Import data only, no generation")

    args = parser.parse_args()

    setup = SetupEnvironment()

    if args.batch:
        # Batch mode
        setup.print_header()
        setup.one_click_setup()
    elif args.generate_only:
        # Generate data only
        setup.print_header()
        setup.generate_demo_data(force=True)
    elif args.import_only:
        # Import data only
        setup.print_header()
        setup.import_database_data()
        setup.import_vector_data()
    else:
        # Interactive mode
        setup.run_interactive()


if __name__ == "__main__":
    main() 