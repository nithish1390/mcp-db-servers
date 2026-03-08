# MCP Database Servers

This workspace contains two MCP database servers:

## Python MCP Server (SQLite)

- Location: `server.py`
- Database: SQLite (example.db)
- Features: Query and execute SQL operations
- Command: `python server.py`

## Java MCP Server (Oracle/H2)

- Location: `java-db-server/`
- Database: Configurable (currently H2 for testing, can be changed to Oracle)
- Features: Planned query and execute operations
- Status: In development
- Command: `java -cp java-db-server/target/classes com.example.McpDbServer`

## MCP Configuration

Both servers are configured in `.vscode/mcp.json` for use with VS Code MCP clients.

## Python Server Features

- **Tools**:
  - `query_db`: Execute SELECT queries
  - `execute_db`: Execute modification queries

- **Resources**:
  - `db://schema`: Database schema information

## Java Server Features (Planned)

Similar tools and resources for Oracle database operations.

## Setup

1. For Python server: `pip install "mcp[cli]"`
2. For Java server: `cd java-db-server && mvn clean compile`

## Usage

Run either server and connect via MCP-compatible clients like Claude Desktop or VS Code extensions.

## Tools

- `query_db`: Execute SELECT queries
- `execute_db`: Execute modification queries

## Resources

- `db://schema`: Database schema information