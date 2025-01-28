import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

# Pinata API endpoints
PINATA_PIN_LIST_ENDPOINT = "https://api.pinata.cloud/data/pinList"
PINATA_UPLOAD_ENDPOINT = "https://api.pinata.cloud/pinning/pinFileToIPFS"

# Page title and description
st.title("NodeVault")
st.write("Your images stored safely on the node-powered network.")

# Set up headers for Pinata API requests
headers = {
    "pinata_api_key": PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_SECRET_API_KEY,
}

# Sidebar: Display list of uploaded images from Pinata
with st.sidebar:
    st.header("📂 Uploaded Documents")
    response = requests.get(PINATA_PIN_LIST_ENDPOINT, headers=headers)
    
    if response.status_code == 200:
        pinned_files = response.json().get("rows", [])
        
        if pinned_files:
            # Iterate over and display each pinned file
            for file in pinned_files:
                file_name = file.get("metadata", {}).get("name", "Unnamed File")
                ipfs_hash = file.get("ipfs_pin_hash")
                timestamp = file.get("date_pinned")
                ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

                # Display file details and thumbnail
                st.write(f"**File:** {file_name}")
                st.write(f"**Uploaded At:** {timestamp}")
                file_size_kb = file.get("size", 0) // 1024
                st.write(f"**Size:** {file_size_kb} KB")
                st.image(ipfs_url, caption="Thumbnail", width=100)
                st.write(f"[🔗 View Full Image]({ipfs_url})")
        else:
            st.write("No documents uploaded yet.")
    else:
        st.error("⚠️ Failed to retrieve files from Pinata. Please check your API credentials.")

# Image upload section
uploaded_files = st.file_uploader(
    "Choose image(s) to upload", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

# Process each uploaded file
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Display file details
        st.write(f"**Uploading:** {uploaded_file.name}")
        file_size_kb = uploaded_file.size / 1024  # Convert size to KB
        st.write(f"**Size:** {file_size_kb:.2f} KB")

        # Preview the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Preview of {uploaded_file.name}", use_column_width=True)

        # Prepare the file for upload to Pinata
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

        # Upload the image to Pinata
        with st.spinner(f"Uploading {uploaded_file.name} to Pinata..."):
            response = requests.post(PINATA_UPLOAD_ENDPOINT, files=files, headers=headers)

        # Handle the response after upload
        if response.status_code == 200:
            ipfs_hash = response.json().get("IpfsHash", "")
            st.success(f"✅ Successfully uploaded {uploaded_file.name}!")
            st.write(f"**IPFS Hash:** `{ipfs_hash}`")

            # Display the IPFS URL and stored image
            ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
            st.write(f"[🔗 Access Image]({ipfs_url})")
            st.image(ipfs_url, caption=f"Stored Image: {uploaded_file.name}", use_column_width=True)
        else:
            st.error(f"❌ Failed to upload {uploaded_file.name}. Please try again.")

# End message with branding
st.write("🚀 Powered by Pinata and Streamlit")
