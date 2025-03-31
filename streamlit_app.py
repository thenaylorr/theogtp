import streamlit as st
import time
import random
import json
import os
import hashlib
import requests
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
import re

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
if "use_web_search" not in st.session_state:
    st.session_state.use_web_search = True

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
    .search-results {
        background-color: #f5f5f5;
        padding: 0.8rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        border-left: 3px solid #ffa726;
    }
    .search-result-title {
        color: #1a0dab;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }
    .search-result-snippet {
        color: #545454;
    }
    .search-result-url {
        color: #006621;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Web Search Functions
def search_google(query, num_results=3):
    """
    Perform a Google search and return results.
    This is a simplified implementation using direct HTML scraping.
    In a production environment, you would use a proper API.
    """
    try:
        # Format the search query
        search_query = query.replace(' ', '+')
        url = f"https://www.google.com/search?q={search_query}"
        
        # Set a user agent to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Send the request
        response = requests.get(url, headers=headers)
        
        # Parse the HTML
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            search_results = []
            results = soup.find_all('div', class_='tF2Cxc')
            
            for result in results[:num_results]:
                title_element = result.find('h3')
                link_element = result.find('a')
                snippet_element = result.find('div', class_='VwiC3b')
                
                if title_element and link_element and snippet_element:
                    title = title_element.text
                    link = link_element.get('href')
                    if link.startswith('/url?q='):
                        link = link.split('/url?q=')[1].split('&')[0]
                    snippet = snippet_element.text
                    
                    search_results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
            
            return search_results
        else:
            return []
    except Exception as e:
        print(f"Error in search: {e}")
        return []

def get_webpage_content(url):
    """
    Fetch and extract the main content from a webpage.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit text length
            return text[:3000]
        else:
            return ""
    except Exception as e:
        print(f"Error fetching webpage: {e}")
        return ""

def search_and_generate_response(query, temperature=0.7):
    """
    Enhanced response generation that uses web search for information.
    """
    try:
        # First, search for information
        search_results = search_google(query, num_results=3)
        
        if not search_results:
            return "I couldn't find specific information about that from the web. " + generate_fallback_response(query, temperature)
        
        # Collect content from search results
        collected_info = []
        for result in search_results:
            collected_info.append(f"Title: {result['title']}")
            collected_info.append(f"Snippet: {result['snippet']}")
            
            # Try to get more detailed content from the webpage
            page_content = get_webpage_content(result['link'])
            if page_content:
                # Extract a relevant portion
                relevant_content = extract_relevant_content(page_content, query)
                if relevant_content:
                    collected_info.append(f"Content: {relevant_content}")
        
        # Generate a response based on collected information
        info_text = "\n\n".join(collected_info)
        
        # Format the response nicely
        response = format_search_response(query, search_results, info_text)
        return response
    
    except Exception as e:
        print(f"Error in search and response: {e}")
        return "I encountered an error while searching for information. " + generate_fallback_response(query, temperature)

def extract_relevant_content(text, query):
    """
    Extract the most relevant portions of text based on the query.
    """
    # Simple extraction based on query keywords
    query_keywords = set(query.lower().split())
    
    # Split text into paragraphs
    paragraphs = text.split('\n')
    
    # Score paragraphs based on keyword matches
    scored_paragraphs = []
    for para in paragraphs:
        if len(para) < 20:  # Skip very short paragraphs
            continue
        
        score = sum(1 for word in para.lower().split() if word in query_keywords)
        scored_paragraphs.append((score, para))
    
    # Sort by score and take top 3
    scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
    
    relevant_paragraphs = [para for score, para in scored_paragraphs[:3] if score > 0]
    
    if not relevant_paragraphs and scored_paragraphs:
        # If no paragraphs matched keywords, take the first substantial paragraph
        for _, para in scored_paragraphs:
            if len(para) > 100:
                relevant_paragraphs.append(para)
                break
    
    return " ".join(relevant_paragraphs)[:1000]  # Limit length

def format_search_response(query, search_results, info_text):
    """
    Format the final response based on search results and extracted information.
    """
    # Start with a brief introduction
    response = f"Based on my search for information about '{query}', here's what I found:\n\n"
    
    # Analyze the collected information to form a coherent response
    # This is a simplified approach - in a real AI system, you'd use more sophisticated NLP
    
    # Extract key sentences from the info text that seem most relevant
    info_sentences = re.split(r'[.!?]', info_text)
    info_sentences = [s.strip() for s in info_sentences if len(s.strip()) > 20]
    
    # Select sentences that seem most relevant (containing query terms)
    query_terms = set(query.lower().split())
    relevant_sentences = []
    
    for sentence in info_sentences:
        lower_sentence = sentence.lower()
        if any(term in lower_sentence for term in query_terms):
            relevant_sentences.append(sentence)
    
    # If we don't have enough relevant sentences, add some others
    if len(relevant_sentences) < 3 and info_sentences:
        for sentence in info_sentences:
            if sentence not in relevant_sentences:
                relevant_sentences.append(sentence)
            if len(relevant_sentences) >= 5:
                break
    
    # Construct the main body of the response
    if relevant_sentences:
        # Join the relevant sentences into a coherent paragraph
        main_content = ". ".join(relevant_sentences[:5])
        if not main_content.endswith('.'):
            main_content += '.'
        response += main_content + "\n\n"
    else:
        response += "I couldn't find detailed information directly answering your query.\n\n"
    
    # Add sources
    response += "Sources:\n"
    for idx, result in enumerate(search_results, 1):
        response += f"{idx}. {result['title']} - {result['link']}\n"
    
    return response

def generate_fallback_response(prompt, temperature=0.7):
    """
    Fallback response generator when web search fails or is disabled.
    """
    # Simple responses based on keywords
    responses = [
        "I'm TheoGPT, a language model that tries to find information from the web.",
        "Based on general knowledge, this topic relates to various factors that would need further research.",
        "Without specific web information, I can only offer a general response on this topic.",
        "I'd need to search for more current information to give you a complete answer.",
        "This question would benefit from specific data that I couldn't retrieve at the moment.",
        "From a general perspective, this topic involves multiple considerations.",
        "I don't have enough specific information to provide a detailed answer.",
        "This appears to be a specialized topic that would require detailed research.",
    ]
    
    # Add some domain-specific responses based on keywords
    if "python" in prompt.lower() or "code" in prompt.lower():
        responses.append("This seems to be related to programming. For specific code solutions, I'd need to find current best practices and documentation.")
    
    if "explain" in prompt.lower() or "what is" in prompt.lower():
        responses.append("To explain this concept properly, I'd need to gather information from reliable sources. In general terms, this relates to a topic that has multiple aspects and interpretations.")
    
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
        option_col1, option_col2, option_col3, option_col4 = st.columns([1, 1, 1, 1])
        
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
            # Web search toggle
            st.session_state.use_web_search = st.checkbox("Use web search", value=True, 
                                                        help="Enable to allow TheoGPT to search the internet for information")
        
        with option_col4:
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
            
            # Generate response based on whether web search is enabled
            if st.session_state.use_web_search:
                response = search_and_generate_response(
                    st.session_state.messages[-1]["content"], 
                    temperature=temperature
                )
            else:
                response = generate_fallback_response(
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
