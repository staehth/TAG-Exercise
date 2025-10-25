# app_frontend.py
import streamlit as st
import requests
import os

# Backend URL (adjust if running via Docker Compose)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/query")

st.set_page_config(page_title="Text-to-SQL Demo", page_icon="🧠")
st.title("🧠 Text-to-SQL Natural Language Query")

st.markdown("""
Ask a question about your demo database and get a grounded, factual answer.
""")

question = st.text_area("Enter your question:", height=100)

if st.button("Run Query"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": question})
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Answer:")
                    st.markdown(data["answer"])
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {e}")
