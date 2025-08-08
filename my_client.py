import asyncio
from fastmcp import Client

async def main():
    # Create a client instance. FastMCP will infer the StdioTransport
    # from the python script path.
    # The client will manage the server subprocess lifecycle.
    async with Client("my_server.py") as client:
        # Call a tool on the server.
        # The first argument to call_tool is the tool name,
        # and the second is a dictionary of arguments.
        # Assuming the server has a tool named 'hello'.
        result = await client.call_tool("hello", {"name": "World"})
        print(result)    

if __name__ == "__main__":
    asyncio.run(main())

