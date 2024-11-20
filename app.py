import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Image
import os
import json
from PIL import Image

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=REGION)

# Change page title
st.set_page_config(page_title="Receipt OCR")

# Display the banner image
banner_image_path = "image/hkairport-logo.png"
st.image(banner_image_path, use_container_width=True)

# Streamlit app
st.title("Demo of Receipt OCR with Google Gemini API")

# Create columns for file uploaders
col1, col2 = st.columns(2)
with col1:
    st.session_state['uploaded_file1'] = st.file_uploader("Upload Image 1", key="file1")
with col2:
    st.session_state['uploaded_file2'] = st.file_uploader("Upload Image 2", key="file2")

# Retrieve uploaded files from session state
uploaded_files = [
    st.session_state.get('uploaded_file1'),
    st.session_state.get('uploaded_file2')
]
uploaded_files = [f for f in uploaded_files if f is not None]

if uploaded_files is not None:
    # Display the uploaded images
    image = Image.open(uploaded_files)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Create the generative model
    generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

    prompt = """Convert the provided images into dumped JSON body. Return shop name, order date (null if not present on the receipt), and final payment amount only.
        Requirements:
        - Output: Return solely the JSON content without any additional explanations or comments.
        - Use this JSON schema: {"shop_name": "string", "order_date": "string", "payment_total": "string"}
        - No Delimiters: Do not use code fences or delimiters like ```json.
        - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
        - Shop Name Format: Keep the first row of detected texts only, using 'UTF-8' decoding.
        - Order Date Format: Change to date format (YYYY-MM-DD) if detected.
        - Final Payment Format: Do not include detected texts.
        """

    # Generate content using the generative model
    response = generative_multimodal_model.generate_content(prompt, uploaded_files[0])

    content = response.text.encode().decode('utf-8')

    # Display the result in the second column
    # with col2:
    #     # Parse the content as JSON and display it in a code block
    #     json_response = json.loads(content)
    #     pretty_json = json.dumps(json_response, indent=4)
    #     st.code(pretty_json, language='json')