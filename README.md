# QueryBot

🚀 An intelligent query bot powered by LangGraph, featuring natural language to SQL conversion with advanced vector search and multi-database support.

## ✨ Core Features

### 🧠 Intelligent Query Processing
- **Natural Language Understanding**: Convert complex natural language queries into precise SQL statements
- **Intent Analysis**: Intelligently determine query intent clarity and proactively clarify ambiguous requirements
- **Term Standardization**: Automatically map business aliases to standard database fields
- **Context Awareness**: Understand query intent based on conversation history and business context

### 🔄 Intelligent Workflow Engine
- **Graph State Machine Architecture**: 13 specialized processing nodes built on LangGraph
- **Dynamic Routing**: Intelligently decide next steps based on processing results
- **Error Recovery**: Automatic SQL error detection and repair mechanisms
- **Process Visualization**: Complete processing flow tracking and monitoring

### 🛡️ Data Security
- **SQL Injection Protection**: Parameterized queries and input validation
- **Data Access Control**: Database access based on environment configuration
- **Audit Logging**: Complete query history and operation records

### 🔍 Vector Semantic Search
- **Table Structure Understanding**: Vectorized storage of table descriptions and structure information
- **Query Example Matching**: Intelligent SQL generation based on similar queries
- **Term Semantic Search**: Support for fuzzy matching and semantic understanding of term lookup

### 🏗️ Scalable Architecture
- **Modular Design**: Each processing node has single responsibility, easy to maintain and extend
- **Local Development**: Streamlined setup for demo and development environments
- **Multi-Database Support**: Hybrid architecture with MySQL/PostgreSQL primary database + Milvus vector database
- **Monitoring & Tracing**: Full-chain monitoring with integrated Langfuse and Phoenix

## 🏗️ System Architecture

### Core Processing Flow

```mermaid
graph TD
    A([Natural Language Query]) --> B[Intent Analysis]
    B --> C{Intent Clear?}
    C -->|No| D[Clarify Question]
    C -->|Yes| E[Keyword Extraction]
    E --> F[Term Mapping]
    F --> G[Query Rewriting]
    G --> H[Data Source Identification]
    H --> I[Table Structure Analysis]
    I --> J[Feasibility Check]
    J --> K[Query Example Retrieval]
    K --> L[SQL Generation]
    L --> M[Permission Control]
    M --> N[SQL Execution]
    N --> O{Execution Success?}
    O -->|No| P[Error Analysis]
    O -->|Yes| Q[Result Generation]
    P --> R{Repairable?}
    R -->|Yes| N
    R -->|No| S[Return Error]
    Q --> T([Return Result])
    
    %% Enhanced styling for different node types
    classDef inputOutput fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000,font-weight:bold
    classDef nlpProcessing fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef dataProcessing fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef sqlProcessing fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef securityControl fill:#e0f2f1,stroke:#00695c,stroke-width:3px,color:#000,font-weight:bold
    classDef decision fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000,font-style:italic
    classDef errorHandling fill:#fce4ec,stroke:#ad1457,stroke-width:2px,color:#000
    classDef resultOutput fill:#e0f7fa,stroke:#00838f,stroke-width:2px,color:#000
    
    %% Apply enhanced styles to nodes
    class A,T inputOutput
    class B,E,F,G nlpProcessing
    class H,I,J,K dataProcessing
    class L,N sqlProcessing
    class M securityControl
    class C,O,R decision
    class D,P,S errorHandling
    class Q resultOutput
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Layer** | FastAPI + uvicorn | Asynchronous HTTP interface service |
| **Workflow Engine** | LangGraph | Intelligent state machine and process control |
| **AI Framework** | LangChain | LLM invocation and toolchain management |
| **Vector Database** | Milvus | Semantic search and vector storage |
| **Relational Database** | MySQL/PostgreSQL | Business data and permission management |
| **Monitoring & Tracing** | Langfuse/Phoenix | LLM call chain tracing and analysis |

## 📁 Project Structure

```
QueryBot/
├── 📁 backend/                     # 🔧 Backend Services
│   └── sql_assistant/
│       ├── api.py                  # FastAPI application entry
│       ├── async_executor.py       # Asynchronous task executor
│       ├── graph/                  # Workflow graph definitions
│       ├── nodes/                  # 13 processing nodes
│       ├── routes/                 # Conditional routing logic
│       ├── states/                 # State data structures
│       └── utils/                  # Utility functions
├── 📁 data/                        # 💾 Data Directory
│   ├── demo_data_csv/              # Demo data
│   ├── vector_db_csv/              # Vector database metadata
│   ├── config/                     # Configuration files
│   └── temp/                       # Temporary files
├── 📁 tools/                       # 🛠️ Tool Suite
│   ├── setup_demo_environment.py   # Intelligent environment setup wizard
│   ├── data_generation/            # Data generation tools
│   ├── mysql_import/               # MySQL import tools
│   └── vector_db_import/           # Vector database import tools
├── 📁 frontend/                    # 🎨 Frontend Interface (Streamlined QueryBot)
├── 📁 tools/admin/                # 🔧 Admin Tools (Vector database management)
├── 📁 utils/                       # 🔧 Common Utilities
│   ├── core/                     # Infrastructure modules
│   │   ├── config.py             # Unified configuration management
│   │   ├── constants.py          # Global constant definitions
│   │   ├── error_handler.py      # Error handling utilities
│   │   └── logging_config.py     # Logging configuration utilities
│   ├── factories/                # Connection factory modules
│   │   ├── database.py           # Database connection factory
│   │   ├── embedding.py          # Embedding model factory
│   │   └── milvus.py             # Milvus connection factory
│   └── services/                 # Business service modules
│       ├── llm.py                # LLM service wrapper
│       └── milvus_service.py     # Milvus advanced services
├── 📋 pyproject.toml               # Python project configuration and dependencies
├── 🔒 uv.lock                      # Dependency lock file for reproducible builds
└── 🚀 start_local.sh               # QueryBot local development startup script
```

## 🚀 Quick Start

### System Requirements

- **Python**: 3.12+
- **uv**: Fast Python package manager
- **Database**: MySQL 8.0+ or PostgreSQL 12+
- **Vector Database**: Milvus 2.4+ or Zilliz Cloud
- **Memory**: 4GB+
- **Storage**: 5GB+

### 1. Clone the Project

```bash
git clone https://github.com/i-richardwang/QueryBot.git
cd QueryBot
```

### 2. Install uv

```bash
# Install uv on macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or install via pip
pip install uv

