import streamlit as st
from backend.workflow import create_workflow

# Import workflow from backend
app = create_workflow()

# Streamlit App
st.title("VISA Offers and Perks Assistant")
st.markdown(
    "<h3 style='font-size: 18px;'>Backed by data from <a href='https://www.visa.com.sg/en_sg/visa-offers-and-perks/' target='_blank'>VISA Offers + Perks</a></h3>", 
    unsafe_allow_html=True
)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Ask me something about VISA offers:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_container = st.empty()
        response_text = ""
        # Stream response from LangGraph
        # currently not using history (st.session_state.messages) as it degrades performance. I make the trade-off of removing muilti-turn capabilities for this assistant.
        for message, metadata in app.stream({"question": user_input, "history": [{"role": "user", "content": user_input}]}, stream_mode="messages"): 
            if metadata["langgraph_node"] == "generate":
                response_text += message.content
                response_container.markdown(response_text)

        # Save the final assistant message to the session
        st.session_state.messages.append({"role": "assistant", "content": response_text})