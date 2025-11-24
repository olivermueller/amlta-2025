# 1) Your standard FastAPI app
# Assumes the FastAPI app from above is already defined
from fastmcp import FastMCP
from fastapi import FastAPI

app = FastAPI(title="Math API")

@app.post("/add_numbers", operation_id="add_numbers")
async def add_numbers(a: int, b: int):
    return {"result": a + b}

# 1. Generate MCP server from your API
mcp = FastMCP.from_fastapi(app=app, name="Math API MCP")

# 2. Create the MCP's ASGI app
mcp_app = mcp.http_app(path='/mcp')

# 3. Create a new FastAPI app that combines both sets of routes
combined_app = FastAPI(
    title="Math API with MCP",
    routes=[
        *mcp_app.routes,  # MCP routes
        *app.routes,      # Original API routes
    ],
    lifespan=mcp_app.lifespan,
)

# Now you have:
# - Regular API: http://localhost:8000/add_numbers
# - LLM-friendly MCP: http://localhost:8000/mcp
# Both served from the same FastAPI application!

# 5) Run with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(combined_app, host="0.0.0.0", port=8000)