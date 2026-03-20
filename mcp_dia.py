import os
import tempfile
from typing import Any, List, Optional
from mcp.server.fastmcp import FastMCP
import graphviz
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.generic.device import Tablet
from diagrams.generic.network import Router
from diagrams.onprem.client import Client, User
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Nginx

# Initialize FastMCP server
mcp = FastMCP("Visual Diagram Server")

@mcp.tool()
def create_graphviz_diagram(dot_source: str, format: str = "png", filename: str = "diagram") -> str:
    """
    Create a diagram using Graphviz DOT language.
    
    Args:
        dot_source: The Graphviz DOT source code.
        format: Output format (e.g., 'png', 'svg', 'pdf').
        filename: Name of the output file (without extension).
        
    Returns:
        Path to the generated diagram file.
    """
    try:
        dot = graphviz.Source(dot_source)
        # Create a temporary directory for the output
        temp_dir = tempfile.mkdtemp(prefix="mcp_graphviz_")
        output_path = dot.render(filename=filename, directory=temp_dir, format=format, cleanup=True)
        return output_path
    except Exception as e:
        return f"Error generating Graphviz diagram: {str(e)}"

@mcp.tool()
def create_cloud_diagram(
    name: str,
    nodes: List[dict],
    edges: List[dict],
    direction: str = "LR",
    out_format: str = "png"
) -> str:
    """
    Create a cloud architecture diagram using the 'diagrams' library.
    
    Args:
        name: The name of the diagram.
        nodes: A list of node dictionaries. Each dict should have 'id', 'label', and 'type'.
               Example types: 'aws.compute.EC2', 'aws.database.RDS', 'aws.network.ELB',
               'onprem.client.User', 'onprem.compute.Server', 'onprem.database.PostgreSQL',
               'onprem.network.Nginx', 'generic.device.Tablet'.
        edges: A list of edge dictionaries. Each dict should have 'from' and 'to' (using node IDs).
        direction: Diagram direction ('LR', 'TB', 'RL', 'BT').
        out_format: Output format ('png', 'jpg', 'svg', 'pdf').
        
    Returns:
        Path to the generated diagram file.
    """
    try:
        # Map of string types to classes
        # This is a limited subset for demonstration. A full mapping would be huge.
        from diagrams.aws.compute import EC2
        from diagrams.aws.database import RDS
        from diagrams.aws.network import ELB
        from diagrams.aws.storage import S3
        from diagrams.onprem.client import Client, User
        from diagrams.onprem.compute import Server
        from diagrams.onprem.database import PostgreSQL
        from diagrams.onprem.network import Nginx
        from diagrams.generic.device import Tablet
        
        type_map = {
            "aws.compute.EC2": EC2,
            "aws.database.RDS": RDS,
            "aws.network.ELB": ELB,
            "aws.storage.S3": S3,
            "onprem.client.User": User,
            "onprem.client.Client": Client,
            "onprem.compute.Server": Server,
            "onprem.database.PostgreSQL": PostgreSQL,
            "onprem.network.Nginx": Nginx,
            "generic.device.Tablet": Tablet,
        }

        temp_dir = tempfile.mkdtemp(prefix="mcp_diagrams_")
        output_file = os.path.join(temp_dir, "cloud_diagram")

        with Diagram(name, show=False, filename=output_file, outformat=out_format, direction=direction):
            created_nodes = {}
            for node_data in nodes:
                node_id = node_data['id']
                node_label = node_data.get('label', node_id)
                node_type_str = node_data.get('type', 'onprem.compute.Server')
                
                node_class = type_map.get(node_type_str, Server)
                created_nodes[node_id] = node_class(node_label)
            
            for edge_data in edges:
                src_id = edge_data['from']
                dst_id = edge_data['to']
                label = edge_data.get('label', "")
                
                if src_id in created_nodes and dst_id in created_nodes:
                    if label:
                        created_nodes[src_id] >> Edge(label=label) >> created_nodes[dst_id]
                    else:
                        created_nodes[src_id] >> created_nodes[dst_id]

        return f"{output_file}.{out_format}"
    except Exception as e:
        return f"Error generating cloud diagram: {str(e)}"

if __name__ == "__main__":
    mcp.run()
