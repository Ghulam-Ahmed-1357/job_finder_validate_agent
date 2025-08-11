from agents import Agent, RunContextWrapper,Runner,set_tracing_disabled,OpenAIChatCompletionsModel, input_guardrail, enable_verbose_stdout_logging, RunConfig, function_tool, GuardrailFunctionOutput, TResponseInputItem, InputGuardrailTripwireTriggered
from openai import AsyncOpenAI
import asyncio

from pydantic import BaseModel

GEMINI_MODEL ="gemini-2.0-flash"
GEMINI_API_KEY = "AIzaSyCHgy-9liuIF2KaC_7UqkhQ03CBAFBtEAw"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

enable_verbose_stdout_logging()

set_tracing_disabled(disabled=True)

client = AsyncOpenAI(api_key=GEMINI_API_KEY,base_url=BASE_URL)

model= OpenAIChatCompletionsModel(model=GEMINI_MODEL,openai_client=client)

class InputGuardrailType(BaseModel):
    reason: str
    user_is_asking_about_job: bool

class UserProfile(BaseModel):
    name:str
    age:int
    gender:str
    education:str
    experience:int

@function_tool()
def job_finder(wrapper:RunContextWrapper[UserProfile]):
    '''Find job for the applicant'''
    if(wrapper.context.experience > 1):
        return "I can find job for you"
    # elif(wrapper.context.experience > 3):
    #     return "You are welcome, there are many jobs for you"
    else:
        return "I cann't find a job for you"

@input_guardrail
async def verify_user_Input(
    ctx: RunContextWrapper[UserProfile],
    input:str | list[TResponseInputItem],
    agent:Agent) -> GuardrailFunctionOutput:
    print("\n\n\n\nInput Guardrail\n\n\n\n")
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered= result.final_output.user_is_asking_about_job
    )

guardrail_agent = Agent(name='Guardrail agent',instructions='Check that the user is only asking about job',output_type=InputGuardrailType,model=model)

job_finder_agent = Agent(name= "Job Finder Agent", instructions="you will tell the user that the user is validated for getting the job. Use tool to answer the user question and validate whether the applier can get job or not.",tools=[job_finder],input_guardrails=[verify_user_Input],model=model)

def main():
    user_data = UserProfile(
    name= "Umer",
    age= 23,
    education= "BSCS",
    experience= 2, 
    gender= "Male")

    try:
        # result = await Runner.run(
        #     job_finder_agent,
        #     "hello find a job for me as a web development", 
        #     context=user_data, 
        #     run_config=RunConfig(model=model))
        result = Runner.run_sync(
            job_finder_agent,
            "hello find a job for me as a web development", 
            context=user_data, 
            run_config=RunConfig(model=model))
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print('User is not asking about job')

def start():
    asyncio.run(main())