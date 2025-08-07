# QueryBot

🚀 基于LangGraph构建的智能查询机器人，具备自然语言转SQL、高级向量搜索和多数据库支持能力。

## ✨ 核心特性

### 🧠 智能查询处理
- **自然语言理解**：将复杂的自然语言查询转换为精确的SQL语句
- **意图分析**：智能判断查询意图的清晰度，主动澄清模糊的需求
- **术语标准化**：自动映射业务别名到标准数据库字段
- **上下文感知**：基于对话历史和业务上下文理解查询意图

### 🔄 智能工作流引擎
- **图状态机架构**：基于LangGraph构建的13个专业化处理节点
- **动态路由**：根据处理结果智能决定下一步操作
- **错误恢复**：自动SQL错误检测和修复机制
- **过程可视化**：完整的处理流程跟踪和监控

### 🛡️ 数据安全
- **SQL注入防护**：参数化查询和输入验证
- **数据访问控制**：基于环境配置的数据库访问权限
- **审计日志**：完整的查询历史和操作记录

### 🔍 向量语义搜索
- **表结构理解**：表描述和结构信息的向量化存储
- **查询示例匹配**：基于相似查询的智能SQL生成
- **术语语义搜索**：支持模糊匹配和术语查找的语义理解

### 🏗️ 可扩展架构
- **模块化设计**：每个处理节点职责单一，便于维护和扩展
- **本地开发友好**：为演示和开发环境提供简化配置
- **多数据库支持**：MySQL/PostgreSQL主数据库 + Milvus向量数据库的混合架构
- **监控与追踪**：集成Langfuse和Phoenix的全链路监控

## 🏗️ 系统架构

### 核心处理流程

```mermaid
graph TD
    A([自然语言查询]) --> B[意图分析]
    B --> C{意图清晰?}
    C -->|否| D[澄清问题]
    C -->|是| E[关键词提取]
    E --> F[术语映射]
    F --> G[查询重写]
    G --> H[数据源识别]
    H --> I[表结构分析]
    I --> J[可行性检查]
    J --> K[查询示例检索]
    K --> L[SQL生成]
    L --> M[权限控制]
    M --> N[SQL执行]
    N --> O{执行成功?}
    O -->|否| P[错误分析]
    O -->|是| Q[结果生成]
    P --> R{可修复?}
    R -->|是| N
    R -->|否| S[返回错误]
    Q --> T([返回结果])
    
    %% 不同节点类型的增强样式
    classDef inputOutput fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000,font-weight:bold
    classDef nlpProcessing fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef dataProcessing fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef sqlProcessing fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef securityControl fill:#e0f2f1,stroke:#00695c,stroke-width:3px,color:#000,font-weight:bold
    classDef decision fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000,font-style:italic
    classDef errorHandling fill:#fce4ec,stroke:#ad1457,stroke-width:2px,color:#000
    classDef resultOutput fill:#e0f7fa,stroke:#00838f,stroke-width:2px,color:#000
    
    %% 为节点应用增强样式
    class A,T inputOutput
    class B,E,F,G nlpProcessing
    class H,I,J,K dataProcessing
    class L,N sqlProcessing
    class M securityControl
    class C,O,R decision
    class D,P,S errorHandling
    class Q resultOutput
```

### 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **API层** | FastAPI + uvicorn | 异步HTTP接口服务 |
| **工作流引擎** | LangGraph | 智能状态机和过程控制 |
| **AI框架** | LangChain | LLM调用和工具链管理 |
| **向量数据库** | Milvus | 语义搜索和向量存储 |
| **关系数据库** | MySQL/PostgreSQL | 业务数据和权限管理 |
| **监控与追踪** | Langfuse/Phoenix | LLM调用链追踪和分析 |

## 📁 项目结构

```
QueryBot/
├── 📁 backend/                     # 🔧 后端服务
│   └── sql_assistant/
│       ├── api.py                  # FastAPI应用入口
│       ├── async_executor.py       # 异步任务执行器
│       ├── graph/                  # 工作流图定义
│       ├── nodes/                  # 13个处理节点
│       ├── routes/                 # 条件路由逻辑
│       ├── states/                 # 状态数据结构
│       └── utils/                  # 实用工具函数
├── 📁 data/                        # 💾 数据目录
│   ├── demo_data_csv/              # 演示数据
│   ├── vector_db_csv/              # 向量数据库元数据
│   ├── config/                     # 配置文件
│   └── temp/                       # 临时文件
├── 📁 tools/                       # 🛠️ 工具套件
│   ├── setup_demo_environment.py   # 智能环境设置向导
│   ├── data_generation/            # 数据生成工具
│   ├── mysql_import/               # MySQL导入工具
│   └── vector_db_import/           # 向量数据库导入工具
├── 📁 frontend/                    # 🎨 前端界面
├── 📁 tools/admin/                # 🔧 管理工具（向量数据库管理）
├── 📁 utils/                       # 🔧 通用工具
│   ├── core/                     # 基础设施模块
│   │   ├── config.py             # 统一配置管理
│   │   ├── constants.py          # 全局常量定义
│   │   ├── error_handler.py      # 错误处理工具
│   │   └── logging_config.py     # 日志配置工具
│   ├── factories/                # 连接工厂模块
│   │   ├── database.py           # 数据库连接工厂
│   │   ├── embedding.py          # 嵌入模型工厂
│   │   └── milvus.py             # Milvus连接工厂
│   └── services/                 # 业务服务模块
│       ├── llm.py                # LLM服务封装
│       └── milvus_service.py     # Milvus高级服务
├── 📋 pyproject.toml               # Python项目配置和依赖
├── 🔒 uv.lock                      # 依赖锁定文件，确保可重现构建
└── 🚀 start_local.sh               # QueryBot本地开发启动脚本
```

