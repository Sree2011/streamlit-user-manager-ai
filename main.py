import streamlit as st

st.title("Streamlit + Ollama Test")

st.write("If you see this, Streamlit is working!")

goal = st.text_input("Enter your goal:")
timeline = st.text_input("Enter timeline (e.g., 2 weeks):")

if st.button("Generate Plan"):
    st.success(f"Goal: {goal}, Timeline: {timeline}")