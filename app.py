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
    return tuned_model.generate_content(inputs, generation_config=GenerationConfig(temperature=0.1, response_mime_type="application/json"))


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
        tuned_model_endpoint_name = 'projects/1081365314029/locations/us-central1/endpoints/4472506538048618496' # "gemini-pro-exp007"
        tuned_model = GenerativeModel(tuned_model_endpoint_name)

        # Generate contents
        prompt = """
        You are a receipt analyzer. Extract and validate the following information in JSON format:
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
                - payment_total: Net spending amount after deduction of any kind of gift cards, vouchers, HKIA Dollar, coupons and discounts.
                - airport_address: Return 1 if address contains 'HKIA', '機場' or '客運大樓' and matches Hong Kong Int'l Airport location. Otherwise return 0.
        """
        
        response = generate_response(image1_info, prompt)

        # Parse the response
        content = response.text
    
        # Parse the content as JSON and display it in a code block
        json_response = json.loads(content)

        # Identify mandatory fields ("shop_name", "order_date", "payment_total") with null values
        null_fields = [key for key, value in json_response.items() if not value and key in ("shop_name", "order_date", "payment_total")]
        
        # Display remarks if any field is null
        if null_fields:
            if len(null_fields) == 1:
                fields_str = null_fields[0]
            elif len(null_fields) == 2:
                fields_str = ' and '.join(null_fields)
            else:
                fields_str = ', '.join(null_fields[:-1]) + ', and ' + null_fields[-1]
        
            remarks_to_customer = f"{fields_str} cannot be auto-detected. Please upload a clear invoice image for verification."
            remarks_to_cs = f"{fields_str} cannot be auto-detected. Please verify."
        else:
            remarks_to_customer = ""
            remarks_to_cs = ""

        # Add remarks to the JSON response        
        json_response['remarks_to_customer'] = remarks_to_customer
        json_response['remarks_to_cs'] = remarks_to_cs

        
        ########################################################
        # List to store keys of updated values
        updated_keys = []
        
        # If there are null fields and a second image is provided, try to extract them from image2
        if null_fields and image2_info:

            # Generate response for the second image
            response2 = generate_response(image2_info, prompt)

            # Parse the response from image2
            content2 = response2.text

            # Parse the content as JSON and display it in a code block
            json_response2 = json.loads(content2)

            # Update null values in json_response from json_response2
            for key in json_response:
                if not json_response[key] and key in json_response2 and json_response2[key]:
                    json_response[key] = json_response2[key]
                    updated_keys.append(key)

            # Identify fields that are still null
            remaining_null_fields = [key for key, value in json_response.items() if not value]

            # Display remarks if any field remains null
            if remaining_null_fields:
                if len(remaining_null_fields) == 1:
                    fields_str = remaining_null_fields[0]
                elif len(remaining_null_fields) == 2:
                    fields_str = ' and '.join(remaining_null_fields)
                else:
                    fields_str = ', '.join(remaining_null_fields[:-1]) + ', and ' + remaining_null_fields[-1]
            
                remarks_to_customer = f"{fields_str} still cannot be auto-detected. Please upload a clear invoice image for verification."
            else:
                remarks_to_customer = ""

            # Add remarks to the JSON response        
            json_response['remarks_to_customer'] = remarks_to_customer

            # If updated_key is not empty, add remarks to the JSON response
            if updated_keys:
                json_response['remarks_to_cs'] = f"{updated_keys} are auto-detected from second image, which may not come from the same transaction. Please verify."

        ########################################################
        # Find the best match of shop name from a list of shop names
        shop_list = pd.read_csv('gs://crm_receipt_image/hkia_shop_list.csv')
        # Create a list of shop names 
        shop_names = shop_list['trade_name'].tolist()

        # Find the best match of shop name from the list
        try:
            # Use fuzz.ratio to compare similarity between two strings and extract the best match
            # Kindly note that 'process.extractOne' pre-processes the strings using utils.full_process before applying the scorer
                # e.g. Convert to lowercase, Trim whitespace collapse multiple spaces to single space, etc.
            if json_response['shop_name'] is not None:
                json_response['shop_name_matched'] = process.extractOne(json_response['shop_name'].lower(), shop_names, scorer=fuzz.ratio, score_cutoff=60)[0]
            else:
                json_response['shop_name_matched'] = ''
        
        except TypeError: # if no match is found
            json_response['shop_name_matched'] = 'Others'
        
        #If 'valid_receipt' is '0', update json_response by setting all fields to null (except 'airport_address' and 'valid_receipt'
        json_response = set_fields_to_null_if_invalid(json_response)

        # Display the final JSON response
        # Set ensure_ascii is false, to keep output as-is
        pretty_json = json.dumps(json_response, indent=4, ensure_ascii=False)
        st.code(pretty_json, language='json')