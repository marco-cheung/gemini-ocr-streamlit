import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig, Image
import os
import json

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=REGION)

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

    # Define the JSON schema
    json_schema = {
        "title": "Receipt OCR Result",
        "description": "Return the shop name, order date, and final payment amount from the receipt",
        "type": "object",
        "properties": {
            "shop_name": {"type": "string", "description": "Shop name"},
            "order_date": {"type": "string", "description": "Transaction date"},
            "payment_total": {"type": "string", "description": "Final payment amount"}
        },
    }

    # Construct the prompt
    prompt = f"""Convert the provided image into dumped JSON body. Return shop name, order date (null if not present on the receipt), and final payment amount only.
    Requirements:
    - Output: Return solely the JSON content without any additional explanations or comments.
    - Use this JSON schema: <JSONSchema>{json.dumps(json_schema)}</JSONSchema>.
    - No Delimiters: Do not use code fences or delimiters like ```json.
    - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
    - Shop Name Format: Keep the first row of detected texts only.
    - Order Date Format: Change to date format (YYYY-MM-DD) if detected.
    - Final Payment Format: Do not include detected texts.
    """

    # Create the generative model
    generation_config = GenerationConfig(response_mime_type="application/json")
    generative_multimodal_model = GenerativeModel("gemini-1.5-flash-002", generation_config=generation_config)

    # Generate content
    response = generative_multimodal_model.generate_content([prompt, image])

    # Display the result in the second column
    with col2:
        st.write(response.text)