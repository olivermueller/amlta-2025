from browser_use import Agent, ChatOpenAI, Tools, ActionResult
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = ""

async def main():

    tools = Tools()

    #TODO: Define your tool here (the tools defined for browser use will automatically be added to tools) https://docs.browser-use.com/customize/tools/add
    # the tool shall ask the user for verification of the results of the challenge before doing anything else
    # Solve this: https://rpachallenge.com
    
    llm = ChatOpenAI(
        model="gpt-4o"
    )

    # Define the task prompt here:
    task = """your task prompt here"""


    agent = Agent(task=task, llm=llm, tools=tools)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())