from browser_use import Agent, ChatOpenAI, Tools, ActionResult
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = ""

async def main():
    
    tools = Tools()

    @tools.action(description='Ask human for help with a question')
    def ask_human(question: str) -> ActionResult:
        answer = input(f'{question} > ')
        return f'The human responded with: {answer}'
    
    llm = ChatOpenAI(
        model="gpt-4o"
    )

    task = """Go to rpachallenge.com, click on start, and fill in the form with this data one after another until all entries are submitted:
    First Name	Last Name 	Company Name	Role in Company	Address	Email	Phone Number
John	Smith	IT Solutions	Analyst	98 North Road	jsmith@itsolutions.co.uk	40716543298
Jane	Dorsey	MediCare	Medical Engineer	11 Crown Street	jdorsey@mc.com	40791345621
Albert	Kipling	Waterfront	Accountant	22 Guild Street	kipling@waterfront.com	40735416854
Michael	Robertson	MediCare	IT Specialist	17 Farburn Terrace	mrobertson@mc.com	40733652145
Doug	Derrick	Timepath Inc.	Analyst	99 Shire Oak Road	dderrick@timepath.co.uk	40799885412
Jessie	Marlowe	Aperture Inc.	Scientist	27 Cheshire Street	jmarlowe@aperture.us	40733154268
Stan	Hamm	Sugarwell	Advisor	10 Dam Road	shamm@sugarwell.org	40712462257
Michelle	Norton	Aperture Inc.	Scientist	13 White Rabbit Street	mnorton@aperture.us	40731254562
Stacy	Shelby	TechDev	HR Manager	19 Pineapple Boulevard	sshelby@techdev.com	40741785214
Lara	Palmer	Timepath Inc.	Programmer	87 Orange Street	lpalmer@timepath.co.uk	40731653845

When completed ask human if everything was filled correctly using the ask_human tool."""
    agent = Agent(task=task, llm=llm, tools=tools)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())