## 🚀 快速开始

### 系统要求

- **Python**：3.12+
- **uv**：快速Python包管理器
- **数据库**：MySQL 8.0+ 或 PostgreSQL 12+
- **向量数据库**：Milvus 2.4+ 或 Zilliz Cloud
- **内存**：4GB+
- **存储**：5GB+

### 1. 克隆项目

```bash
git clone https://github.com/i-richardwang/QueryBot.git
cd QueryBot
```

### 2. 安装uv

```bash
# 在 macOS/Linux 上安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或通过pip安装
pip install uv

# 在Windows上使用PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. 环境配置

```bash
# 复制环境配置文件
cp env.example .env

# 编辑配置文件，填写您的API密钥和数据库信息
vim .env
```

#### 数据库配置选项

**选项1：完整数据库URL（推荐用于云数据库）**
```bash
# Neon PostgreSQL
SQLBOT_DB_URL=postgresql://user:password@host.neon.tech/database?sslmode=require

# Supabase PostgreSQL
SQLBOT_DB_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres

# PlanetScale MySQL
SQLBOT_DB_URL=mysql://user:password@host.planetscale.com:3306/database?sslmode=require
```

**选项2：独立参数（适用于本地数据库）**
```bash
SQLBOT_DB_TYPE=postgresql
SQLBOT_DB_HOST=localhost
SQLBOT_DB_PORT=5432
SQLBOT_DB_USER=postgres
SQLBOT_DB_PASSWORD=your_password
SQLBOT_DB_NAME=sql_assistant
```

#### 向量数据库配置选项

**选项1：Zilliz Cloud（推荐用于生产环境）**
```bash
# 只需要URI和令牌，更加简单！
VECTOR_DB_URI=https://your-cluster-endpoint.zillizcloud.com:443
VECTOR_DB_TOKEN=your_zilliz_cloud_token
VECTOR_DB_DATABASE=default
```

**选项2：本地Milvus（适用于开发环境）**
```bash
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=19530
VECTOR_DB_DATABASE=default
```

### 4. 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

**核心依赖包：**
- **AI框架**：LangChain, LangGraph, Langfuse
- **Web服务**：FastAPI, Uvicorn, Streamlit
- **数据库**：MySQL, Milvus, SQLAlchemy
- **数据处理**：Pandas, Pydantic
- **工具库**：Requests, Python-dotenv, PyYAML

### 5. 启动QueryBot服务

#### 选项1：使用启动脚本（推荐）
```bash
# 使用交互式启动脚本
./start_local.sh
```

#### 选项2：手动启动
```bash
# 启动QueryBot API服务
uv run uvicorn backend.sql_assistant.api:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 初始化演示数据

```bash
# 使用智能设置向导（推荐）
uv run python tools/setup_demo_environment.py

# 或一键批量设置
uv run python tools/setup_demo_environment.py --batch
```

### 7. 启动前端应用

```bash
# 启动QueryBot前端
cd frontend
uv run streamlit run app.py

# 或启动管理工具（仅供开发者使用）
cd tools/admin
uv run streamlit run admin_app.py
```

### 8. 验证安装

```bash
# 检查配置
uv run python tools/config_validator.py

# 启动服务
./start_local.sh
```

访问以下端点进行验证：
- **QueryBot前端**：http://localhost:8501
- **API服务**：http://localhost:8000/health
- **管理工具**：http://localhost:8502

## 💻 使用示例

### API调用示例

```python
import requests

# 发送查询请求
response = requests.post(
    "http://localhost:8000/api/query-bot",
    json={
        "text": "查询技术研发部最新春季招聘的所有候选人信息",
        "username": "demo_user",
        "session_id": "demo_session_001"
    }
)

result = response.json()
print(result["text"])
```

### 支持的查询类型

```sql
-- 基础查询
"查询所有Java开发工程师候选人"

-- 聚合统计
"统计各部门招聘成功率"

-- 时间筛选
"查询最近三个月的招聘活动"

-- 复杂条件
"查询P7+级别且经验超过5年的候选人"

-- 关联查询
"查询张伟担任面试官的所有招聘活动和候选人"
```

## 📊 智能处理节点

