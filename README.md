# MCP Database Servers

This workspace contains three MCP database servers:

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

## Java MCP Server (Oracle/H2)

- Location: `java-db-server/`
- Database: Configurable (currently H2 for testing, can be changed to Oracle)
- Features: Planned query and execute operations
- Status: In development
- Command: `java -cp java-db-server/target/classes com.example.McpDbServer`

## MCP Configuration

All servers are configured in `.vscode/mcp.json` for use with VS Code MCP clients.

## Server Features

- **Tools**:
  - `query_db`: Execute SELECT queries
  - `execute_db`: Execute modification queries

- **Resources**:
  - `db://schema`: Database schema information

## Setup

1. For Python servers: `pip install "mcp[cli]" cx-Oracle`
2. For Java server: `cd java-db-server && mvn clean compile`

## Usage

Run any server and connect via MCP-compatible clients like Claude Desktop or VS Code extensions.

## Tools

- `query_db`: Execute SELECT queries
- `execute_db`: Execute modification queries

## Resources

- `db://schema`: Database schema information