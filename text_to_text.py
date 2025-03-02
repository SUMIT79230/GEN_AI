from dotenv import load_dotenv
load_dotenv()

from PIL import Image
import streamlit as st
import io
import os
import google.generativeai as genai
import time

st.set_page_config(page_title="Gen_AI Session", layout="wide")

# Configure API Key
api_key = os.getenv("API_KEY")
if not api_key:
    st.error("❌ API Key is missing! Please check your environment variables.")
    st.stop()

genai.configure(api_key=api_key)

# Fix CSS Styling for better UI
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
            min-width: 220px; 
            max-width: 250px;
    }
    div[data-baseweb="select"] {
        width: 190px !important;  
    }
    .uploaded-image {
        width: 100px;  
        height: 100px; 
        object-fit: cover;
        border-radius: 10px; 
        display: block;
        margin: auto;
    }
    textarea {
        height: 80px !important;
        font-size: 16px !important;
    }
        .stButton>button {
            font-size: 14px !important; /* Decrease font size */
            padding: 6px 12px !important; /* Reduce padding */
            border-radius: 8px !important; /* Rounded corners */
            background-color: #0072B5 !important; /* Custom blue */
            color: white !important;
            border: none !important;
        }
        .stButton>button:hover {
            background-color: #005A8D !important;
        }
        .fixed-image {{
            width: 200px !important;
            height: 200px !important;
            object-fit: cover;
            border-radius: 10px;
            display: block;
            margin: auto;
            border: 2px solid #ccc;
        }}
        .setting-bar {
        position: absolute;
        top: 2px;
        left: 10px;
        font-size: 20px;
        font-weight: bold;
        z-index: 999;  /* Ensure it's always on top */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Model Selection Mapping
model_mapping = {
    "📄 Text Processing": "gemini-1.5-pro-latest",
    "🖼️ Image & Text Processing": "gemini-1.5-flash"
}

with st.sidebar:
    st.markdown(
        "<div style='text-align: left; font-weight: bold; font-size: 22px;margin-bottom:-50px'>🔽 Select a Model</div>",
        unsafe_allow_html=True
    )
    model_options = list(model_mapping.keys())
    selected_model_label = st.selectbox(
        "",
        model_options, 
        index=0 
    )
    selected_model = model_mapping[selected_model_label]


# Initialize Gemini Model
try:
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"❌ Error initializing model: {e}")
    st.stop()

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
            st.error(f"❌ Error processing image: {e}")
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

col1 = st.container()  # Main input area
col2 = st.container()  # Buttons & File Upload below input

if selected_model == "gemini-1.5-pro-latest":
    with col1:
        user_input = st.text_area("Enter your question:", key="Input")

    with col2:
        st.write("")  # Space for better alignment
        submit = st.button("🚀 Ask Your Question")

    if submit :
        if not user_input :
            error_message = st.error("⚠️ Please Ask Question in Input Box ")
            time.sleep(2) 
            error_message.empty()
        else :    
            st.subheader("🤖 Response :")
            response_container = st.empty()

            with st.spinner("⏳ Processing... Please wait"):
                with st.expander("🔹 Click to Expand Response", expanded=True):
                    for chunk in get_response_gemini_pro(user_input):
                        response_container.write(chunk)

elif selected_model == "gemini-1.5-flash":

    with col1:
        user_input = st.text_area("Enter your question (optional):", key="Input")
    
    with col2:
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="📌 Uploaded Image", width=200)

    submit = st.button("🔍 Process Image For Insight")

    if submit :
        if not uploaded_file :
            error_message = st.error("⚠️ Please provide an image ")
            time.sleep(2) 
            error_message.empty()
        elif not uploaded_file and not user_input:
            error_message = st.error("⚠️ Please provide either an image or text input.")
            time.sleep(2) 
            error_message.empty()
        else:
            st.subheader("🤖 Response:")
            response_container = st.empty()

            with st.spinner("⏳ Processing... Please wait"):
                with st.expander("🔹 Click to Expand Response", expanded=True):
                    for chunk in get_response_gemini_flash(user_input, uploaded_file):
                        response_container.write(chunk)

st.divider()