# On Windows using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Environment Configuration

```bash
# Copy environment configuration file
cp env.example .env

# Edit configuration file, fill in your API keys and database information
vim .env
```

#### Database Configuration Options

**Option 1: Complete Database URL (Recommended for Cloud Databases)**
```bash
# For Neon PostgreSQL
SQLBOT_DB_URL=postgresql://user:password@host.neon.tech/database?sslmode=require

# For Supabase PostgreSQL
SQLBOT_DB_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres

# For PlanetScale MySQL
SQLBOT_DB_URL=mysql://user:password@host.planetscale.com:3306/database?sslmode=require
```

**Option 2: Individual Parameters (For Local Databases)**
```bash
SQLBOT_DB_TYPE=postgresql
SQLBOT_DB_HOST=localhost
SQLBOT_DB_PORT=5432
SQLBOT_DB_USER=postgres
SQLBOT_DB_PASSWORD=your_password
SQLBOT_DB_NAME=sql_assistant
```

#### Vector Database Configuration Options

**Option 1: Zilliz Cloud (Recommended for Production)**
```bash
# Only need URI and token - much simpler!
VECTOR_DB_URI=https://your-cluster-endpoint.zillizcloud.com:443
VECTOR_DB_TOKEN=your_zilliz_cloud_token
VECTOR_DB_DATABASE=default
```

**Option 2: Local Milvus (For Development)**
```bash
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=19530
VECTOR_DB_DATABASE=default
```

### 4. Install Dependencies

```bash
# Install dependencies using uv
uv sync
```

**Core dependency packages:**
- **AI Framework**: LangChain, LangGraph, Langfuse
- **Web Services**: FastAPI, Uvicorn, Streamlit
- **Databases**: MySQL, Milvus, SQLAlchemy
- **Data Processing**: Pandas, Pydantic
- **Utility Libraries**: Requests, Python-dotenv, PyYAML

### 5. Start QueryBot Service

#### Option 1: Using the Startup Script (Recommended)
```bash
# Use the interactive startup script
./start_local.sh
```

#### Option 2: Manual Startup
```bash
# Start QueryBot API service
uv run uvicorn backend.sql_assistant.api:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Initialize Demo Data

```bash
# Use intelligent setup wizard (recommended)
uv run python tools/setup_demo_environment.py

# Or one-click batch setup
uv run python tools/setup_demo_environment.py --batch
```

### 7. Start Frontend Application

```bash
# Start QueryBot frontend
cd frontend
uv run streamlit run app.py

# Or start admin tools (for developers only)
cd tools/admin
uv run streamlit run admin_app.py
```

### 8. Verify Installation

```bash
# Check configuration
uv run python tools/config_validator.py

# Start services
./start_local.sh
```

Visit these endpoints to verify:
- **QueryBot Frontend**: http://localhost:8501
- **API Service**: http://localhost:8000/health
- **Admin Tools**: http://localhost:8502

## 💻 Usage Examples

### API Call Example

```python
import requests

# Send query request
response = requests.post(
    "http://localhost:8000/api/query-bot",
    json={
        "text": "Query all candidate information for the latest spring recruitment in the Technology R&D Department",
        "username": "demo_user",
        "session_id": "demo_session_001"
    }
)

result = response.json()
print(result["text"])
```

### Supported Query Types

```sql
-- Basic queries
"Query all Java developer candidates"

-- Aggregation statistics
"Count recruitment success rate by department"

-- Time filtering
"Query recruitment activities in the last three months"

-- Complex conditions
"Query candidates with P7+ level and more than 5 years of experience"

