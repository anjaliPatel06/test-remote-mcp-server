from fastmcp import FastMCP
import random
import json

mcp = FastMCP('simple calculator server')

@mcp.tool
def add(a:int,b:int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def random_number(min_val:int = 1, max_val:int = 100) -> int:
    """Generate a random number within a range"""
    return random.randint(min_val,max_val)

@mcp.resource("info://server")
def get_server_info() -> str:
    """Get information about this server"""
    return json.dumps({
        "name": "simple calculator server",
        "version": "1.0.0",
        "description": "A basic MCP server with math tools",
        "tools": ["add","random_number"],
        "author" : "your Name"
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000 )
  
