import time
from pathlib import Path

import requests
import streamlit as st


API_URL = "http://localhost:8000/chat"

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"


st.set_page_config(
    page_title="'The Hobbit' RAG Assistant",
    page_icon=str(ASSETS_DIR / "ring.jpg"),
)


# --------------------------------------------------------------------
# Header
# --------------------------------------------------------------------

left, center, right = st.columns([1, 12, 1])

with center:

    icon_col, text_col = st.columns([2, 12], vertical_alignment="bottom")

    with icon_col:
        st.image(ASSETS_DIR / "ring.png", width=120)

    with text_col:
        st.markdown(
    """
    <h1 style="
        margin:0;
        padding:0;
        white-space: nowrap;
    ">
        'The Hobbit' RAG Assistant
    </h1>

    <p style="
        margin:0;
        color:#777;
        font-size:18px;
    ">
        Azure OpenAI + Azure AI Search RAG Demo
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()


# --------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------------------------
# Display previous messages
# --------------------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

        if "sources" in message:

            with st.expander("Retrieved sources"):

                for source in message["sources"]:

                    st.markdown(
                        f"""
**{source['title']}**

**File:**  
{source['source']}

**Chunk:**  
{source['chunk']}

**Retrieval score:**  
{source['retrieval_score']:.5f}
"""
                    )


# --------------------------------------------------------------------
# Chat input
# --------------------------------------------------------------------

question = st.chat_input("Ask about The Hobbit...")


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.write(question)

    response = requests.post(
        API_URL,
        json={"question": question},
    )

    result = response.json()

    with st.chat_message("assistant"):

        placeholder = st.empty()
        current = ""

        for word in result["answer"].split():
            current += word + " "
            placeholder.markdown(current)
            time.sleep(0.08)

        with st.expander("Retrieved sources"):

            for source in result["sources"]:

                st.markdown(
                    f"""
**{source['title']}**

**File:**  
{source['source']}

**Chunk:**  
{source['chunk']}

**Retrieval score:**  
{source['retrieval_score']:.5f}
"""
                )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )