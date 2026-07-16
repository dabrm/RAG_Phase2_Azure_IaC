import streamlit as st
import requests


API_URL = "http://localhost:8000/chat"


st.set_page_config(
    page_title="'The Hobbit' RAG Assistant",
    page_icon="🧙"
)


st.title("🧙 'The Hobbit' RAG Assistant")

st.caption(
    "Azure OpenAI + Azure AI Search Hybrid RAG Demo"
)


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

        if "sources" in message:
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(
                        f"""
                        **{source['title']}**

                        Chunk: {source['chunk']}  
                        Retrieval score: {source['retrieval_score']:.5f}
                        """
                    )


question = st.chat_input(
    "Ask about The Hobbit..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)


    response = requests.post(
        API_URL,
        json={
            "question": question
        }
    )

    result = response.json()


    with st.chat_message("assistant"):

        st.write(
            result["answer"]
        )

        with st.expander(
            "📚 Retrieved sources"
        ):

            for source in result["sources"]:

                st.write(
                    f"""
                    **{source['title']}**

                    File:
                    {source['source']}

                    Chunk:
                    {source['chunk']}

                    Retrieval score:
                    {source['retrieval_score']:.5f}
                    """
                )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"]
        }
    )