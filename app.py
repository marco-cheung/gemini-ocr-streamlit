import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Image
import os
import json
import base64
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
    return generative_multimodal_model.generate_content(inputs)


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
    prompt = """Return shop name, order date (null if not present on the receipt) and final payment amount only.
        Error check:
        1) if shop name detected in the second image differs from the first, return null JSON value for shop_name, order_date, payment_total.
           FOr remarks, return error message "Detected disparate shop name, please re-upload two invoice images for a single transaction only."

        If no errors of the above, please follow the instructions below:
        1) Output: Return solely the Markdown content without any additional explanations or comments.
        2) Use this JSON schema: {'shop_name': str, 'order_date': str, 'payment_total': str, 'remarks': str} 
        3) No Delimiters: Do not use code fences or delimiters like ```markdown.
        4) Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
        5) Shop Name Format: Keep the first row of detected texts only.
        6) Order Date Format: Change to date format (YYYY-MM-DD) if detected.
        7) Final Payment Format: Do not include detected texts.
        8) Remarks: Error message if any, else return null JSON value.
      """
        
    response = generate_response(prompt, image1_info, image2_info)

    content = response.text.encode().decode('utf-8')
    st.write(content)

    # Display the result
    # Parse the content as JSON and display it in a code block
    #json_response = json.loads(content)
    #pretty_json = json.dumps(json_response, indent=4)
    #st.code(pretty_json, language='json')