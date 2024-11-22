import streamlit as st
import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel, Image
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


def generate_response(prompt, image1_info, image2_info=None):
    inputs = [prompt, image1_info]
    if image2_info is not None:
        inputs.append(image2_info)
    return generative_multimodal_model.generate_content(
        inputs,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )

# Create two columns
col1, col2 = st.columns(2)

with col1:
    uploaded_file1 = st.file_uploader("Shop Invoice", key="file1")

# Display uploaded image
if uploaded_file1 is not None:
    image1 = PIL.Image.open(uploaded_file1)
    image1_info = Image.from_bytes(uploaded_file1.getvalue())

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
                image2_info = Image.from_bytes(uploaded_file2.getvalue())
                st.image(image2, caption='Uploaded Image 2.', use_container_width=True)          
            else:
                image2_info = None
   
    # Create the generative model
    generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

    # Generate contents
    prompt = """
    1) Two-fold OCR for text detection in images:
    - If any required fields are missing or undetectable from 'uploaded_file1', try to extract missing values from 'uploaded_file2'.
    - If 'shop_name', 'order_date', or 'payment_total' are still missing after checking 'uploaded_file2', return a JSON response with 'remarks' set to 'Please upload a clear invoice image for verification.'.

    2) Output:
    - Return only the Markdown content without explanations or comments.
    - Do not use code fences or delimiters.
    - Include all parts of the page, including headers, footers, and subtext.
    - Shop Name: Remove special characters, encode as UTF-8, and convert Unicode escape sequences to characters.
    - Order Date: Format as YYYY-MM-DD if detected, otherwise return null.
    - Order Datetime: Format as YYYY-MM-DD hh:mm if detected, otherwise return null.
    - Invoice Number: Trim whitespaces.
    - Payment Total: If not found, search for similar keywords like "Amount Due".
    - Remarks: Return error message if any of the following fields ('shop_name', 'order_date', 'payment_total') is still missing after trying to extract missing values from 'uploaded_file2', else return null.
    """

    response_schema = {
    "type": "object",
    "properties": {
        "shop_name": {
            "type": "string",
            "nullable": True
        },
        "order_date": {
            "type": "string", 
            "format": "date",
            "nullable": True
        },
        "order_datetime": {
            "type": "string", 
            "format": "datetime",
            "nullable": True
        },
        "invoice_num": {
            "type": "string", 
            "format": "string",
            "nullable": True
        },
        "payment_total": {
            "type": "string",
            "nullable": True
        },
        "remarks": {
            "type": "string",
            "nullable": True
        }
    },
    "required": ["shop_name", "order_date", "order_datetime", "invoice_num", "payment_total", "remarks"]
    }

    response = generate_response(prompt, image1_info, image2_info)

    content = response.text.encode().decode('utf-8')
    #st.write(content)

    # Parse the content as JSON and display it in a code block
    json_response = json.loads(content)
    pretty_json = json.dumps(json_response, indent=4)
    st.code(pretty_json, language='json')