QueryBot包含13个专业化处理节点：

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **意图分析** | 判断查询意图清晰度 | 用户查询 | 意图清晰度 |
| **关键词提取** | 提取查询关键信息 | 标准化查询 | 关键词列表 |
| **术语映射** | 标准化业务术语 | 关键词 | 标准术语 |
| **查询重写** | 规范化查询表达 | 映射结果 | 重写查询 |
| **数据源识别** | 识别相关数据表 | 重写查询 | 匹配表列表 |
| **表结构分析** | 获取详细表信息 | 表列表 | 表结构信息 |
| **可行性检查** | 验证查询可行性 | 查询+结构 | 可行性结果 |
| **查询示例检索** | 查找相似查询 | 查询意图 | 示例SQL |
| **SQL生成** | 生成SQL语句 | 所有上下文 | SQL查询 |
| **权限控制** | 注入权限条件 | SQL+用户 | 安全SQL |
| **SQL执行** | 执行数据库查询 | 安全SQL | 执行结果 |
| **错误分析** | 分析和修复错误 | 错误信息 | 修复方案 |
| **结果生成** | 格式化最终结果 | 执行结果 | 用户响应 |

## 🔧 配置指南

### 环境变量配置

| 类别 | 变量名 | 描述 | 示例 |
|------|--------|------|------|
| **基础** | `BASE_HOST` | 服务主机地址 | `localhost` |
| **数据库** | `SQLBOT_DB_TYPE` | 数据库类型 | `mysql` 或 `postgresql` |
| **数据库** | `SQLBOT_DB_*` | 数据库连接信息 | `localhost:3306` (MySQL) 或 `localhost:5432` (PostgreSQL) |
| **向量数据库** | `VECTOR_DB_*` | Milvus连接信息 | `localhost:19530` |
| **LLM** | `LLM_MODEL` | LLM模型名称 | `Qwen/Qwen2.5-72B-Instruct` |
| **LLM** | `LLM_API_KEY` | LLM API密钥 | `sk-your_api_key` |
| **LLM** | `LLM_API_BASE` | LLM API基础URL | `https://api.siliconflow.cn/v1` |
| **嵌入模型** | `EMBEDDING_API_*` | 向量化服务配置 | API密钥和端点 |
| **监控** | `LANGFUSE_ENABLED` | 启用追踪 | `true/false` |

### 权限配置

系统提供灵活的权限管理和简化配置：

#### 演示模式（默认）
```bash
# 用于演示和开发的简化权限控制
USER_AUTH_ENABLED=false
```

对于高级用例，通过设置`USER_AUTH_ENABLED=true`启用基于角色的访问控制。

## 🛠️ 开发指南

### 添加新的处理节点

1. **创建节点文件**
```python
# backend/sql_assistant/nodes/new_node.py
def new_processing_node(state: SQLAssistantState) -> dict:
    """新的处理节点"""
    # 实现处理逻辑
    return {"new_field": result}
```

2. **在图中注册**
```python
# backend/sql_assistant/graph/assistant_graph.py
graph_builder.add_node("new_processing", new_processing_node)
graph_builder.add_edge("previous_node", "new_processing")
```

3. **更新状态定义**
```python
# backend/sql_assistant/states/assistant_state.py
class SQLAssistantState(TypedDict):
    # ... 现有字段
    new_field: Optional[Any]
```

### 自定义数据生成器

```python
# tools/data_generation/custom_generator.py
from tools.data_generation import RecruitmentDataGenerator

class CustomDataGenerator(RecruitmentDataGenerator):
    def generate_custom_data(self, count: int):
        # 实现自定义数据生成逻辑
        pass
```

## 🚀 部署指南

### Streamlit Cloud部署
简单的演示部署，请参阅`STREAMLIT_DEPLOYMENT_GUIDE.md`

### 运行应用程序

```bash
# 启动QueryBot服务
uv run uvicorn backend.sql_assistant.api:app --host 0.0.0.0 --port 8000 --reload

# 在另一个终端启动前端
cd frontend
uv run streamlit run app.py
```

### 配置选项

```bash
# 在.env文件中自定义配置
vim .env

# 主要配置区域：
# - 数据库连接设置
# - LLM API密钥和端点
# - 向量数据库配置
# - 监控和追踪选项
```

## 🤝 贡献

我们欢迎社区贡献！

### 如何贡献

1. **Fork项目**并创建功能分支
2. **提交代码**并通过测试
3. **创建Pull Request**并描述更改
4. **代码审查**并在批准后合并到主分支

### 开发标准

- 遵循PEP 8编码标准
- 添加完整的类型提示
- 编写单元测试和文档
- 使用有意义的提交信息

### 报告问题

- 使用GitHub Issues报告错误
- 提供详细的重现步骤
- 包含系统环境信息
- 附加相关日志信息

## 📄 许可证

本项目采用[MIT许可证](LICENSE)。

## 📞 联系我们

- **项目仓库**：https://github.com/i-richardwang/QueryBot
- **问题报告**：https://github.com/i-richardwang/QueryBot/issues

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！