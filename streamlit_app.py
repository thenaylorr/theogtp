import streamlit as st
import time
import random
import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict

# Set page configuration
st.set_page_config(
    page_title="TheoGPT",
    page_icon="🧠",
    layout="wide"
)

# File paths for user data and conversations
USER_DATA_DIR = "user_data"
os.makedirs(USER_DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(USER_DATA_DIR, "users.json")

# Initialize users data file if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# Load users data
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Save users data
def save_users(users_data):
    with open(USERS_FILE, "w") as f:
        json.dump(users_data, f)

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authenticate user
def authenticate(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

# Register new user
def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    
    users[username] = {
        "password": hash_password(password),
        "conversations": {}
    }
    save_users(users)
    return True

# Save conversation
def save_conversation(username, conversation_id, title, messages):
    users = load_users()
    if username in users:
        if conversation_id not in users[username]["conversations"]:
            # New conversation
            users[username]["conversations"][conversation_id] = {
                "title": title,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": messages
            }
        else:
            # Update existing conversation
            users[username]["conversations"][conversation_id]["messages"] = messages
            users[username]["conversations"][conversation_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        save_users(users)
        return True
    return False

# Get user conversations
def get_user_conversations(username):
    users = load_users()
    if username in users:
        return users[username]["conversations"]
    return {}

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
if "sign_up_mode" not in st.session_state:
    st.session_state.sign_up_mode = False

# Custom CSS for a brighter, more appealing interface
st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
        color: #333;
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        background-color: #ffffff;
        color: #333;
        border: 1px solid #ddd;
        border-radius: 6px;
    }
    .stButton>button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #0d8c6e;
    }
    .user-message {
        background-color: #e6f7ff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #1e88e5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .assistant-message {
        background-color: #f0f7f5;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #10a37f;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .thinking-animation {
        display: inline-block;
        margin-left: 5px;
    }
    .conversation-sidebar {
        padding: 8px;
        border-radius: 6px;
        margin-bottom: 4px;
        cursor: pointer;
    }
    .conversation-sidebar:hover {
        background-color: #eaeaea;
    }
    .selected-conversation {
        background-color: #e6f7ff;
        border-left: 3px solid #1e88e5;
    }
    .sidebar-title {
        font-weight: 600;
        color: #333;
    }
    .sidebar-date {
        font-size: 0.8em;
        color: #777;
    }
    .login-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 400px;
    }
    .login-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .login-button {
        width: 100%;
        margin-top: 1rem;
    }
    .error-message {
        color: #d32f2f;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .success-message {
        color: #388e3c;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

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
    time.sleep(1)  # Simulating "thinking" time
    return random.choice(responses)

# Login/Registration Screen
def show_login_page():
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='login-header'>Welcome to TheoGPT</h1>", unsafe_allow_html=True)
    
    # Toggle between login and signup
    if st.session_state.sign_up_mode:
        st.subheader("Create an Account")
    else:
        st.subheader("Log In")
    
    # Input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Error message placeholder
    message_placeholder = st.empty()
    
    if st.session_state.sign_up_mode:
        # Sign up form
        password_confirm = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up", key="signup_button"):
            if not username or not password:
                message_placeholder.markdown("<p class='error-message'>Please fill in all fields</p>", unsafe_allow_html=True)
            elif password != password_confirm:
                message_placeholder.markdown("<p class='error-message'>Passwords do not match</p>", unsafe_allow_html=True)
            elif register_user(username, password):
                message_placeholder.markdown("<p class='success-message'>Account created successfully! You can now log in.</p>", unsafe_allow_html=True)
                st.session_state.sign_up_mode = False
                time.sleep(1)
                st.rerun()
            else:
                message_placeholder.markdown("<p class='error-message'>Username already exists</p>", unsafe_allow_html=True)
        
        # Toggle to login mode
        if st.button("Already have an account? Log In"):
            st.session_state.sign_up_mode = False
            st.rerun()
    else:
        # Login form
        if st.button("Log In", key="login_button"):
            if not username or not password:
                message_placeholder.markdown("<p class='error-message'>Please fill in all fields</p>", unsafe_allow_html=True)
            elif authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.messages = []
                st.rerun()
            else:
                message_placeholder.markdown("<p class='error-message'>Invalid username or password</p>", unsafe_allow_html=True)
        
        # Toggle to signup mode
        if st.button("Don't have an account? Sign Up"):
            st.session_state.sign_up_mode = True
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main application UI
def show_chat_interface():
    # Create columns for the layout
    col1, col2 = st.columns([1, 3])
    
    # Sidebar with conversations list
    with col1:
        st.subheader("Conversations")
        
        # New chat button
        if st.button("+ New Chat", key="new_chat"):
            st.session_state.messages = []
            st.session_state.current_conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
            st.rerun()
        
        # Get user conversations
        conversations = get_user_conversations(st.session_state.username)
        
        # Display conversations
        st.write("---")
        for conv_id, conv_data in conversations.items():
            # Determine if this is the selected conversation
            is_selected = conv_id == st.session_state.current_conversation_id
            container_class = "conversation-sidebar selected-conversation" if is_selected else "conversation-sidebar"
            
            with st.container():
                st.markdown(f"""
                <div class='{container_class}' id='conv-{conv_id}'>
                    <div class='sidebar-title'>{conv_data['title'][:30]}</div>
                    <div class='sidebar-date'>{conv_data['updated_at']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Handle click to select conversation (not perfect, but works for demo)
                if st.button("Select", key=f"select_{conv_id}", help="Load this conversation"):
                    st.session_state.current_conversation_id = conv_id
                    st.session_state.messages = conv_data['messages']
                    st.rerun()
        
        # Logout button
        st.write("---")
        if st.button("Log Out"):
            # Save current conversation before logging out
            if st.session_state.messages:
                # Generate title from first message or use default
                title = st.session_state.messages[0]["content"][:30] if st.session_state.messages else "New Conversation"
                save_conversation(st.session_state.username, st.session_state.current_conversation_id, 
                                title, st.session_state.messages)
            
            # Reset session state
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.rerun()
    
    # Main content - chat interface
    with col2:
        # Options row
        option_col1, option_col2, option_col3 = st.columns([1, 1, 1])
        
        with option_col1:
            # Model selection dropdown
            model = st.selectbox(
                "Model",
                ["TheoGPT-3.5", "TheoGPT-4"]
            )
        
        with option_col2:
            # Temperature slider
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Higher values make output more random, lower values make it more deterministic"
            )
        
        with option_col3:
            # Save conversation button
            if st.button("Save conversation"):
                if st.session_state.messages:
                    # Generate title from first message or use default
                    title = st.session_state.messages[0]["content"][:30] if st.session_state.messages else "New Conversation"
                    if save_conversation(st.session_state.username, st.session_state.current_conversation_id, 
                                        title, st.session_state.messages):
                        st.success("Conversation saved!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("No messages to save!")
                    time.sleep(1)
                    st.rerun()
        
        # Display chat history
        st.subheader("Chat")
        chat_container = st.container(height=400)
        
        with chat_container:
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
            
            # Auto-save conversation after each response
            if st.session_state.messages:
                title = st.session_state.messages[0]["content"][:30] if st.session_state.messages else "New Conversation"
                save_conversation(st.session_state.username, st.session_state.current_conversation_id, 
                                title, st.session_state.messages)
            
            # Clear thinking state
            st.session_state.thinking = False
            
            # Rerun to update UI
            thinking_container.empty()
            st.rerun()

# Main app logic - show login or chat interface
st.title("TheoGPT")

if not st.session_state.logged_in:
    show_login_page()
else:
    show_chat_interface()

# Footer
st.markdown("""
---
TheoGPT is a demonstration app and not affiliated with OpenAI. Created for educational purposes.
""")
