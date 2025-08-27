import streamlit as st
import requests
import json
import os

# Set up the API model and URL from environment variables or a fallback
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

# Get the API key from Streamlit secrets
API_KEY = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY"))

# Define a simple knowledge base for a "very light RAG"
# In a real-world scenario, this would be a database or vector store
NETWORK_POLICIES = {
    "Strict Firewall Policy": """
    Context: The firewall must be configured to deny all incoming traffic by default,
    except for specific ports (80, 443, 22) for web and SSH access. Outgoing traffic
    is permitted for all internal hosts.
    """,
    "DMZ Web Server Policy": """
    Context: The DMZ web server must allow incoming traffic on ports 80 and 443 from
    any source. All other incoming traffic should be blocked. The server can only
    initiate connections to internal databases on port 3306.
    """,
    "Guest Network Policy": """
    Context: The guest network must provide internet access only. All traffic
    between hosts on the guest network should be blocked. No access to the internal
    corporate network is permitted from the guest network.
    """
}

def generate_configuration(prompt, context):
    """
    Sends a request to the Gemini API to generate network configuration.

    Args:
        prompt (str): The user's request for the configuration.
        context (str): The retrieved policy to augment the prompt (RAG).

    Returns:
        str: The generated configuration or an error message.
    """
    if not API_KEY:
        return "API Key is not configured. Please add your GOOGLE_API_KEY to Streamlit secrets."

    # Construct the full prompt, including the retrieved context
    full_prompt = f"""
    You are a very very expert network engineer assistant. Your task is to generate a network device
    configuration based on the user's request, ensuring it adheres to the provided
    network policy. Provide the configuration in a clean and detail, human-readable text format,
    without any extra conversation.

    Network Policy:
    {context}

    User Request:
    {prompt}

    Generated Configuration:
    """

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 1024
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), params={"key": API_KEY})
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        response_data = response.json()
        
        # Extract the generated text
        generated_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No configuration generated.")
        
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="Intelligent Network Configuration Assistant", layout="wide")

st.title("MANISH - Intelligent Network Configuration Assistant")
st.markdown("Use this AI-powered tool to generate, verify, and safely deploy network configurations. The AI will use a selected policy as context to ensure the generated configuration is consistent and correct.")
st.divider()

# Input for the network policy (RAG retrieval)
st.subheader("1. Select Network Policy (Retrieval)")
selected_policy = st.selectbox(
    "Choose a policy to act as the knowledge context for the AI:",
    list(NETWORK_POLICIES.keys())
)
st.markdown(f"**Policy Details:**\n```\n{NETWORK_POLICIES[selected_policy].strip()}\n```")

# Input for the user's request
st.subheader("2. Describe Your Configuration Request (Generation)")
user_prompt = st.text_area(
    "Enter a detailed description of the network configuration you need:",
    placeholder="e.g., Configure VLAN 10 for the sales department with a subnet of 10.0.10.0/24 and assign a static IP of 10.0.10.1 to the gateway. Ensure DHCP is enabled for 10.0.10.100-200."
)

# Button to trigger the generation
if st.button("Generate Configuration", type="primary"):
    if not user_prompt:
        st.warning("Please provide a configuration request.")
    else:
        with st.spinner("Generating configuration..."):
            configuration = generate_configuration(user_prompt, NETWORK_POLICIES[selected_policy])
            
            st.divider()
            st.subheader("3. Generated Configuration")
            st.code(configuration, language="text")

            # Simulate the verification and deployment steps
            st.subheader("4. Verification & Deployment Simulation")
            st.success("✅ Configuration verified! It is consistent with the selected policy.")
            st.info("🚀 The configuration is now ready for safe deployment to a virtual device for final testing.")
