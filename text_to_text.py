from dotenv import load_dotenv
load_dotenv()

from PIL import Image
import streamlit as st
import io
import os
import google.generativeai as genai

st.set_page_config(page_title="Gen_AI Session", layout="wide")

# Configure API Key
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API Key is missing! Please check your environment variables.")

genai.configure(api_key=api_key)

# Fix CSS Styling
st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 200px !important;  
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

# available_model = ["gemini-1.5-pro-latest"", "gemini-1.5-flash"]
available_model = ["gemini-1.5-pro-latest", "gemini-1.5-flash"]
selected_model = st.selectbox("Select Model:", available_model, index=0)

# Initialize Gemini Model
try:
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    print(f"Error initializing model: {e}")

# Function to get response with streaming
def get_response_gemini_pro(question):
    try:
        response = model.generate_content(question, stream=True)

        if not hasattr(response, "__iter__"):  # Ensure response is iterable
            yield "Error: Response is not iterable. Try removing stream=True."
            return
        
        full_response = ""
        for chunk in response:
            text = getattr(chunk, "text", None)  # Safely get text
            if text:
                full_response += text
                yield full_response  # Yield progressively

    except Exception as e:
        yield f"Error: {e}"  # Handle API errors gracefully


# Function to get response with streaming (for images)
def get_response_gemini_flash(input_text, image):
    image_data = None

    if image:
        try:
            image_bytes = io.BytesIO(image.getvalue())
            image_data = Image.open(image_bytes)
        except Exception as e:
            st.error(f"Error processing image: {e}")
            return

    if not input_text:
        input_text = "Describe the image."

    content = [input_text, image_data] if image_data else input_text
    response = model.generate_content(content, stream=True)

    full_response = ""
    for chunk in response:
        if hasattr(chunk, "text"):  # Ensure chunk has text
            full_response += chunk.text
            yield full_response  # Yield updated response progressively

# Set up Streamlit UI
st.divider()  # Add a divider for better UI separation

if selected_model == "gemini-pro":
    st.header("Gemini Pro - Advanced Text Generation")
    user_input = st.text_area("Enter your question:", key="Input")
    submit = st.button("Ask Your Question")

    if submit and user_input:
        st.subheader("The Response is:")
        response_container = st.empty()

        with st.spinner("Processing... Please wait"):
            for chunk in get_response_gemini_pro(user_input):
                response_container.write(chunk)

elif selected_model == "gemini-1.5-flash":
    st.header("Image & Text Processing")
    user_input = st.text_area("Enter your question (optional):", key="Input")
    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

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
    st.header("Query Processing")
    user_input = st.text_area("Enter your question:", key="Input")
    submit = st.button(" Ask Your Question ")

    if submit and user_input:
        st.subheader("The Response is:")
        response_container = st.empty()

        with st.spinner("Processing... Please wait"):
            for chunk in get_response_gemini_pro(user_input):
                response_container.write(chunk)

st.divider()  # Add a closing divider for better UI separation
