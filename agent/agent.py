import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_classic.agents import create_react_agent, AgentExecutor
from .tools import web_search, wikipedia_tool, url_reader, summarizer_tool
from langchain_core.prompts import PromptTemplate

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# use smaller faster model to save tokens
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api_key, temperature=0)


def get_agent(question: str, chat_history: str = ""):
    prompt = PromptTemplate.from_template(
        """You are a helpful research assistant. Answer the user's question clearly and concisely.

You have access to these tools:
{tools}

Use this format STRICTLY:
Question: the input question
Thought: what should I do
Action: one of [{tool_names}]
Action Input: the input
Observation: the result
Thought: I now know the final answer
Final Answer: the answer

RULES:
- Call web_search ONCE with a clear query
- If the snippets answer the question — write Final Answer immediately
- Only call url_reader if snippets are missing key facts — maximum 1 URL
- Never repeat the same tool call
- Never call more than 3 tools total
- Write Final Answer in this format:
  * 1 paragraph summary (3-4 sentences)
  * ## Key Findings — 4-6 bullet points with specific facts
  * ## Bottom Line — 1-2 sentences conclusion

Previous conversation:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""
    )

    tools = [web_search, url_reader, wikipedia_tool, summarizer_tool]
    agent = create_react_agent(llm=llm, prompt=prompt, tools=tools)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=4,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        early_stopping_method="generate",
    )

    result = agent_executor.invoke({"input": question, "chat_history": chat_history})
    return result
