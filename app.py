import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Image
import os
import json

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=REGION)

# Streamlit app
st.title("Gemini API OCR with Streamlit")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    image_path = f"/tmp/{uploaded_file.name}"
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Load the image from the local file
    image = Image.load_from_file(image_path)

    # Create the generative model
    generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002")

    # Generate content
    response = generative_multimodal_model.generate_content(
        ["""Convert the provided image into JSON format. Return shop name, order date (null if not present on the receipt), and final payment amount only.
         Requirements:
          - Output: Return solely the JSON content without any additional explanations or comments.
          - Use this JSON schema: {"shop_name": "string", "order_date": "string", "payment_total": "string"}
          - No Delimiters: Do not use code fences or delimiters like ```json.
          - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
          - Shop Name Format: Keep the first row of detected texts only.
          - Order Date Format: Change to date format (YYYY-MM-DD) if detected.
          - Final Payment Format: Do not include detected texts.
        """]
    )

    # Extract the content from the response
    content = response[0].text

    # Print the raw content for debugging
    st.write("Raw content:", content)

    # Attempt to parse the content as JSON
    try:
        json_response = json.loads(content)
        st.json(json_response)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON: {e}")
        st.write("Raw content:", content)