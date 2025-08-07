# Tools Collection

Tool collection for QueryBot project, including data generation, data import, environment setup and other utilities.

## Directory Structure

```
tools/
├── README.md                       # 🔗 Unified documentation for tool collection
├── setup_demo_environment.py       # 🚀 Intelligent demo environment setup wizard
├── data_generation/                # 📊 Data generation tools
│   ├── __init__.py
│   └── generate_recruitment_data.py
├── mysql_import/                   # 🗄️ MySQL data import tools
│   ├── __init__.py
│   └── auto_import_mysql.py
└── vector_db_import/               # 🔍 Vector database import tools
    ├── __init__.py
    └── auto_import_vector_db.py
```

## 🚀 Quick Start

### Recommended: Intelligent Setup Wizard

```bash
# Interactive setup (recommended)
uv run python tools/setup_demo_environment.py

# One-click batch setup
uv run python tools/setup_demo_environment.py --batch

# Generate data only
uv run python tools/setup_demo_environment.py --generate-only

# Import data only
uv run python tools/setup_demo_environment.py --import-only
```

The intelligent setup wizard provides:
- 🔍 Dependency checking and environment validation
- 📊 Data status display
- 🎯 Interactive operation selection
- 🚀 One-click complete setup
- 🧹 Data file cleanup
- ❓ Detailed help information

## 📊 Tool Module Description

### 1. Data Generation Tools (`data_generation/`)

**Function**: Generate fictional demo data

**Core Class**: `RecruitmentDataGenerator`

**Generated Content**:
- Recruitment activity information (50 records)
- Interviewer information (100 records)
- Candidate information (500 records)
- Table description metadata
- Query examples
- Term definitions

**Usage**:
```bash
# Use as module
uv run python -m tools.data_generation.generate_recruitment_data

# Custom data volume
uv run python -m tools.data_generation.generate_recruitment_data \
    --activities 30 --interviewers 80 --candidates 300
```

### 2. MySQL Import Tools (`mysql_import/`)

**Function**: Automatically import CSV files to MySQL database

**Features**:
- Automatically scan `data/demo_data_csv/` directory
- Use filename as table name
- Support full overwrite and selective import
- Automatically create table structure

**Usage**:
```bash
# Import all tables
uv run python -m tools.mysql_import.auto_import_mysql

# Import specific table
uv run python -m tools.mysql_import.auto_import_mysql --table recruitment_candidate_info
```

### 3. Vector Database Import Tools (`vector_db_import/`)

**Function**: Import metadata to Milvus vector database

**Features**:
- Automatically scan `data/vector_db_csv/` directory
- Match data according to collection configuration files
- Support incremental import and overwrite mode
- Automatic deduplication processing

**Usage**:
```bash
# Import all collections
uv run python -m tools.vector_db_import.auto_import_vector_db

# Import specific collection (overwrite mode)
uv run python -m tools.vector_db_import.auto_import_vector_db \
    --collection query_examples --overwrite
```

## 🔧 Environment Requirements

### Python Dependencies

```bash
uv add pandas mysql-connector-python sqlalchemy pymilvus
```

### Service Dependencies

- **MySQL Database**: Store business data
- **Milvus Vector Database**: Store vectorized metadata
- **Environment Variable Configuration**: Database connection information

### Environment Variables

Configure the following variables in `.env` file:

```env
# MySQL Configuration
SQLBOT_DB_HOST=localhost
SQLBOT_DB_PORT=3306
SQLBOT_DB_USER=root
SQLBOT_DB_PASSWORD=your_password
SQLBOT_DB_NAME=your_database

# Milvus Configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Other Configuration
EMBEDDING_API_KEY=your_api_key
EMBEDDING_API_BASE=your_api_base
EMBEDDING_MODEL=your_model
```

## 📋 Usage Scenarios

### Scenario 1: Initial Project Setup
```bash
# Use intelligent wizard for one-click setup
uv run python tools/setup_demo_environment.py --batch
```

### Scenario 2: Development Testing
```bash
# Generate new test data only
uv run python tools/setup_demo_environment.py --generate-only

# Re-import specific table
uv run python -m tools.mysql_import.auto_import_mysql --table recruitment_activity_info
```

### Scenario 3: Data Update
```bash
# Update vector database (overwrite mode)
uv run python -m tools.vector_db_import.auto_import_vector_db --overwrite
```

### Scenario 4: Troubleshooting
```bash
# Start interactive wizard to check status
uv run python tools/setup_demo_environment.py
# Select "5. 📈 View Data Status"
```

## 🎯 Best Practices

### 1. Development Environment Setup
- Use intelligent wizard for initial setup
- Regularly use status check function to verify environment
- Adjust data volume size as needed

### 2. Data Management
- Backup existing data before production use
- Use cleanup function to regularly clean test data
- Import by module for precise control

### 3. Troubleshooting
- Prioritize checking dependency status
- View detailed error logs
- Use selective import to locate issues

## 💡 Design Philosophy

- **Simple and Easy**: Provide interactive wizard to lower usage threshold
- **Modular**: Independent functions, can be used separately or in combination
- **Intelligent**: Automatically detect environment and provide status feedback
- **Extensible**: Easy to add new data generators and import tools

## 🤝 Contribution Guide

### Adding New Tools

1. Create new subdirectory under `tools/`
2. Follow existing module structure (`__init__.py`, main script)
3. Update this README documentation with usage instructions
4. Integrate into intelligent setup wizard if needed

### Code Standards

- Use type hints
- Add detailed docstrings
- Follow PEP 8 coding style
- Include error handling and logging