"""MCP server for generating architecture diagrams.

This server creates diagram markup (Mermaid) based on provided components and relationships.

Example tool call (Mermaid flowchart):
{
  "tool": "create_architecture_diagram",
  "args": {
    "components": ["Web", "API", "Database"],
    "relations": [["Web", "API"], ["API", "Database"]],
    "direction": "LR"
  }
}

The response is a Mermaid diagram string that can be rendered in Markdown viewers that support Mermaid.
"""

import json
import os
import tempfile
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from mcp.server.fastmcp import Context, FastMCP


mcp = FastMCP("Diagram Generator Server")


def _parse_or_error(data: str) -> Any:
    """Parse JSON-like strings into Python objects."""
    try:
        return json.loads(data)
    except Exception:
        try:
            # Fallback to python literal eval
            import ast

            return ast.literal_eval(data)
        except Exception as e:
            raise ValueError(f"Unable to parse input as JSON or Python literal: {e}")


@mcp.tool()
def create_architecture_diagram(
    components: Any,
    relations: Any,
    direction: str = "LR",
    diagram_type: str = "flowchart",
    ctx: Context = None,
) -> str:
    """Create an architecture diagram description.

    Args:
        components: List of component names.
        relations: List of [from, to] pairs.
        direction: Graph direction (e.g., LR, TB).
        diagram_type: Type of Mermaid diagram (flowchart or graph TD).

    Returns:
        Mermaid diagram text.
    """
    # Parse if inputs are stringified
    if isinstance(components, str):
        components = _parse_or_error(components)
    if isinstance(relations, str):
        relations = _parse_or_error(relations)

    if not isinstance(components, list):
        raise ValueError("components must be a list")
    if not isinstance(relations, list):
        raise ValueError("relations must be a list")

    # Mermaid flowchart support
    direction = direction.upper() if isinstance(direction, str) else "LR"
    diagram_lines: List[str] = []

    if diagram_type.lower() in ["flowchart", "flowchart"]:
        diagram_lines.append(f"flowchart {direction}")
        # Add nodes for readability (Mermaid auto-creates nodes from relations too)
        for node in components:
            safe_node = str(node).replace(" ", "_")
            diagram_lines.append(f"    {safe_node}[{node}]")

        # Add relations
        for rel in relations:
            if isinstance(rel, (list, tuple)) and len(rel) >= 2:
                src = str(rel[0]).replace(" ", "_")
                dst = str(rel[1]).replace(" ", "_")
                diagram_lines.append(f"    {src} --> {dst}")
            else:
                raise ValueError("Each relation must be a list/tuple of [from, to].")
    else:
        raise ValueError(f"Unsupported diagram type: {diagram_type}")

    return "\n".join(diagram_lines)


def _layout_graph(components: List[str], relations: List[List[str]]) -> Dict[str, Tuple[int, int]]:
    """Compute simple hierarchical layout positions for nodes."""
    # Build adjacency and reverse adjacency
    adj: Dict[str, List[str]] = {c: [] for c in components}
    for src, dst in relations:
        if src in adj:
            adj[src].append(dst)
        else:
            adj[src] = [dst]
        if dst not in adj:
            adj[dst] = []

    # BFS from first component to assign levels
    levels: Dict[str, int] = {}
    queue = deque()
    if components:
        queue.append((components[0], 0))

    while queue:
        node, level = queue.popleft()
        if node in levels:
            continue
        levels[node] = level
        for neigh in adj.get(node, []):
            if neigh not in levels:
                queue.append((neigh, level + 1))

    # Assign any unvisited nodes to next levels
    for node in components:
        if node not in levels:
            levels[node] = max(levels.values(), default=0) + 1

    # Group nodes by level
    level_nodes: Dict[int, List[str]] = {}
    for node, level in levels.items():
        level_nodes.setdefault(level, []).append(node)

    # Compute positions
    positions: Dict[str, Tuple[int, int]] = {}
    x_gap = 220
    y_gap = 120
    for level, nodes in sorted(level_nodes.items()):
        y_start = 50
        for i, node in enumerate(nodes):
            x = 50 + level * x_gap
            y = y_start + i * y_gap
            positions[node] = (x, y)

    return positions


@mcp.tool()
def create_architecture_diagram_png(
    components: Any,
    relations: Any,
    output_name: str = "architecture",
    direction: str = "LR",
    ctx: Context = None,
) -> str:
    """Create a PNG architecture diagram using a lightweight renderer.

    Args:
        components: List of component names.
        relations: List of [from, to] pairs.
        output_name: Base filename for the generated PNG (without extension).
        direction: Graph direction (ignored for layout in this simple renderer).

    Returns:
        Path to the generated PNG file.
    """
    # Parse inputs
    if isinstance(components, str):
        components = _parse_or_error(components)
    if isinstance(relations, str):
        relations = _parse_or_error(relations)

    if not isinstance(components, list):
        raise ValueError("components must be a list")
    if not isinstance(relations, list):
        raise ValueError("relations must be a list")

    positions = _layout_graph([str(c) for c in components], [[str(a), str(b)] for a, b in relations])

    # Determine canvas size
    max_x = max(x for x, _ in positions.values())
    max_y = max(y for _, y in positions.values())
    width = max_x + 200
    height = max_y + 150

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except Exception:
        font = ImageFont.load_default()

    # Draw edges
    for src, dst in relations:
        if src not in positions or dst not in positions:
            continue
        x1, y1 = positions[str(src)]
        x2, y2 = positions[str(dst)]
        # Start/end at box centers
        draw.line((x1 + 60, y1 + 20, x2 + 60, y2 + 20), fill="black", width=2)
        # Arrow head
        draw.polygon(
            [
                (x2 + 60, y2 + 20),
                (x2 + 55, y2 + 15),
                (x2 + 55, y2 + 25),
            ],
            fill="black",
        )

    # Draw nodes
    for node, (x, y) in positions.items():
        w = 140
        h = 40
        draw.rectangle([x, y, x + w, y + h], outline="black", width=2, fill="#F0F8FF")
        try:
            bbox = draw.textbbox((0, 0), node, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = font.getsize(node)
        text_x = x + (w - text_w) / 2
        text_y = y + (h - text_h) / 2
        draw.text((text_x, text_y), node, fill="black", font=font)

    temp_dir = tempfile.mkdtemp(prefix="diagram_mcp_")
    output_path = os.path.join(temp_dir, f"{output_name}.png")
    img.save(output_path)

    return output_path


@mcp.tool()
def create_mermaid_diagram(mermaid_text: str, ctx: Context = None) -> str:
    """Return a raw Mermaid diagram string (for rendering in a Mermaid viewer)."""
    return mermaid_text


if __name__ == "__main__":
    mcp.run()
