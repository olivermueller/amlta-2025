from browser_use import Agent, ChatOpenAI, Tools, ActionResult
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = ""

async def main():

    tools = Tools()
    
    @tools.action(description='write counts to csv with head,tails columns')
    def write_counts_to_csv(content: str) -> ActionResult:
        with open("results.csv", "w") as f:
            f.write("head,tails\n")
            f.write(content)
        return "Results written to results.csv"
    
    llm = ChatOpenAI(
        model="gpt-4o"
    )

    task = """Go to https://justflipacoin.com/#flip-a-coin, flip the coin 5 times, and record the results of each flip. After completing the flips, summarize how many times heads and tails were flipped and write it to a csv file using the write counts to csv tool."""
    agent = Agent(task=task, llm=llm, tools=tools)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())