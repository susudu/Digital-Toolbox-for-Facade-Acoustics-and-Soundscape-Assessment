import streamlit as st
import requests

BACKEND = "https://your-backend-url.onrender.com"

st.title("Digital Toolbox Dashboard")

file_id = st.text_input("Enter File ID to View Results:")

if st.button("Load Result"):
    plot_url = f"{BACKEND}/result/{file_id}"
    response = requests.get(plot_url)

    if response.status_code == 200:
        st.image(plot_url, caption="Processing Result")
    else:
        st.warning("Result not ready yet or file_id not found.")
