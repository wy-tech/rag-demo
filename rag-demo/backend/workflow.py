from typing import List
from typing_extensions import TypedDict

from langchain.schema import Document
from langgraph.graph import END, StateGraph, START

from backend.nodes import filter_parallel,multi_query_retriever, decomposition_retriever, generate, get_card_type, get_payment_type, construct_filter

class GraphState(TypedDict):
    question: str
    generation: str
    multi_query_docs: List[Document]
    decomposition_docs: List[Document]
    card_type: List[str] 
    payment_type: str
    filter_list = List[str]
    generation: str

def create_workflow():
    workflow = StateGraph(GraphState)
    # Define the nodes
    workflow.add_node("filter_parallel", filter_parallel)  # generatae
    workflow.add_node("multi_query_retriever", multi_query_retriever)  # transform_query
    workflow.add_node("decomposition_retriever", decomposition_retriever)  # transform_query
    workflow.add_node("generate", generate)  # transform_query

    # # Build graph
    workflow.add_edge(START,"filter_parallel")
    workflow.add_edge(START,"filter_parallel")

    workflow.add_edge("filter_parallel","multi_query_retriever")
    workflow.add_edge("filter_parallel","decomposition_retriever")

    workflow.add_edge("decomposition_retriever","generate")
    workflow.add_edge("multi_query_retriever","generate")

    workflow.add_edge("generate",END)

    app = workflow.compile()
    return app
