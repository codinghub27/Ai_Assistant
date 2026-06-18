import os
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_classic.agents import create_react_agent,AgentExecutor
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from tavily import TavilyClient
from bs4 import BeautifulSoup
import requests

@tool
def calculator(expression:str)->str:
    """
Use this to evaluate a math expression. Input must be a valid math expression as a string like '10 + 5' or '25 * 4'   """
    evalu=eval(expression)
    return f"Calculated Expression : {evalu}"



tavily_api=os.getenv('TAVILY_API_KEY')
client=TavilyClient(api_key=tavily_api)

@tool
def web_search(search_query:str):
    """
    Use this to web_search tool for searching a user's query. Input must be a string for searching the query to a web research

    """
    response =client.search(query=search_query)
    results=response["results"]
    output=""

    output+="\n".join([
        f"Title:{item['title']},\n Url:{item['url']},\nSnippet:{item['content']}"
        for item in results
    ])
    output+="\n\nNew Data"
    return output

@tool
def url_reader(url:str):
    """
    Use this to url_reader tool for searching a url and get text for research of a url . Input must be a url string for searching the url to a web research

    """
    try:
        headers={"User-Agent":"Mozilla/5.0 (ResearchBot/1.0"}
        response = requests.get(url, timeout=5,headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs=soup.find_all('p')
        text=' '.join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"failed to read url:{url}:{str(e)}"

    return text[:2000]




@tool
def weather_data(city_name:str):
    """
Use this to get a City weather. Input must be a valid string city like 'Bhimavaram' or 'Hyderabad'
    """
    return f"Today {city_name} weather is 'Sunny,32°C'"






load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")

llm=ChatGroq(model="llama-3.3-70b-versatile",api_key=groq_api_key,temperature=0)

# prompt=hub.pull("hwchase17/react")
prompt = PromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format STRICTLY:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT RULES:
- You MUST use one of [{tool_names}] as the Action. Never use "None" as an Action.
- Once you have enough information from an Observation, write "Thought: I now know the final answer" followed by "Final Answer: ..." immediately.
- Do NOT repeat the same Action and Action Input more than once.

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
)

agent=create_react_agent(llm=llm,prompt=prompt,tools=[calculator,weather_data,web_search])

agent_executor=AgentExecutor(
    agent=agent,
    tools=[calculator,weather_data,web_search],
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)

print(agent_executor.invoke({"input":"what is 200 / 4 and what is the weather in Delhi?"}))

# print(agent_executor.invoke({"input": "latest AI news"}))

# results = client.search(query="latest AI news")
# print(results)

