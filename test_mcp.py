import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
import traceback

async def main():
    url = "https://mcp.browserbase.com/mcp?browserbaseApiKey=bb_live_lm78csp7I4Lp17uFEgjnQRzIMYA"
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Initialized!")
                tools = await session.list_tools()
                print("Tools:", tools)
    except Exception as e:
        print("Error:")
        traceback.print_exc()

asyncio.run(main())
