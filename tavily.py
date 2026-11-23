import os 
from langchain_tavily import TavilySearch 
from langchain.chat_models import init_chat_model 
from langchain.agents import create_agent
from langchain.messages import HumanMessage

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILYA_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_Key")

#model = init_chat_model(model="openai/gpt-oss-120b",model_provider="groq")
model = init_chat_model(model="gpt-5.4-mini",model_provider="openai")

tavily_tool = TavilySearch() 

agent = create_agent(
    model=model, 
    tools=[tavily_tool],
    system_prompt="You are a helpful assistant"
)

while True: 
    user_input = input("User:")
    response = agent.invoke({
        "messages":[
            HumanMessage(content=user_input)
        ]
    })
    print(f"AI:{response["messages"][-1].content}")

