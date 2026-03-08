package com.example;

import io.modelcontextprotocol.server.Server;
import io.modelcontextprotocol.server.StdioServerTransport;
import io.modelcontextprotocol.types.*;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

public class McpDbServer {

    private static Connection connection;

    public static void main(String[] args) throws Exception {
        // Initialize database connection
        initializeDatabase();

        // Create MCP server
        Server server = Server.builder()
                .name("java-db-server")
                .version("1.0.0")
                .build();

        // Register tools
        server.setListToolsHandler((request) -> {
            return CompletableFuture.completedFuture(new ListToolsResult(List.of(
                    new Tool(
                            "query_db",
                            "Execute a SELECT query on the database",
                            Map.of("query", new ToolArg("string", "SQL SELECT query to execute", true))
                    ),
                    new Tool(
                            "execute_db",
                            "Execute an INSERT, UPDATE, or DELETE query",
                            Map.of("query", new ToolArg("string", "SQL query to execute", true))
                    )
            ), null));
        });

        server.setCallToolHandler((request) -> {
            String name = request.params().name();
            Map<String, Object> arguments = request.params().arguments();
            try {
                switch (name) {
                    case "query_db":
                        String query = (String) arguments.get("query");
                        String result = handleQuery(query);
                        return CompletableFuture.completedFuture(new CallToolResult(List.of(new TextContent("text", result)), null, null));
                    case "execute_db":
                        String execQuery = (String) arguments.get("query");
                        String execResult = handleExecute(execQuery);
                        return CompletableFuture.completedFuture(new CallToolResult(List.of(new TextContent("text", execResult)), null, null));
                    default:
                        return CompletableFuture.completedFuture(new CallToolResult(List.of(new TextContent("text", "Unknown tool: " + name)), null, null));
                }
            } catch (Exception e) {
                return CompletableFuture.completedFuture(new CallToolResult(List.of(new TextContent("text", "Error: " + e.getMessage())), null, null));
            }
        });

        // Register resources
        server.setListResourcesHandler((request) -> {
            return CompletableFuture.completedFuture(new ListResourcesResult(List.of(
                    new Resource("db://schema", "Database schema information", null, null, null)
            ), null));
        });

        server.setReadResourceHandler((request) -> {
            String uri = request.params().uri();
            if ("db://schema".equals(uri)) {
                String schema = """
Tables:
- users: id (INT PRIMARY KEY), name (VARCHAR(100)), age (INT)
                """.trim();
                return CompletableFuture.completedFuture(new ReadResourceResult(List.of(new TextResourceContents(uri, "text/plain", schema)), null));
            }
            throw new IllegalArgumentException("Unknown resource: " + uri);
        });

        // Start server
        StdioServerTransport transport = new StdioServerTransport();
        server.connect(transport).join();
    }

    private static void initializeDatabase() throws SQLException {
        // For demo purposes, using H2. Replace with Oracle connection details.
        String url = "jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1";
        String username = "sa";
        String password = "";

        connection = DriverManager.getConnection(url, username, password);

        // Create sample table
        try (Statement stmt = connection.createStatement()) {
            stmt.execute("""
                CREATE TABLE users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    age INT
                )
            """);

            // Insert sample data
            stmt.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)");
            stmt.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)");
            stmt.execute("INSERT INTO users (name, age) VALUES ('Charlie', 35)");
        }
    }

    private static String handleQuery(String query) throws SQLException {
        try (PreparedStatement stmt = connection.prepareStatement(query);
             ResultSet rs = stmt.executeQuery()) {

            StringBuilder result = new StringBuilder();
            int columnCount = rs.getMetaData().getColumnCount();

            // Add header
            for (int i = 1; i <= columnCount; i++) {
                if (i > 1) result.append(" | ");
                result.append(rs.getMetaData().getColumnName(i));
            }
            result.append("\n");

            // Add separator
            result.append("-".repeat(result.length() - 1)).append("\n");

            // Add data rows
            while (rs.next()) {
                for (int i = 1; i <= columnCount; i++) {
                    if (i > 1) result.append(" | ");
                    result.append(rs.getString(i));
                }
                result.append("\n");
            }

            return result.toString().trim();
        }
    }

    private static String handleExecute(String query) throws SQLException {
        try (PreparedStatement stmt = connection.prepareStatement(query)) {
            int rowsAffected = stmt.executeUpdate();
            return "Query executed successfully. Rows affected: " + rowsAffected;
        }
    }
}