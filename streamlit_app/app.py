import streamlit as st
import requests

API_URL = "https://3w64re5ngk.execute-api.us-east-1.amazonaws.com/ask"

st.set_page_config(page_title="AI Practice Test Assistant", page_icon="🤖")
st.title("🤖 AI Practice Test Assistant")
st.markdown("Ask any AWS-related question and get an instant AI-powered answer.")

question = st.text_input("Enter your question:")

if st.button("Get Answer") and question:
    with st.spinner("Thinking..."):
        res = requests.post(API_URL, json={"question": question})
        if res.status_code == 200:
            data = res.json()
            st.success(data['answer'])
            st.caption(f"Source: {data['source']}")
        else:
            st.error("Something went wrong.")