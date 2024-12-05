import streamlit as st
import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel, Image
import os
import json
import PIL.Image
import io
import pandas as pd
from thefuzz import fuzz, process  # for fuzzy string matching

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

# Function to convert image to png
def convert_to_png(image_data):
    image = PIL.Image.open(io.BytesIO(image_data)).convert('RGB')
    output = io.BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()


# Function to generate response from the generative model
def generate_response(image, prompt):
    inputs = [image, prompt]
    #return generative_multimodal_model.generate_content(inputs, generation_config=GenerationConfig(temperature=0.1,
                                                                                                   #response_mime_type="application/json")
                                                                                                   #)
    # Create the generative model using tuned model
    return tuned_model.generate_content(inputs, generation_config=GenerationConfig(temperature=0.1))


def set_fields_to_null_if_invalid(receipt_data):
    if receipt_data.get('valid_receipt') == 0 or receipt_data.get('airport_address') == 0:
        for key in receipt_data:
            if key not in ['airport_address', 'valid_receipt','remarks_to_customer']:
                receipt_data[key] = None
        
        receipt_data['remarks_to_customer'] = "A valid HKIA receipt is not found in the image. Please upload again."
    
    return receipt_data

# Create two columns
col1, col2 = st.columns(2)

with col1:
    uploaded_file1 = st.file_uploader("Shop Invoice", key="file1")

# Display uploaded image
if uploaded_file1 is not None:
    image1 = PIL.Image.open(uploaded_file1)
    image1_info = Image.from_bytes(convert_to_png(uploaded_file1.getvalue()))

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
                image2_info = Image.from_bytes(convert_to_png(uploaded_file2.getvalue()))
                st.image(image2, caption='Uploaded Image 2.', use_container_width=True)          
            else:
                image2_info = None

# Create a container to display the submit button
left, middle, right = st.columns(3)
if middle.button("Submit", use_container_width=True):
    if uploaded_file1 is None:
        st.write(f"**Note: Please upload receipt image(s) first.**")

    else: 
        # Create the generative model
        #generative_multimodal_model = GenerativeModel("gemini-1.5-pro-002") # "gemini-1.5-flash-002" for faster response
        tuned_model_endpoint_name = 'projects/1081365314029/locations/us-central1/endpoints/6796012102050906112' # "gemini-pro-exp008"
        tuned_model = GenerativeModel(tuned_model_endpoint_name)

        # Generate contents
        prompt = """
        You are a receipt analyzer. Extract and validate the following information:
                {
                    "shop_name": string | null,       // Store name without special chars
                    "order_date": string | null,      // YYYY-MM-DD
                    "order_datetime": string | null,   // YYYY-MM-DD HH:mm
                    "payment_total": number | null,    // Final amount paid
                    "airport_address": 0 | 1,         // 1 if Hong Kong International Airport location, else 0
                    "valid_receipt": 0 | 1            // 1 if authentic receipt, else 0
                }

                Validation rules:
                - Set all fields except airport_address and valid_receipt to null if receipt is not authentic.
                - order_date: Format as 'YYYY-MM-DD'. Convert AM/PM to 24-hour time. If date is given as '05042024', it should be '2024-04-05'.
                - order_datetime: Format as 'YYYY-MM-DD HH:mm'. Convert AM/PM to 24-hour time.
                - payment_total: Net spending amount after deduction of any kind of gift cards, vouchers, HKIA Dollar, coupons and discounts. Note: "TO PAY" line does not necessarily reflect the final payment amount.
                - airport_address: Return 1 if address contains 'HKIA', '機場' or '客運大樓' and matches Hong Kong Int'l Airport location. Otherwise return 0.
        
        Explain how to get payment_total from the receipt.
        """
        
        response = generate_response(image1_info, prompt)

        # Parse the response
        content = response.text
        st.write(content)