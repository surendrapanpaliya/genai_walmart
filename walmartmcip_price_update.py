
import requests
import re

from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

# Function to extract number from text like "445 INR"
def extract_number(text):
    match = re.search(r"(\d+(\.\d+)?)", text)
    if match:
        return float(match.group(1))
    else:
        raise ValueError("No valid number found in input.")

# MCP API Call
def call_mcp_price_update(input_text):
    product_id = "WM12345"  # Example product
    new_price = extract_number(input_text)

    response = requests.post("http://localhost:8000/update_price", json={
        "product_id": product_id,
        "new_price": new_price
    })
    return response.json()

# Define MCP Tool
mcp_tool = Tool(
    name="UpdatePriceTool",
    func=call_mcp_price_update,
    description="Use this tool to update the product price via MCP server. Pass the target price as input."
)

# Use ChatOpenAI LLM
llm = ChatOpenAI(temperature=0)

# Load ReAct Prompt from LangChain Hub
prompt = hub.pull("hwchase17/react")

# Create ReAct Agent
agent = create_react_agent(llm, tools=[mcp_tool], prompt=prompt)

# Use AgentExecutor with .invoke()
agent_executor = AgentExecutor(agent=agent, tools=[mcp_tool], verbose=True)

# Run the Agent
result = agent_executor.invoke({"input": "Competitor dropped price to 450 INR. Lower our price to 445 INR."})

print("\n=== Final Result ===")
print(result)
