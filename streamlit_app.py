import streamlit as st
import time
import random
from typing import List, Dict

# Set page configuration
st.set_page_config(
    page_title="TheoGPT",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False

# Custom CSS to make the app look more like ChatGPT
st.markdown("""
<style>
    .main {
        background-color: #343541;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #40414f;
        color: white;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    .user-message {
        background-color: #343541;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .assistant-message {
        background-color: #444654;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .thinking-animation {
        display: inline-block;
        margin-left: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("TheoGPT")
st.markdown("A ChatGPT-style interface powered by Streamlit")

# Sidebar with options
with st.sidebar:
    st.header("Options")
    
    # Model selection dropdown
    model = st.selectbox(
        "Select model",
        ["TheoGPT-3.5", "TheoGPT-4"]
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values make it more deterministic"
    )
    
    # Clear conversation button
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.experimental_rerun()

# Mock response generator
def generate_response(prompt: str, temperature: float = 0.7) -> str:
    """
    Simulate an AI response. This is a placeholder for actual API integration.
    
    Args:
        prompt: The user input
        temperature: Controls randomness (not actually used in this mock function)
        
    Returns:
        A simulated response
    """
    # Simple responses based on keywords
    responses = [
        "I'm TheoGPT, a language model designed to simulate ChatGPT functionality.",
        "Based on my analysis, that would require further consideration.",
        "That's an interesting question. From my perspective...",
        "I can help you with that! Here's what you need to know:",
        "There are several approaches to solving this problem.",
        "Let me think about this from different angles.",
        "I don't have enough information to provide a complete answer.",
        "That's beyond my current capabilities, but I can suggest alternatives.",
    ]
    
    # Add some domain-specific responses based on keywords
    if "python" in prompt.lower() or "code" in prompt.lower():
        responses.append("```python\n# Here's a Python solution\ndef example_function():\n    return 'This is a sample code block'\n```")
    
    if "explain" in prompt.lower() or "what is" in prompt.lower():
        responses.append("To explain this concept, I need to break it down into key components...")
    
    # Randomly select a response with some "thinking" delay
    time.sleep(2)  # Simulating "thinking" time
    return random.choice(responses)

# Display chat history
st.header("Chat")
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>TheoGPT:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)

# Chat input
with st.container():
    # Create a form to handle the chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("Type your message here:", key="user_input", height=100)
        cols = st.columns([0.9, 0.1])
        with cols[1]:
            submit_button = st.form_submit_button("Send")
    
    # Process the user input when the form is submitted
    if submit_button and user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Set thinking state to true
        st.session_state.thinking = True
        st.rerun()

# Display thinking animation if needed
if st.session_state.thinking:
    thinking_container = st.empty()
    thinking_container.markdown("""
    <div class="assistant-message">
        <strong>TheoGPT:</strong> Thinking<span class="thinking-animation">...</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate response
    response = generate_response(
        st.session_state.messages[-1]["content"], 
        temperature=temperature
    )
    
    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear thinking state
    st.session_state.thinking = False
    
    # Rerun to update UI
    thinking_container.empty()
    st.rerun()

# Footer
st.markdown("""
---
TheoGPT is a demonstration app and not affiliated with OpenAI. Created for educational purposes.
""")
