import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Image
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

# Create the generative model
generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    uploaded_file1 = st.file_uploader("Upload Shop Invoice (1/2)", key="file1", use_container_width=True)

with col2:
    uploaded_file2 = st.file_uploader("Upload Shop Invoice (2/2)", key="file2", use_container_width=True)   


# Create a button to trigger the upload
if st.button("Upload"):
    if uploaded_file1 and not uploaded_file2:
        # Save the uploaded file to a temporary location
        image_1 = PIL.Image.open(uploaded_file1)
        image_2 = None

    elif uploaded_file1 and uploaded_file2:
        # Save the uploaded files to temporary locations
        image_1 = PIL.Image.open(uploaded_file1)
        image_2 = PIL.Image.open(uploaded_file2)
    else:
        st.error("Please upload at least one file.")
        image_1 = image_2 = None

    if image_1:
        # Create the generative model
        generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

        # Generate content
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
            """] + [Image(image_1), Image(image_2)] if image_2 else [Image(image_1)]
        )

        # Display the result in the second column
        with col2:
            st.json(response)
    #content = response.text.encode().decode('utf-8')

    # Display the result in the second column
    # with col2:
    #     # Parse the content as JSON and display it in a code block
    #     json_response = json.loads(content)
    #     pretty_json = json.dumps(json_response, indent=4)
    #     st.code(pretty_json, language='json')