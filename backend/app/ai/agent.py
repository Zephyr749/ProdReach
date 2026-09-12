import json
from app.ai.client import client
from app.core.config import app_settings
from app.ai.tools import (
    AVAILABLE_TOOLS,
    tool_search_products,
    tool_get_product_details,
    tool_search_reviews,
)


AGENT_SYSTEM_PROMPT = """You are an autonomous product research agent for Indian marketplace products.
    Your goal is to answer the user's shopping request by autonomously searching products, inspecting specs, and verifying customer reviews.
    Guidelines:
        1. Always search for products first before making assumptions.
        2. If the user mentions qualitative requirements (e.g. "battery life", "mic quality", "heating"), search customer reviews for the candidate products to verify claims.
        3. Base all recommendations strictly on verified tool results.
        4. When finished, provide a clear, evidence-backed recommendation with trade-offs.
"""

TOOL_MAP = {
    "search_products": tool_search_products,
    "get_product_details": tool_get_product_details,
    "search_reviews": tool_search_reviews,
}

async def run_product_research_agent(user_query: str, max_steps: int = 7) -> str:
    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    
    for step in range(max_steps):
        print(f"\n---Agent Step: {step + 1} ---")
        
        # 1. Ask the model what to do next
        response = client.chat.completions.create(
            model= app_settings.agent_model_name,
            messages= messages,
            tools= AVAILABLE_TOOLS,
            tool_choice= "auto",
            # temperature= 0.0
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        # 2. Check if the model wants to call tools or it's done
        if not message.tool_calls:
            print("Agent completed research")
            return message.content
        
        # 3. Execute all tool calls requested by model
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            
            print(f"Invoking tool: {fn_name}({fn_args})")
            
            tool_fn = TOOL_MAP.get(fn_name)
            
            if tool_fn:
                try:
                    tool_result = await tool_fn(**fn_args)
                except Exception as e:
                    tool_result = {"error": str(e)}
                    
            else:
                tool_result = {"error": f"Tool {fn_name} is not implemented"}
            
            print("Tool result: ", tool_result)
            # 4. Feed tool result back to the model as a tool role message
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })
            
    return "Agent reached maximum step limit before concluding."


