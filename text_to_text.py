from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai

# Configure API Key
genai.configure(api_key=os.getenv("API_KEY"))

# Initialize Gemini Model
model = genai.GenerativeModel("gemini-pro")

# Function to get response with streaming
def get_response(question):
    response = model.generate_content(question, stream=True)  
    return response 

# Set up Streamlit UI
st.set_page_config(page_title="Q&A")
st.header("1. Text To Text")

# User input field
user_input = st.text_input("Input:", key="Input")
submit = st.button("Ask Your Question")

# Process input and generate response
if submit and user_input:
    st.subheader("The Response is:")
    response_stream = get_response(user_input) 
    response_container = st.empty()  

    full_response = ""  # Store complete response
    for chunk in response_stream:
        full_response += chunk.text  
        response_container.write(full_response) 
