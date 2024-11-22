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


# Function to generate response from the generative model
def generate_response(prompt, image):
    inputs = [prompt, image]
    return generative_multimodal_model.generate_content(inputs, generation_config=GenerationConfig(temperature=0.1,
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
        "payment_total": 99.99
    }

    Rules:
    1. shop_name: UTF-8 encoded, no special chars, decode Unicode escape sequences to unicode characters
    2. order_date: YYYY-MM-DD format or null
    3. order_datetime: YYYY-MM-DD HH:mm format or null
    4. invoice_num: Trimmed whitespace or null
    5. payment_total: Final amount paid by customer, i.e. net payment amount after deducting amount such as gift card and e-Coupon discount
  
    Return clean JSON only, no additional text or further explanation.
    """
    
    response = generate_response(prompt, image1_info)

    content = response.text.encode().decode('utf-8')
   
    # Parse the content as JSON and display it in a code block
    json_response = json.loads(content)

    # Identify mandatory fields ("shop_name", "order_date", "payment_total") with null values
    null_fields = [key for key, value in json_response.items() if not value and key in ("shop_name", "order_date", "payment_total")]
    
    # Update original json response and display remarks if any field is null
    if null_fields:
        if len(null_fields) == 1:
            fields_str = null_fields[0]
        elif len(null_fields) == 2:
            fields_str = ' and '.join(null_fields)
        else:
            fields_str = ', '.join(null_fields[:-1]) + ', and ' + null_fields[-1]
    
        remarks = f"{fields_str} cannot be auto-detected. Please upload a clear invoice image for verification."
    else:
        remarks = ""

    # Add remarks to the JSON response        
    json_response['remarks'] = remarks
    
    # Display the response
    pretty_json = json.dumps(json_response, indent=4)
    st.code(pretty_json, language='json')

    # If there are null fields and a second image is provided, try to extract them from image2
    if null_fields and image2_info:
        # Modify the prompt to extract only the null fields
        fields_to_extract = ", ".join(f'"{field}"' for field in null_fields)

        # Prompt for the null fields
        prompt_null_fields = f"""
        {
            "shop_name": "Store Name", 
            "order_date": "YYYY-MM-DD",
            "order_datetime": "YYYY-MM-DD HH:mm",
            "invoice_num": "123456",
            "payment_total": 99.99
        }

        Rules:
        1. shop_name: UTF-8 encoded, no special chars, decode Unicode escape sequences to unicode characters
        2. order_date: YYYY-MM-DD format or null
        3. order_datetime: YYYY-MM-DD HH:mm format or null
        4. invoice_num: Trimmed whitespace or null
        5. payment_total: Final amount paid by customer, i.e. net payment amount after deducting amount such as gift card and e-Coupon discount

        Additional Instructions:
        Only extract the following fields: {fields_to_extract}

        Return clean JSON only, no additional text or further explanation.
        """

        # Generate response for the second image
        response2 = generate_response(prompt_null_fields, image2_info)

        # Parse the response from image2
        content2 = response2.text.encode().decode('utf-8')
        json_response2 = json.loads(content2)

        # Update the original response with values from the second image
        for key in null_fields:
            if key in json_response2 and json_response2[key]:
                json_response[key] = json_response2[key]

        # Identify fields that are still null
        remaining_null_fields = [key for key in null_fields if not json_response.get(key)]

        # Update remarks if any fields are still null
        if remaining_null_fields:
            if json_response["remarks"]:
                json_response["remarks"] += "\n"
            if len(remaining_null_fields) == 1:
                fields_str = remaining_null_fields[0]
            elif len(remaining_null_fields) == 2:
                fields_str = ' and '.join(remaining_null_fields)
            else:
                fields_str = ', '.join(remaining_null_fields[:-1]) + ', and ' + remaining_null_fields[-1]
            json_response["remarks"] += f"{fields_str} still cannot be auto-detected. Please upload a clear invoice image for verification."

        # Display the final JSON response
        pretty_json = json.dumps(json_response, indent=4)
        st.code(pretty_json, language='json')