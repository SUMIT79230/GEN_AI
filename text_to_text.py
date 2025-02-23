from dotenv import load_dotenv
load_dotenv()

from PIL import Image
import streamlit as st
import io
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

available_model = ["gemini-pro","gemini-1.5-flash","gemini-1.5-pro-latest"]
selected_model = st.selectbox("Select Model : ",available_model,index = 0)

# Initialize Gemini Model
model = genai.GenerativeModel(selected_model)

# Function to get response with streaming from gemini_pro
def get_response_gemini_pro(question):
    response = model.generate_content(question, stream=True)  
    return response 

# Function to get response with streaming from gemini_pro_vision
def get_response_gemini_flash(input,image):
    if image is not None:
        image_bytes = io.BytesIO(image.getvalue())  # Convert file to bytes
        image_data = Image.open(image_bytes)
    else:
        image_data = None
    
    if input != "":
        response = model.generate_content([input, image_data])
    else:
        response = model.generate_content(image_data)
    return response.text

# Set up Streamlit UI
if selected_model == "gemini-pro":
    st.header("Gemini Pro - Advanced Text Generation")
    user_input = st.text_input("Input:", key="Input")
    submit = st.button("Ask Your Question")
    # Process input and generate response
    if submit and user_input:
        st.subheader("The Response is:")
        response_stream = get_response_gemini_pro(user_input) 
        response_container = st.empty()  

        full_response = ""  # Store complete response
        for chunk in response_stream:
            full_response += chunk.text  
            response_container.write(full_response) 
elif selected_model == "gemini-1.5-flash":
    
    st.header("Gemini Pro Vision - Image to Text Processing")
    user_input = st.text_input("Input:", key="Input")
    uploaded_file = st.file_uploader("Choose an image...",type = ["jpg","jpeg","png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image,caption = "Uploaded Image ",use_container_width = True)
    submit = st.button("Tell an about the image")
    # Process input and generate response
    if submit :
        st.subheader("The Response is:")
        response_stream = get_response_gemini_flash(user_input,uploaded_file) 
        response_container = st.empty()  

        full_response = ""  # Store complete response
        for chunk in response_stream:
            full_response += chunk  
            response_container.write(full_response) 
elif selected_model == "gemini-1.5-pro-latest":
    st.header("Gemini 1.5 Pro - Cutting-Edge Multimodal AI")
    user_input = st.text_input("Input:", key="Input")
    submit = st.button("Ask Your Question")

