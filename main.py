import os

import streamlit as st

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

def main():
    st.title("SQL-Agent App Demo")
    default_session_state = [{"role": "assistant", "content": "How can I help you?"}]

    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state["messages"] = default_session_state
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        st.session_state["api_key"] = st.text_input(
            "Enter your OpenAI API key:",
            type="password",
            value=st.session_state["api_key"],
        )
        st.session_state["llm"] = st.text_input(
            "Enter your prefered OpenAI model:",
            value="gpt-4o-mini",
        )
        st.session_state["database_path"] = st.text_input(
            "Enter your sqlite database path:",
            value="sqlite:///data/database.db",
        )
        if st.button("Clear message history"):
            st.session_state["messages"] = default_session_state

    if st.session_state["api_key"]:
        os.environ["OPENAI_API_KEY"] = st.session_state["api_key"]

        # Initialize database and agent
        db = SQLDatabase.from_uri(st.session_state["database_path"])
        llm = ChatOpenAI(model=st.session_state["llm"], temperature=0)

        agent_executor = create_sql_agent(
            llm, db=db, agent_type="openai-tools", verbose=True
        )

        # Display chat messages
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

        # User input
        user_query = st.chat_input(placeholder="Ask me anything!")

        if user_query:
            st.session_state["messages"].append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)

            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                response = agent_executor.run(user_query, callbacks=[st_cb])
                st.session_state["messages"].append({"role": "assistant", "content": response})
                st.write(response)
    else:
        st.warning("Please enter your OpenAI API key in the sidebar to start chatting.")

if __name__ == "__main__":
    main()