from agents import RunConfig, function_tool
from agents import Agent, RunContextWrapper,Runner,set_tracing_disabled,OpenAIChatCompletionsModel
from openai import AsyncOpenAI
import asyncio

from pydantic import BaseModel

GEMINI_MODEL ="gemini-2.0-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

set_tracing_disabled(disabled=True)

client = AsyncOpenAI(api_key=GEMINI_API_KEY,base_url=BASE_URL)

model= OpenAIChatCompletionsModel(model=GEMINI_MODEL,openai_client=client)


class UserProfile(BaseModel):
    name:str
    age:int
    gender:str
    education:str
    experience:int

user_data = UserProfile(
    name= "Umer",
    age= 23,
    education= "BSCS",
    experience= 2, 
    gender= "Male")

@function_tool
def job_finder(wrapper:RunContextWrapper[UserProfile]):
    '''Find job for the applicant'''
    if(wrapper.context.experience > 1):
        return "I can find job for you"
    # elif(wrapper.context.experience > 3):
    #     return "You are welcome, there are many jobs for you"
    else:
        return "I cann't find a job for you"

job_finder_agent = Agent(name= "Job Finder Agent", instructions="you will tell the user that the user is validated for grtting the job. Use tool to answer the user question and validate whether the applier can get job or not.",tools=[job_finder],model= model)

async def main():
    result = await Runner.run(job_finder_agent,"hello find a job for me web development",context=user_data, run_config=RunConfig(model=model))
    print(result.final_output)

def start():
    asyncio.run(main())