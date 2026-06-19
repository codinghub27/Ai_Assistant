from langchain_classic.agents import tool
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup
import wikipedia
import requests
import os
from langchain_groq import ChatGroq  # add this at the top

load_dotenv()

tavily_api=os.getenv('TAVILY_API_KEY')
client=TavilyClient(api_key=tavily_api)

groq_api_key=os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api_key, temperature=0)


@tool
def web_search(search_query: str):
    """
    Search the web for current information. Use a specific, disambiguated query
    (e.g. 'Valorant game best agents tier list 2025' not just 'best agents').
    Returns titles, URLs, and snippets from top results.
    """
    response = client.search(
        query=search_query,
        search_depth="advanced",
        max_results=3,
    )
    results = response.get("results", [])
    if not results:
        return "No web results found. Try a more specific search query."

    blocks = []
    for index, item in enumerate(results, start=1):
        snippet = item.get('content', 'N/A')[:300]  # limit snippet length
        blocks.append(
            f"Result {index}\n"
            f"Title: {item.get('title', 'N/A')}\n"
            f"Url: {item.get('url', 'N/A')}\n"
            f"Snippet: {snippet}"
        )
    return "\n\n".join(blocks)

@tool
def url_reader(url:str):
    """
    Fetch and extract the main text content from a URL. Use only when web_search snippets are insufficient.
    Input must be a valid URL string.
    """
    # skip sites known to block or return junk
    blocked = ['facebook.com', 'twitter.com', 'instagram.com', 'reddit.com', 'latimes.com']
    if any(site in url for site in blocked):
        return f"Skipped {url} — this site blocks automated reading. Use search snippets instead."
    try:
        headers={"User-Agent":"Mozilla/5.0 (ResearchBot/1.0"}
        response=requests.get(url,timeout=4,headers=headers)
        soup=BeautifulSoup(response.text,'html.parser')
        para=soup.find_all('p')
        text='\n'.join(p.get_text() for p in para)
        # remove very short lines (ads, nav items)
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 60]
        text = '\n'.join(lines)
    except Exception as e:
        return f"failed to read url:{url}:{str(e)}"

    return text[:3000]

@tool
def wikipedia_tool(topic:str):
    """
    use this tool for search and get for a summary of a topic .wikipedia is good for established facts. use this tool to find a specific topic meaning and summary if you don't the meaning of a topic content
    """
    try:
        # strip surrounding quotes the LLM sometimes adds
        topic = topic.strip().strip('"').strip("'")
        summary= wikipedia.summary(topic)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Topic '{topic}' is ambiguous. Try one of: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{topic}'"
    except Exception as e:
        return f"failed to return summary of {topic}: {e}"
    return summary[:1500]

@tool
def summarizer_tool(text: str):
    """
    Turn long research text into structured notes with key facts, names, stats,
    and bullet points. Use after url_reader when content is long.
    """
    response = llm.invoke(
        "Extract detailed structured research notes from this text. "
        "Include specific facts, names, numbers, rankings, and reasons. "
        "Use bullet points:\n\n" + text[:6000]
    )
    return response.content

# print(wikipedia_tool.invoke("what is python "))
# print(url_reader.invoke("https://en.wikipedia.org/wiki/Artificial_intelligence"))
# print(summarizer_tool.invoke("Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals."))

