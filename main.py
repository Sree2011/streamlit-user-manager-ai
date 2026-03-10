import streamlit as st
from user_manager.crud import add_user, list_users
from ai_assistant.ollama_client import ask_with_context

st.title("User Manager + AI Assistant")

# CRUD demo
if st.button("Add Sample User"):
    user = add_user("Priya", "Backend Developer")
    st.success(f"Added {user.name} as {user.role}")

st.write("### Current Users")
users = list_users()
st.write(users)

# Ollama demo with DB integration
query = st.text_area("Ask Ollama (e.g., 'Add a frontend developer named Arjun'):")

if st.button("Send to Ollama"):
    context = "You are an assistant that manages a user database. " \
              "When asked to add a user, respond ONLY in JSON with keys 'name' and 'role'. " \
              "Example: {\"name\": \"Arjun\", \"role\": \"Frontend Developer\"}"

    answer = ask_with_context(context, query)
    st.write("Ollama raw response:", answer)

    # Try to parse Ollama’s JSON output
    import json
    try:
        data = json.loads(answer)
        if "name" in data and "role" in data:
            user = add_user(data["name"], data["role"])
            st.success(f"Added {user.name} as {user.role}")
        else:
            st.warning("Ollama did not return valid JSON with 'name' and 'role'.")
    except Exception as e:
        st.error(f"Failed to parse Ollama response: {e}")