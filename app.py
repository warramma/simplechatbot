import os
from uuid import uuid4


import streamlit as st
from groq import AuthenticationError as GroqAuthenticationError
from groq import RateLimitError as GroqRateLimitError
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from openai import AuthenticationError as OpenAIAuthenticationError
from openai import RateLimitError as OpenAIRateLimitError

from langchain_tavily import TavilySearch

PROVIDERS = {
    "Groq": ("groq", "openai/gpt-oss-120b", "https://console.groq.com/keys"),
    "OpenAI": ("openai", "gpt-4.1-mini", "https://platform.openai.com/api-keys"),
}

SYSTEM_PROMPT = "You are a helpful assistant. Be clear and concise."
tavily_URL = "https://app.tavily.com/home"


def start_chat():
    st.session_state.saver = InMemorySaver()
    st.session_state.thread_id = str(uuid4())
    st.session_state.checkpoint = None
    st.session_state.history = []


def stream_answer(agent, prompt, config, response):
    """Show the answer as model text arrives."""
    answer = ""
    for chunk, metadata in agent.stream(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config,
        stream_mode="messages",
    ):
        if metadata.get("langgraph_node") == "model" and isinstance(chunk, AIMessage):
            if chunk.text:
                answer += chunk.text
                response.markdown(answer + " ▌")
    return answer.strip()


st.set_page_config(page_title="LangChain Chatbot", page_icon="💬")
st.title("A Simple LangChain AI Chatbot")

with st.sidebar:
    provider = st.selectbox("Model provider", list(PROVIDERS), on_change=start_chat)
    model_provider, model_name, key_url = PROVIDERS[provider]
    st.caption(f"Model · {model_name}")
    api_key = st.text_input(
        f"{provider} API key",
        type="password",
        key=f"{provider}_key",
        on_change=start_chat,
    ).strip()
    st.markdown(f"[Get a {provider} API key]({key_url})")
    st.caption(
        "The app server receives your key and uses it to authenticate with your "
        "selected provider. Changing your key or provider starts a new chat."
    )
    tavily_apiKey = st.text_input(
        label="Tavily Api Key",
        type="password",
        on_change=start_chat

    ).strip()
    st.markdown(f"[Get Tavily API Key]({tavily_URL})")
    st.button("New chat", on_click=start_chat)

if "saver" not in st.session_state:
    start_chat()

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not api_key:
    st.info("Choose a model provider and enter its API key in the sidebar.")

if not tavily_apiKey:
    st.info("Enter Tavily Search API Key")

prompt = st.chat_input("Ask a question", disabled=not api_key)
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.status("Generating a response…")
        response = st.empty()
        thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
        # Resume from the last completed turn if a previous attempt failed.
        config = st.session_state.checkpoint or thread_config
        error = None
        try:
            tools=[]
            if tavily_apiKey:
                os.environ["TAVILY_API_KEY"] = tavily_apiKey
                tools.append(TavilySearch())
            else:
                os.environ.pop("TAVILY_API_KEY", None)
            model = init_chat_model(
                model_name,
                model_provider=model_provider,
                api_key=api_key,
                timeout=30,
                max_retries=0,
                **({"reasoning_format": "hidden"} if provider == "Groq" else {}),
            )
            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                checkpointer=st.session_state.saver,
            )
            answer = stream_answer(agent, prompt, config, response)
            if answer:
                st.session_state.checkpoint = agent.get_state(thread_config).config
            else:
                error = "The model returned no text. Try asking again."
        except (GroqAuthenticationError, OpenAIAuthenticationError):
            error = "The provider rejected the API key. Check it in the sidebar."
        except (GroqRateLimitError, OpenAIRateLimitError):
            error = "The provider reported a rate limit or quota issue. Check your API usage."
        except Exception:
            error = "The request failed. Check your API access or try again."

        if error:
            if st.session_state.checkpoint is None:
                start_chat()
            response.empty()
            status.update(label="Request failed", state="error")
            st.error(error)
        else:
            status.update(label="Response complete", state="complete")
            response.markdown(answer)
            st.session_state.history.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer},
            ])
