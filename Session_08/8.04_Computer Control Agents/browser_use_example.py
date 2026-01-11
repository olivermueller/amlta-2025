from browser_use import Agent, ChatOpenAI, Tools, ActionResult
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = ""

async def main():

    tools = Tools()
    
    llm = ChatOpenAI(
        model="gpt-4o"
    )
    task = """Go to https://justflipacoin.com/#flip-a-coin, flip the coin 5 times, and record the results of each flip. 
    After completing the flips, summarize how many times heads and tails were flipped."""
    agent = Agent(task=task, llm=llm, tools=tools)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())