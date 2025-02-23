from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai

st.set_page_config(page_title="Q&A")
# Configure API Key
genai.configure(api_key=os.getenv("API_KEY"))

# for model in genai.list_models():
#     print(model.name);

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 150px !important;  /* Adjust the width */
    }
    </style>
    """,
    unsafe_allow_html=True
)

available_model = ["gemini-pro","gemini-pro-vision","gemini-1.5-pro-latest"]
selected_model = st.selectbox("Select Model : ",available_model,index = 0)

# Initialize Gemini Model
model = genai.GenerativeModel(selected_model)

# Set up Streamlit UI
if selected_model == "gemini-pro":
    st.header("Gemini Pro - Advanced Text Generation")
elif selected_model == "gemini-pro-vision":
    st.header("Gemini Pro Vision - Image to Text Processing")
elif selected_model == "gemini-1.5-pro-latest":
    st.header("Gemini 1.5 Pro - Cutting-Edge Multimodal AI")


# Function to get response with streaming
def get_response(question):
    response = model.generate_content(question, stream=True)  
    return response 

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
