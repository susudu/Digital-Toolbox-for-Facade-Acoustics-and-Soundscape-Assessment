import streamlit as st
import requests

BACKEND = "https://digital-toolbox-api.onrender.com"

st.title("Digital Toolbox Dashboard")

file_id = st.text_input("Enter File ID to View Results:")

if st.button("Load Result"):
    if not file_id:
        st.warning("Please enter a valid file ID.")
    else:
        plot_url = f"{BACKEND}/result/{file_id}"

        st.write("🔗 Plot endpoint:", plot_url)

        # Request the image file
        response = requests.get(plot_url)

        if response.status_code == 200:
            st.image(response.content, caption=f"Processing Result {plot_url}")
        else:
            st.warning("⛔ Result not ready yet or file_id not found.")
