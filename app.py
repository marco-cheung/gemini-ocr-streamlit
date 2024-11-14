import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Image
import os
import json

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=REGION)

# Display the banner image
banner_image_path = "image/hkairport-logo.png"  # Update this path to the correct path of your banner image
st.image(banner_image_path, use_container_width=True)

# Streamlit app
st.title("Demo of Receipt OCR with Google Gemini API")

uploaded_file = st.file_uploader("Please upload an image...")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    image_path = f"/tmp/{uploaded_file.name}"
       
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Create two columns
    col1, col2 = st.columns(2)

    # Display the uploaded image in the first column
    with col1:
        st.image(image_path, caption='Uploaded Image', use_container_width=True)

    # Load the image from the local file
    image = Image.load_from_file(image_path)

    # Create the generative model
    generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

    # Generate content
    response = generative_multimodal_model.generate_content(
        ["""Convert the provided image into dumped JSON body. Return shop name, order date (null if not present on the receipt), and final payment amount only.
         Requirements:
          - Output: Return solely the JSON content without any additional explanations or comments.
          - Use this JSON schema: {"shop_name": "string", "order_date": "string", "payment_total": "string"}
          - No Delimiters: Do not use code fences or delimiters like ```json.
          - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
          - Shop Name Format: Keep the first row of detected texts only, using 'UTF-8' decoding
          - Order Date Format: Change to date format (YYYY-MM-DD) if detected.
          - Final Payment Format: Do not include detected texts.
        """,
        image]
    )

    content = response.text

    # Display the result in the second column
    with col2:
        #Parse the content as JSON and display it in a code block
        json_response = json.loads(content)
        pretty_json = json.dumps(json_response, indent=4)
        st.code(pretty_json, language='json')