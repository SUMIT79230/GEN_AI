from dotenv import load_dotenv
load_dotenv()

from PIL import Image
import streamlit as st
import io
import os
import google.generativeai as genai
import time

st.set_page_config(page_title="Gen_AI Session")

# Configure API Key
genai.configure(api_key=os.getenv("API_KEY"))

# Fix CSS Styling
st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 150px !important;  
    }
    .uploaded-image {
        width: 100px;  
        height: 100px; 
        object-fit: cover;
        border-radius: 10px; 
        display: block;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

available_model = ["gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro-latest"]
selected_model = st.selectbox("Select Model:", available_model, index=0)

# Initialize Gemini Model
model = genai.GenerativeModel(selected_model)

# Function to get response with streaming
def get_response_gemini_pro(question):
    response = model.generate_content(question, stream=True)
    
    full_response = ""
    for chunk in response:
        if chunk.text:
            full_response += chunk.text
            yield full_response  # Yield updated response progressively

# Function to get response with streaming (for images)
def get_response_gemini_flash(input_text, image):
    if image:
        image_bytes = io.BytesIO(image.getvalue())
        image_data = Image.open(image_bytes)
    else:
        image_data = None

    if not input_text:
        input_text = "Describe the image."

    content = [input_text, image_data] if image_data else input_text
    response = model.generate_content(content, stream=True)

    full_response = ""
    for chunk in response:
        if chunk.text:
            full_response += chunk.text
            yield full_response  # Yield updated response progressively

# Set up Streamlit UI
if selected_model == "gemini-pro":
    st.header("Gemini Pro - Advanced Text Generation")
    user_input = st.text_input("Input:", key="Input")
    submit = st.button("Ask Your Question")

    if submit and user_input:
        st.subheader("The Response is:")
        response_container = st.empty()

        with st.spinner("Processing... Please wait"):
            for chunk in get_response_gemini_pro(user_input):
                response_container.write(chunk)

elif selected_model == "gemini-1.5-flash":
    st.header("Gemini Pro Vision - Image to Text Processing")
    user_input = st.text_input("Input:", key="Input")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

    submit = st.button("Process Image for Insights")

    if submit:
        if not uploaded_file and not user_input:
            st.error("Please provide either an image or text input.")
        else:
            st.subheader("The Response is:")
            response_container = st.empty()

            with st.spinner("Processing... Please wait"):
                for chunk in get_response_gemini_flash(user_input, uploaded_file):
                    response_container.write(chunk)

elif selected_model == "gemini-1.5-pro-latest":
    st.header("Gemini 1.5 Pro - Cutting-Edge Multimodal AI")
    user_input = st.text_input("Input:", key="Input")
    submit = st.button("Ask Your Question")
