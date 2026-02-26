"""
Agentic RAG for Health Insurance Policy Verification.
Uses LangGraph to build a stateful agent that decides when to retrieve,
grades document relevance, rewrites queries, and generates answers.
"""

from typing import Literal

from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from config import LLM_MODEL
from retriever import retrieve_policy_info

# --- System Prompt ---
SYSTEM_PROMPT = """You are an expert health insurance policy assistant for HealthShield Plus,
offered by TN IMPACT Insurance Corporation.

Your role:
- Answer questions about insurance policy coverage, premiums, claims, exclusions, and procedures.
- Always base your answers on the retrieved policy documents.
- If the retrieved documents do not contain the answer, say so clearly.
- Be precise with numbers (premiums, limits, co-payments, timelines).
- When quoting policy terms, reference the specific section when possible.
- If the question is not related to health insurance, politely redirect the user.

Do NOT make up information. Only use facts from the retrieved policy documents."""


# --- LLM Setup ---
def get_llm():
    """Get ChatOllama LLM instance (mistral with tool calling support)."""
    return ChatOllama(
        model=LLM_MODEL,
        temperature=0,
    )


# --- Graph Nodes ---

def generate_or_retrieve(state: MessagesState):
    """First node: LLM decides whether to call the retriever tool or respond directly."""
    llm = get_llm()
    llm_with_tools = llm.bind_tools([retrieve_policy_info])
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def grade_documents(state: MessagesState):
    """Grade retrieved documents for relevance to the original question."""
    llm = get_llm()

    messages = state["messages"]

    # Find the original user question
    user_question = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            user_question = msg.content
            break

    # Find the tool response (last ToolMessage)
    tool_content = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "tool":
            tool_content = msg.content
            break

    if not tool_content:
        # No tool response found, go to generate
        return {"messages": []}

    grade_prompt = f"""You are grading the relevance of retrieved documents to a user question.

User question: {user_question}

Retrieved documents:
{tool_content[:3000]}

Is the retrieved content relevant to the user's question?
Answer with ONLY one word: "yes" or "no"."""

    grade_response = llm.invoke([HumanMessage(content=grade_prompt)])
    grade_text = grade_response.content.strip().lower()

    if "yes" in grade_text:
        return {"messages": []}
    else:
        # Documents not relevant - add a message indicating we need to rewrite
        return {"messages": [HumanMessage(content=f"The retrieved documents were not relevant. Please rewrite this question for better retrieval: {user_question}")]}


def rewrite_question(state: MessagesState):
    """Rewrite the question for better retrieval results."""
    llm = get_llm()
    messages = state["messages"]

    # Find the original user question
    user_question = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            user_question = msg.content
            break

    rewrite_prompt = f"""You are a question rewriter. Your goal is to rewrite the following question
to be more specific and better suited for retrieving health insurance policy information from a vector database.

Original question: {user_question}

Rewrite the question to improve retrieval. Output only the rewritten question, nothing else."""

    response = llm.invoke([HumanMessage(content=rewrite_prompt)])
    return {"messages": [HumanMessage(content=response.content)]}


def generate_answer(state: MessagesState):
    """Generate the final answer using the original question and retrieved context."""
    llm = get_llm()
    messages = state["messages"]

    # Find the original user question
    user_question = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            user_question = msg.content
            break

    # Find tool responses for context
    context_parts = []
    for msg in messages:
        if hasattr(msg, "type") and msg.type == "tool":
            context_parts.append(msg.content)
    context = "\n\n".join(context_parts)

    generation_prompt = f"""{SYSTEM_PROMPT}

Based on the following retrieved policy documents, answer the user's question.

Retrieved Policy Information:
{context[:5000]}

User Question: {user_question}

Provide a clear, accurate, and helpful answer based only on the retrieved policy information."""

    response = llm.invoke([HumanMessage(content=generation_prompt)])
    return {"messages": [response]}


# --- Routing Functions ---

def route_after_grading(state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
    """Route based on document relevance grade."""
    messages = state["messages"]
    last_message = messages[-1]

    # If the last message is a HumanMessage with rewrite request, go to rewrite
    if isinstance(last_message, HumanMessage) and "not relevant" in last_message.content.lower():
        return "rewrite_question"
    return "generate_answer"


# --- Build the Graph ---

def build_agent_graph():
    """Construct the LangGraph agentic RAG workflow."""
    workflow = StateGraph(MessagesState)

    # Add nodes
    workflow.add_node("generate_or_retrieve", generate_or_retrieve)
    workflow.add_node("retrieve", ToolNode([retrieve_policy_info]))
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("rewrite_question", rewrite_question)
    workflow.add_node("generate_answer", generate_answer)

    # Add edges
    workflow.add_edge(START, "generate_or_retrieve")

    # After generate_or_retrieve: either call tool or end (direct response)
    workflow.add_conditional_edges(
        "generate_or_retrieve",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )

    # After retrieval, grade the documents
    workflow.add_edge("retrieve", "grade_documents")

    # After grading, either generate or rewrite
    workflow.add_conditional_edges(
        "grade_documents",
        route_after_grading,
        {
            "generate_answer": "generate_answer",
            "rewrite_question": "rewrite_question",
        },
    )

    # After rewriting, retrieve again
    workflow.add_edge("rewrite_question", "generate_or_retrieve")

    # After generating answer, end
    workflow.add_edge("generate_answer", END)

    # Compile the graph
    graph = workflow.compile()
    return graph


def query_agent(question: str) -> str:
    """Run a question through the agentic RAG pipeline and return the answer."""
    graph = build_agent_graph()
    result = graph.invoke({"messages": [HumanMessage(content=question)]})

    # Extract the final AI message
    final_message = result["messages"][-1]
    return final_message.content
