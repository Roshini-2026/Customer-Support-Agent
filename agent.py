from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END,START
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from langchain_core.runnables.graph import MermaidDrawMethod
from dotenv import load_dotenv
import os

# Load environment variables and set OpenAI API key
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')

class State(TypedDict):
    query: str
    category: str
    sentiment: str
    response: str

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


def categorize(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "You are a classifier for Airtel customer support tickets. "
        "Classify the query into exactly one word: Technical, Billing, or General. "
        "Respond with ONLY that one word, no explanation, no markdown.\n\nQuery: {query}"
    )
    chain = prompt | llm
    category = chain.invoke({"query": state["query"]}).content.strip()
    return {"category": category}

def analyze_sentiment(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "Classify the sentiment of this Airtel customer query as exactly one word: "
        "Positive, Neutral, or Negative. Respond with ONLY that word.\n\nQuery: {query}"
    )
    chain = prompt | llm
    sentiment = chain.invoke({"query": state["query"]}).content.strip()
    return {"sentiment": sentiment}

def handle_technical(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "You are an Airtel customer support agent handling a technical issue. "
        "Airtel's official website is https://www.airtel.in and the Airtel Thanks app "
        "lets customers run diagnostics, check network status, and raise complaints. "
        "Airtel customer care can also be reached at 121 (Airtel number) or 198 (toll-free, "
        "for outages and signal issues).\n\n"
        "Give the customer clear troubleshooting steps relevant to their issue first. "
        "If the issue likely needs Airtel's intervention (e.g. outage, SIM/network issue, "
        "router replacement), direct them to the Airtel Thanks app or call 121/198. "
        "Keep the tone helpful and concise, like a real support agent, no placeholders "
        "like [Company Name].\n\nCustomer query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def handle_billing(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "You are an Airtel customer support agent handling a billing query. "
        "Customers can view bills, payment history, and receipts in the Airtel Thanks app "
        "or at https://www.airtel.in/billpay. Payments can be made via the app, website, "
        "UPI, net banking, or at an Airtel store. For billing disputes or refunds, "
        "customers can raise a request through the app or call 121.\n\n"
        "Answer the customer's billing question directly and clearly, like a real support "
        "agent, no placeholders.\n\nCustomer query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def handle_general(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "You are an Airtel customer support agent handling a general inquiry. "
        "Airtel's official website is https://www.airtel.in. Customer care: 121 (from "
        "Airtel number) or 198 (toll-free). Support is also available via the Airtel "
        "Thanks app and on social media (@airtelindia on Twitter/X).\n\n"
        "Answer the customer's question directly and accurately based on what's known "
        "about Airtel. If you don't have the specific detail, point them to "
        "https://www.airtel.in or 121 rather than inventing information.\n\n"
        "Customer query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def escalate(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "You are an Airtel customer support agent. The customer is frustrated. "
        "First, acknowledge their frustration briefly and empathetically. Then give "
        "a real, helpful solution to their query using Airtel's official channels: "
        "Airtel Thanks app, https://www.airtel.in, or customer care at 121/198. "
        "Do not just say 'this has been escalated' — actually try to solve it.\n\n"
        "Customer query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    response += "\n\n(This has also been flagged for priority follow-up by an Airtel support specialist.)"
    return {"response": response}

def route_query(state: State) -> str:
    """Route the query based on its sentiment and category."""
    if state["sentiment"] == "Negative":
        return "escalate"
    elif state["category"] == "Technical":
        return "handle_technical"
    elif state["category"] == "Billing":
        return "handle_billing"
    else:
        return "handle_general"
    

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("categorize", categorize)
workflow.add_node("analyze_sentiment", analyze_sentiment)
workflow.add_node("handle_technical", handle_technical)
workflow.add_node("handle_billing", handle_billing)
workflow.add_node("handle_general", handle_general)
workflow.add_node("escalate", escalate)

# Add edges
workflow.add_edge("categorize", "analyze_sentiment")
workflow.add_conditional_edges(
    "analyze_sentiment",
    route_query,
    {
        "handle_technical": "handle_technical",
        "handle_billing": "handle_billing",
        "handle_general": "handle_general",
        "escalate": "escalate"
    }
)
workflow.add_edge("handle_technical", END)
workflow.add_edge("handle_billing", END)
workflow.add_edge("handle_general", END)
workflow.add_edge("escalate", END)

# Set entry point
workflow.set_entry_point("categorize")

graph= workflow.compile()




def run_customer_support(query: str) -> Dict[str, str]:
    """Process a customer query through the LangGraph workflow.
    
    Args:
        query (str): The customer's query
        
    Returns:
        Dict[str, str]: A dictionary containing the query's category, sentiment, and response
    """
    results = graph.invoke({"query": query})
    return {
        "category": results["category"],
        "sentiment": results["sentiment"],
        "response": results["response"]
    }