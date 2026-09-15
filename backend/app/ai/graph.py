from langgraph.graph import StateGraph, START, END
from app.ai.graph_state import ResearchAgentState
from app.ai.graph_nodes import (
    extract_intent_node,
    filter_candidates_node,
    relax_criteria_node,
    gather_review_evidence_node,
    synthesize_recommendation_node,
)

GRAPH_ACTIONS = {
    "RELAX_CRITERIA": "relax_criteria",
    "END_NO_PRODUCTS": "end_no_products",
    "GATHER_REVIEWS": "gather_reviews",
    "EXTRACT_INTENT": "extract_intent",
    "FILTER_CANDIDATES": "filter_candidates",
    "SYNTHESIZE": "synthesize",
}

def candidate_check_condition(state: ResearchAgentState) -> str:
    """
    Decides whether to gather reviews or relax criteria if too few products matched.
    """
    candidates = state.get("candidates", [])
    retry_count = state.get("retry_count", 0)
    
    # If fewer than 2 candidates and we haven't retried yet, relax budget
    if len(candidates) < 2 and retry_count < 1:
        return GRAPH_ACTIONS["RELAX_CRITERIA"]
    
    # If 0 candidates even after retry, terminate early
    if len(candidates) == 0:
        return GRAPH_ACTIONS["END_NO_PRODUCTS"]
    
    return GRAPH_ACTIONS["GATHER_REVIEWS"]
    
    

def create_research_graph():
    builder = StateGraph(ResearchAgentState)
    
    # 1. Add All Nodes
    builder.add_node(GRAPH_ACTIONS["EXTRACT_INTENT"], extract_intent_node)
    builder.add_node(GRAPH_ACTIONS["FILTER_CANDIDATES"], filter_candidates_node)
    builder.add_node(GRAPH_ACTIONS["RELAX_CRITERIA"], relax_criteria_node)
    builder.add_node(GRAPH_ACTIONS["GATHER_REVIEWS"], gather_review_evidence_node)
    builder.add_node(GRAPH_ACTIONS["SYNTHESIZE"], synthesize_recommendation_node)
    
    # 2. Linear Pipeline: Start -> Extract -> Filter
    builder.add_edge(START, GRAPH_ACTIONS["EXTRACT_INTENT"])
    builder.add_edge(GRAPH_ACTIONS["EXTRACT_INTENT"], GRAPH_ACTIONS["FILTER_CANDIDATES"])
    
    # 3. Conditional Branch: Check candidate count
    builder.add_conditional_edges(
        GRAPH_ACTIONS["FILTER_CANDIDATES"],
        candidate_check_condition,
        {
            GRAPH_ACTIONS["RELAX_CRITERIA"]: GRAPH_ACTIONS["RELAX_CRITERIA"],
            GRAPH_ACTIONS["GATHER_REVIEWS"]: GRAPH_ACTIONS["GATHER_REVIEWS"],
            GRAPH_ACTIONS["END_NO_PRODUCTS"]: END
        }
    )
    
    # 4. Self-Healing Loop: Relax -> Re-filter
    builder.add_edge(GRAPH_ACTIONS["RELAX_CRITERIA"], GRAPH_ACTIONS["FILTER_CANDIDATES"])
    
    # 5. Reviews -> Synthesis -> End
    builder.add_edge(GRAPH_ACTIONS["GATHER_REVIEWS"], GRAPH_ACTIONS["SYNTHESIZE"])
    builder.add_edge(GRAPH_ACTIONS["SYNTHESIZE"], END)
    
    # 6. Compile executable graph
    return builder.compile()
    

research_graph = create_research_graph()