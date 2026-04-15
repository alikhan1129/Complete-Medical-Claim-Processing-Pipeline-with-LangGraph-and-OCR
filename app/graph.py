import asyncio
import logging
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END, START
from app.agents.segregator import classify_pages
from app.agents.id_agent import extract_id_data
from app.agents.discharge_agent import extract_discharge_summary
from app.agents.bill_agent import extract_itemized_bill
from app.agents.aggregator import aggregate_results

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    claim_id: str
    pages: List[Dict[str, Any]]
    page_map: Dict[str, List[str]]
    identity_data: Optional[Dict[str, Any]]
    discharge_data: Optional[Dict[str, Any]]
    bill_data: Optional[Dict[str, Any]]
    final_response: Optional[Dict[str, Any]]

async def segregator_node(state: AgentState) -> Dict[str, Any]:
    """Node for page classification."""
    logger.info("Running Segregator Agent...")
    page_map = await classify_pages(state["pages"])
    return {"page_map": page_map}

async def extraction_node(state: AgentState) -> Dict[str, Any]:
    """Node for parallel extraction from relevant pages."""
    logger.info("Running Extraction Agents...")
    
    page_map = state["page_map"]
    pages = state["pages"]
    
    def get_text_for_labels(labels: List[str]) -> str:
        relevant_text = []
        for page_num_str, page_labels in page_map.items():
            if any(label in page_labels for label in labels):
                page_num = int(page_num_str)
                # Find page text
                for p in pages:
                    if p["page_number"] == page_num:
                        relevant_text.append(p["text"])
        return "\n\n".join(relevant_text)

    id_text = get_text_for_labels(["identity_document", "claim_forms", "discharge_summary", "itemized_bill"])
    discharge_text = get_text_for_labels(["discharge_summary"])
    bill_text = get_text_for_labels(["itemized_bill", "cash_receipt"])

    # Run extraction agents in parallel
    id_task = extract_id_data(id_text)
    discharge_task = extract_discharge_summary(discharge_text)
    bill_task = extract_itemized_bill(bill_text)
    
    identity_data, discharge_data, bill_data = await asyncio.gather(id_task, discharge_task, bill_task)
    
    return {
        "identity_data": identity_data,
        "discharge_data": discharge_data,
        "bill_data": bill_data
    }

async def aggregator_node(state: AgentState) -> Dict[str, Any]:
    """Node for results aggregation."""
    logger.info("Running Aggregator Agent...")
    final_response = aggregate_results(
        state["claim_id"],
        state["identity_data"],
        state["discharge_data"],
        state["bill_data"]
    )
    return {"final_response": final_response}

def create_graph():
    """Builds the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("segregator", segregator_node)
    workflow.add_node("extraction", extraction_node)
    workflow.add_node("aggregator", aggregator_node)

    # Add Edges
    workflow.add_edge(START, "segregator")
    workflow.add_edge("segregator", "extraction")
    workflow.add_edge("extraction", "aggregator")
    workflow.add_edge("aggregator", END)

    return workflow.compile()

# Initialize the graph
app_graph = create_graph()

async def process_claim(claim_id: str, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper to run the graph."""
    initial_state = {
        "claim_id": claim_id,
        "pages": pages,
        "page_map": {},
        "identity_data": None,
        "discharge_data": None,
        "bill_data": None,
        "final_response": None
    }
    
    result = await app_graph.ainvoke(initial_state)
    return result.get("final_response")
