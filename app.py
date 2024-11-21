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
    uploaded_file = st.file_uploader("Shop Invoice")

# Display uploaded image
if uploaded_file is not None:
    image = PIL.Image.open(uploaded_file)
    image_info = Image.from_bytes(uploaded_file.getvalue())

    st.image(image, caption='Uploaded Image.', use_container_width=True)
   
    # Create the generative model
    generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

    # Generate contents
    prompt = """Return shop name, order date, order number and final payment amount only.
    1) Error check:
       - If shop name and/or final payment amount is not detected, return null JSON value for "shop_name", "order_date", "order_num", "payment_total". 
         For "remarks" in JSON output, return error message "Please upload a clear invoice image for text recognition."
         Otherwise, follow the instructions below.

    2) - Output: Return solely the Markdown content without any additional explanations or comments.
       - No Delimiters: Do not use code fences or delimiters like ```markdown.
       - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
       - Shop Name Format: Keep the first row of detected texts only. Remove any additional texts.
       - Order Date Format: Change to date format (YYYY-MM-DD) if detected. Otherwise, return null JSON value.
       - Final Payment Format: Do not include detected texts.
       - Remarks: Error message if any, else return null JSON value.
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
        "order_num": {
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
    "required": ["shop_name", "order_date", "order_num", "payment_total", "remarks"]
    }

    response = generate_response(prompt, image_info)

    content = response.text.encode().decode('utf-8')
    st.write(content)

    # Display the result
    with col2:
        # Parse the content as JSON and display it in a code block
        json_response = json.loads(content)
        pretty_json = json.dumps(json_response, indent=4)
        st.code(pretty_json, language='json')