-- Join queries
"Query all recruitment activities and candidates where Zhang Wei served as interviewer"
```

## 📊 Intelligent Processing Nodes

QueryBot contains 13 specialized processing nodes:

| Node | Function | Input | Output |
|------|----------|-------|--------|
| **Intent Analysis** | Determine query intent clarity | User query | Intent clarity |
| **Keyword Extraction** | Extract key query information | Standardized query | Keyword list |
| **Term Mapping** | Standardize business terms | Keywords | Standard terms |
| **Query Rewriting** | Normalize query expression | Mapping results | Rewritten query |
| **Data Source Identification** | Identify relevant data tables | Rewritten query | Matched table list |
| **Table Structure Analysis** | Get detailed table information | Table list | Table structure info |
| **Feasibility Check** | Verify query feasibility | Query + structure | Feasibility result |
| **Query Example Retrieval** | Find similar queries | Query intent | Example SQL |
| **SQL Generation** | Generate SQL statements | All context | SQL query |
| **Permission Control** | Inject permission conditions | SQL + user | Secure SQL |
| **SQL Execution** | Execute database queries | Secure SQL | Execution result |
| **Error Analysis** | Analyze and fix errors | Error information | Fix solution |
| **Result Generation** | Format final results | Execution result | User response |

## 🔧 Configuration Guide

### Environment Variable Configuration

| Category | Variable Name | Description | Example |
|----------|---------------|-------------|---------|
| **Basic** | `BASE_HOST` | Service host address | `localhost` |
| **Database** | `SQLBOT_DB_TYPE` | Database type | `mysql` or `postgresql` |
| **Database** | `SQLBOT_DB_*` | Database connection info | `localhost:3306` (MySQL) or `localhost:5432` (PostgreSQL) |
| **Vector DB** | `VECTOR_DB_*` | Milvus connection info | `localhost:19530` |
| **LLM** | `LLM_MODEL` | LLM model name | `Qwen/Qwen2.5-72B-Instruct` |
| **LLM** | `LLM_API_KEY` | LLM API key | `sk-your_api_key` |
| **LLM** | `LLM_API_BASE` | LLM API base URL | `https://api.siliconflow.cn/v1` |
| **Embedding** | `EMBEDDING_API_*` | Vectorization service config | API keys and endpoints |
| **Monitoring** | `LANGFUSE_ENABLED` | Enable tracing | `true/false` |

### Permission Configuration

The system provides flexible permission management with streamlined configuration:

#### Demo Mode (Default)
```bash
# Simplified permission control for demo and development
USER_AUTH_ENABLED=false
```

For advanced use cases, enable role-based access control by setting `USER_AUTH_ENABLED=true`.

## 🛠️ Development Guide

### Adding New Processing Nodes

1. **Create Node File**
```python
# backend/sql_assistant/nodes/new_node.py
def new_processing_node(state: SQLAssistantState) -> dict:
    """New processing node"""
    # Implement processing logic
    return {"new_field": result}
```

2. **Register in Graph**
```python
# backend/sql_assistant/graph/assistant_graph.py
graph_builder.add_node("new_processing", new_processing_node)
graph_builder.add_edge("previous_node", "new_processing")
```

3. **Update State Definition**
```python
# backend/sql_assistant/states/assistant_state.py
class SQLAssistantState(TypedDict):
    # ... existing fields
    new_field: Optional[Any]
```

### Custom Data Generator

```python
# tools/data_generation/custom_generator.py
from tools.data_generation import RecruitmentDataGenerator

class CustomDataGenerator(RecruitmentDataGenerator):
    def generate_custom_data(self, count: int):
        # Implement custom data generation logic
        pass
```

## 🚀 Deployment Guide

### Streamlit Cloud
For easy demo deployment, see `STREAMLIT_DEPLOYMENT_GUIDE.md`

### Running the Application

```bash
# Start QueryBot service
uv run uvicorn backend.sql_assistant.api:app --host 0.0.0.0 --port 8000 --reload

# Start frontend in another terminal
cd frontend
uv run streamlit run app.py
```

### Configuration Options

```bash
# Customize configuration in your .env file
vim .env

# Key configuration areas:
# - Database connection settings
# - LLM API keys and endpoints
# - Vector database configuration
# - Monitoring and tracing options
```

## 🤝 Contributing

We welcome community contributions!

### How to Contribute

1. **Fork the project** and create a feature branch
2. **Submit code** and pass tests
3. **Create Pull Request** and describe changes
4. **Code review** and merge to main branch after approval

### Development Standards

- Follow PEP 8 coding standards
- Add complete type hints
- Write unit tests and documentation
- Use meaningful commit messages

### Reporting Issues

- Use GitHub Issues to report bugs
- Provide detailed reproduction steps
- Include system environment information
- Attach relevant log information

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 📞 Contact Us

- **Project Repository**: https://github.com/i-richardwang/QueryBot
- **Issue Reporting**: https://github.com/i-richardwang/QueryBot/issues

---

⭐ If this project helps you, please give us a star!