# Java MCP DB Server

This is a Model Context Protocol (MCP) server written in Java for Oracle database operations.

**Note:** This server is currently in development. The Java MCP SDK is being used, but the implementation may need updates as the SDK matures.

## Features (Planned)

- Query Oracle database with SELECT statements
- Execute INSERT/UPDATE/DELETE operations on Oracle DB
- Database schema information

## Setup

1. Ensure Java 17+ is installed
2. Build the project:
   ```bash
   cd java-db-server
   mvn clean compile
   ```

3. For Oracle DB, update the connection details in `McpDbServer.java`:
   ```java
   String url = "jdbc:oracle:thin:@localhost:1521:xe";
   String username = "your_username";
   String password = "your_password";
   ```

4. Run the server:
   ```bash
   java -cp target/classes com.example.McpDbServer
   ```

## Current Status

- Project structure created
- Basic code framework in place
- Uses H2 database for testing (can be switched to Oracle)
- MCP configuration added to `.vscode/mcp.json`

## Dependencies

- MCP Java SDK
- Oracle JDBC Driver (for Oracle DB)
- H2 Database (for testing)

Once the Java MCP SDK stabilizes, this server will provide full database query capabilities through the MCP protocol.