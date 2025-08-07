# QueryBot - Admin Tools

This directory contains admin tools for QueryBot, for use by development and maintenance personnel only.

## Vector Database Management Tools

### Launch Method
```bash
cd tools/admin
uv run streamlit run admin_app.py
```

### Feature Description
- **Vector Database Management**: Manage data in Milvus vector database
- **CSV Data Upload**: Batch upload and update vector data
- **Data Deduplication**: Automatically detect and handle duplicate data
- **Collection Statistics**: View database statistics

### Important Notes
- This tool is for development and maintenance personnel only
- Please ensure environment variables are properly configured before use
- Data operations directly affect production data, please operate with caution

### Environment Requirements
- Configured Milvus database connection
- Valid embedding service configuration
- Correct data configuration file paths