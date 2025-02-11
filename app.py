import streamlit as st
import base64
import os
from together import Together
from dotenv import load_dotenv  # Load environment variables

# Load API Key from Streamlit Secrets or .env
load_dotenv(dotenv_path=".env")  # Load from .env (for local testing)
API_KEY = os.getenv("TOGETHER_API_KEY") 

if not API_KEY:
    st.error("⚠️ API Key is missing! Set TOGETHER_API_KEY in .env or secrets.toml")
    st.stop()

# Initialize Together API client
client = Together(api_key=API_KEY)

# Streamlit UI
st.title("🧾 Invoice Text Extractor")
st.write("Upload an invoice image and extract text from it.")

# File uploader
uploaded_file = st.file_uploader("Upload an invoice image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    try:
        # Convert the uploaded image to base64
        uploaded_file.seek(0)  # Reset pointer
        base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")

        # Optimized Prompt
            # Optimized Prompt
        getDescriptionPrompt = """
        Extract only the raw text from the invoice while maintaining the original structure.
        Do not add explanations or descriptions. Ensure correct formatting and do not miss any column or any data in image:
        - Merge broken words into complete words (e.g., 'G UEST' → 'GUEST').
        - Maintain column structure correctly without merging unrelated data.
        - Keep numerical values formatted properly (e.g., '2050.00' instead of '205 0 . 00').
        - Preserve date and time as they appear (e.g., '28/05/16' instead of '28 / 05 / 16').
        - Do NOT add interpretations or explanations. Just return the plain text
        - Ensure all fields are captured without missing any information..
        """

        # Call Together AI API
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": getDescriptionPrompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
        )

        # Extract text response
        extracted_text = response.choices[0].message.content if response.choices else "No text extracted."

        # Display extracted text
        st.subheader("📜 Extracted Text")
        st.code(extracted_text, language="markdown")

    except Exception as e:
        st.error(f"⚠️ Error processing image: {e}")
