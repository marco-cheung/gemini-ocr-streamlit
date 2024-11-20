import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
import os
import json
import PIL.Image

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

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


# Create two columns
col1, col2 = st.columns(2)

with col1:
    uploaded_file1 = st.file_uploader("Shop Invoice", key="file1")

# Display uploaded image
if uploaded_file1 is not None:
    image1 = PIL.Image.open(uploaded_file1)
    image_1_byte = input_image_setup(uploaded_file1)

    #Display col2 file uploader if uploaded_file1 is not None
    with col2:
        uploaded_file2 = st.file_uploader("Shop Invoice (2nd image when necessary)", key="file2")

    # Create a container to display images side by side
    image_container = st.container()

    with image_container:
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.image(image1, caption='Uploaded Image 1.', use_container_width=True)
        
        with col_img2:
            if uploaded_file2 is not None:
                image2 = PIL.Image.open(uploaded_file2)
                st.image(image2, caption='Uploaded Image 2.', use_container_width=True)
                image_2_byte = input_image_setup(uploaded_file2)
    
    # Create the generative model
    generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

    # Generate contents
    response = generative_multimodal_model.generate_content(
            ["""Convert the provided images into dumped JSON body. Return shop name, order date (null if not present on the receipt), and final payment amount only.
            Requirements:
            - Output: Return solely the JSON content without any additional explanations or comments.
            - Use this JSON schema: {"shop_name": "string", "order_date": "string", "payment_total": "string"}
            - No Delimiters: Do not use code fences or delimiters like ```json.
            - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
            - Shop Name Format: Keep the first row of detected texts only, using 'UTF-8' decoding.
            - Order Date Format: Change to date format (YYYY-MM-DD) if detected.
            - Final Payment Format: Do not include detected texts.
            """, image_1_byte]
        )

    content = response.text.encode().decode('utf-8')

    # Display the result
    # Parse the content as JSON and display it in a code block
    json_response = json.loads(content)
    pretty_json = json.dumps(json_response, indent=4)
    st.code(pretty_json, language='json')