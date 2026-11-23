[Live Chatbot Link](https://ai-chatbot-ethan-nawaz26.streamlit.app/)

# Deploy a Streaming LangChain Chatbot

![Deploy a Streaming Chatbot — LangChain + Streamlit](assets/streamlit-chatbot-youtube-banner.png)

This Streamlit demo uses a LangChain agent with streaming responses and short-term memory. The viewer chooses Groq or OpenAI and enters one API key in the sidebar.

| Provider | Model |
| --- | --- |
| Groq | `openai/gpt-oss-120b` |
| OpenAI | `gpt-4.1-mini` |

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from this folder.

```bash
uv venv --python 3.13
uv pip install -r requirements.txt
uv run --no-project streamlit run app.py
```

Open the local URL printed in the terminal and enter a provider API key. API usage follows the selected provider's pricing and limits.

## Publish a public URL

1. Push the contents of this folder to a public GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and choose **Create app**.
3. Select your repository and branch, set the main file path to `app.py`, and select Python 3.13 in **Advanced settings**. Viewers enter their own keys through the app.
4. Deploy, then open the resulting `streamlit.app` URL in a private browser window. Try a prompt before sharing the link.

[Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

## Demo prompts

1. **Streaming.** “Explain retrieval-augmented generation in three short paragraphs.”
2. **Memory.** “My name is Nawaz and I live in Peoria, Illinois.” Then ask, “What city did I say I live in?”
3. **New chat.** Select **New chat** and ask the memory question again.

## How the app works

- Each browser session has its own `InMemorySaver` and thread ID. Each request submits the newest message, and the agent reads the earlier turns from its checkpoint. Reloading the page, restarting the app, or selecting **New chat** starts a fresh conversation.
- The agent streams model text with `stream_mode="messages"`. Streamlit updates the answer in place as text arrives.
- The app server receives the password-field value and passes it to the selected provider client. The app keeps the key out of chat history and checkpoints. Use an API key only with a deployment you trust, or run the demo locally.

## Streamlit widgets and components

| Widget or component | What it does in this chatbot |
| --- | --- |
| [`st.selectbox()`](https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox) | Displays a dropdown for choosing Groq or OpenAI. The selection determines which model and API key field the app uses. |
| [`st.text_input()`](https://docs.streamlit.io/develop/api-reference/widgets/st.text_input) | Collects the selected provider’s API key. Setting `type="password"` masks the characters on screen. |
| [`st.button()`](https://docs.streamlit.io/develop/api-reference/widgets/st.button) | Displays **New chat**. Clicking it clears the visible history and starts a new conversation thread. |
| [`st.chat_input()`](https://docs.streamlit.io/develop/api-reference/chat/st.chat_input) | Collects the user’s prompt. The app disables it while the API key field is empty. |
| [`st.chat_message()`](https://docs.streamlit.io/develop/api-reference/chat/st.chat_message) | Creates a message container for the user or assistant. The app also uses it to redraw earlier messages. |
| [`st.sidebar`](https://docs.streamlit.io/develop/api-reference/layout/st.sidebar) | Places the provider selector, API key field, and **New chat** button alongside the conversation. |
| [`st.empty()`](https://docs.streamlit.io/develop/api-reference/layout/st.empty) | Creates a placeholder inside the assistant’s message. The app updates the same placeholder with `response.markdown(...)` as each text chunk arrives. |
| [`st.status()`](https://docs.streamlit.io/develop/api-reference/status/st.status) | Shows that a response is being generated. The app calls `status.update()` to mark it complete or failed. |
| [`st.info()`](https://docs.streamlit.io/develop/api-reference/status/st.info) | Prompts the user to select a provider and enter an API key. |
| [`st.error()`](https://docs.streamlit.io/develop/api-reference/status/st.error) | Displays a request error, such as a rejected key or a rate limit. |
| [`st.title()`](https://docs.streamlit.io/develop/api-reference/text/st.title) | Displays the main chatbot heading. |
| [`st.caption()`](https://docs.streamlit.io/develop/api-reference/text/st.caption) | Displays the selected model ID and explanatory text in the sidebar. |
| [`st.markdown()`](https://docs.streamlit.io/develop/api-reference/text/st.markdown) | Renders formatted messages and the provider’s API key link. |
| [`st.session_state`](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) | Keeps the visible chat history, thread ID, and agent checkpointer available across Streamlit reruns within the browser session. |
| [`st.set_page_config()`](https://docs.streamlit.io/develop/api-reference/config/st.set_page_config) | Sets the browser tab title and icon. |

[Browse the full Streamlit API reference](https://docs.streamlit.io/develop/api-reference).
