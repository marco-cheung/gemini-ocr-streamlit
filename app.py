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
            temperature=0.1,
            response_mime_type="application/json")
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
    You are an intelligent receipt analyzer. Analyze the provided image and extract the following key information:

    {
        "shop_name": "Store Name", 
        "order_date": "YYYY-MM-DD",
        "order_datetime": "YYYY-MM-DD HH:mm",
        "invoice_num": "123456",
        "payment_total": 99.99,
        "remarks": ""
    }

    Rules:
    1. shop_name: UTF-8 encoded, no special chars, convert Unicode escape sequences to readable characters
    2. order_date: YYYY-MM-DD format or null
    3. order_datetime: YYYY-MM-DD HH:mm format or null
    4. invoice_num: Trimmed whitespace or null
    5. payment_total: Final amount paid by customer, i.e. net payment amount after deducting amount such as gift card and e-Coupon discount
    6. remarks: If shop_name/order_datetime/payment_total is null, add: "{key} cannot be auto-detected. Please upload a clear invoice image for verification."
                For example, if shop_name is null, add: "shop_name cannot be auto-detected. Please upload a clear invoice image for verification."
    
    Return clean JSON only, no additional text.
    """
    
    response = generate_response(prompt, image1_info, image2_info)

    content = response.text.encode().decode('utf-8')
    #st.write(content)

    # Parse the content as JSON and display it in a code block
    json_response = json.loads(content)
    pretty_json = json.dumps(json_response, indent=4)
    st.code(pretty_json, language='json')