import streamlit as st
from user_manager.crud import add_user, list_users
from ai_assistant.ollama_client import ask_ollama

st.title("User Manager + AI Assistant")

# CRUD demo
if st.button("Add Sample User"):
    user = add_user("Priya", "Backend Developer")
    st.success(f"Added {user.name} as {user.role}")

st.write("### Current Users")
st.write(list_users())

# Ollama demo
query = st.text_area("Ask Ollama:")
if st.button("Send to Ollama"):
    st.write(ask_ollama(query))