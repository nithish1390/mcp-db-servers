# MCP Database and Excel Servers

This workspace contains MCP servers for database operations and Excel analysis:

## Python MCP Server (SQLite)

- Location: `server.py`
- Database: SQLite (example.db)
- Features: Query and execute SQL operations
- Command: `python server.py`

## Python MCP Server (Oracle)

- Location: `server_oracle.py`
- Database: Oracle DB (hostname: sgxydfg, port: 1521, service: exsgid)
- Features: Query and execute SQL operations on Oracle database
- Command: `python server_oracle.py`

## Python MCP Server (Excel Operations)

- Location: `excel.py`
- Features: Excel file creation, charts, pivot tables, and data analysis
- Command: `python excel.py`

## Java MCP Server (Oracle/H2)

- Location: `java-db-server/`
- Database: Configurable (currently H2 for testing, can be changed to Oracle)
- Features: Planned query and execute operations
- Status: In development
- Command: `java -cp java-db-server/target/classes com.example.McpDbServer`

## MCP Configuration

All servers are configured in `.vscode/mcp.json` for use with VS Code MCP clients.

## Server Features

### Database Servers
- **Tools**:
  - `query_db`: Execute SELECT queries
  - `execute_db`: Execute modification queries

- **Resources**:
  - `db://schema`: Database schema information

### Excel Server
- **Tools**:
  - `create_excel_file`: Create Excel files from CSV data
  - `create_excel`: Create dynamic Excel files with multiple sheets and flexible data formats
  - `update_excel`: Update existing Excel files with new data (cells, ranges, append rows/columns)
  - `create_chart`: Create charts (bar, line, pie, scatter)
  - `create_pivot_table`: Create pivot tables with aggregation
  - `analyze_data`: Perform data analysis (summary, correlation, distribution)
  - `format_excel_file`: Apply formatting to Excel files

- **Resources**:
  - `excel://help`: Help information for Excel operations

## Setup

1. For Python servers: `pip install "mcp[cli]" cx-Oracle pandas openpyxl matplotlib seaborn`
2. For Java server: `cd java-db-server && mvn clean compile`

## Usage

Run any server and connect via MCP-compatible clients like Claude Desktop or VS Code extensions.