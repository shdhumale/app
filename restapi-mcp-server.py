# rest_api_server.py
from fastmcp import FastMCP, Context
import httpx

mcp = FastMCP(name="RESTful API Wrapper 🌐")

BASE_URL = "https://api.restful-api.dev/objects"

@mcp.tool()
async def get_all_objects(ctx: Context):
    async with httpx.AsyncClient() as client:
        resp = await client.get(BASE_URL)
        print("get_all_objects",resp.json())
    return resp.json()

@mcp.tool()
async def get_objects_by_ids(ids: list[str], ctx: Context):
    query = "&".join([f"id={i}" for i in ids])
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}?{query}")
        print("get_objects_by_ids",resp.json())
    return resp.json()

@mcp.tool()
async def get_object_by_id(object_id: str, ctx: Context):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/{object_id}")
        print("get_object_by_id",resp.json())
    return resp.json()

@mcp.tool()
async def add_object(data: dict, ctx: Context):
    async with httpx.AsyncClient() as client:
        resp = await client.post(BASE_URL, json=data)
        print("add_object",resp.json())
    return resp.json()

@mcp.tool()
async def update_object(object_id: str, data: dict, ctx: Context):
    async with httpx.AsyncClient() as client:
        resp = await client.put(f"{BASE_URL}/{object_id}", json=data)
        print("update_object",resp.json())
    return resp.json()

@mcp.tool()
async def patch_object(object_id: str, data: dict, ctx: Context):
    async with httpx.AsyncClient() as client:
        resp = await client.patch(f"{BASE_URL}/{object_id}", json=data)
        print("patch_object",resp.json())
    return resp.json()

@mcp.tool()
async def delete_object(object_id: str, ctx: Context):
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{BASE_URL}/{object_id}")
        print("delete_object",resp.json())
    return {"status_code": resp.status_code, "message": "Deleted" if resp.status_code == 200 else "Failed"}

if __name__ == "__main__":
    #mcp.run(transport="streamable-http", host="127.0.0.1", port=8001, path="/mcp")
    mcp.run()
