import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Groq AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
    <style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat container styling */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 20px 0;
    }
    
    /* Message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 18px 18px 5px 18px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        font-size: 16px;
        line-height: 1.6;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 18px 18px 18px 5px;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: white;
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .sub-header {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 20px;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    /* Input box styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 15px;
        font-size: 16px;
        color: #333;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.5);
    }
    
    /* Sidebar elements */
    .sidebar-content {
        color: white;
        font-size: 16px;
        line-height: 1.8;
    }
    
    /* Stats cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: 700;
        color: white;
        text-align: center;
    }
    
    .stat-label {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        margin-top: 5px;
    }
    
    /* Clear button */
    .clear-button {
        background: rgba(255, 87, 87, 0.8) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0
if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found in environment variables!")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='color: white; font-size: 28px;'>⚙️ Settings</h1>", unsafe_allow_html=True)
    
    # Model selection
    model = st.selectbox(
        "🤖 Select Model",
        ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-8b-instant"],
        index=0
    )
    
    # Temperature slider
    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Controls randomness. Lower is more focused, higher is more creative."
    )
    
    # Max tokens
    max_tokens = st.slider(
        "📝 Max Tokens",
        min_value=100,
        max_value=4000,
        value=1024,
        step=100,
        help="Maximum length of the response"
    )
    
    st.markdown("---")
    
    # Statistics
    st.markdown("<h2 style='color: white; font-size: 22px;'>📊 Statistics</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{st.session_state.conversation_count}</div>
                <div class='stat-label'>Messages</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{len(st.session_state.messages)}</div>
                <div class='stat-label'>History</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
        <div class='sidebar-content'>
            <h3 style='font-size: 18px;'>💡 Tips</h3>
            <ul>
                <li>Ask anything you want</li>
                <li>Use lower temperature for factual answers</li>
                <li>Use higher temperature for creative responses</li>
                <li>Adjust max tokens for longer answers</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown("<h1 class='main-header'>🤖 Groq AI Chat Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Powered by Groq's Lightning-Fast LLM Inference</p>", unsafe_allow_html=True)

# Chat container
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'>👤 {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-message'>🤖 {message['content']}</div>", unsafe_allow_html=True)
    
    # Add some space for scrolling
    st.markdown("<br><br>", unsafe_allow_html=True)

# Input area
st.markdown("---")
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "💬 Your message",
        placeholder="Type your message here...",
        key="user_input",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("🚀 Send", use_container_width=True)

# Handle message sending
if send_button and user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_count += 1
    
    # Show loading animation
    with st.spinner("🔮 AI is thinking..."):
        try:
            # Get AI response
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract response
            ai_response = chat_completion.choices[0].message.content
            
            # Add AI response to history
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.session_state.conversation_count += 1
            
            # Rerun to update the display
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Quick prompts
st.markdown("---")
st.markdown("<h3 style='color: white; text-align: center;'>✨ Quick Prompts</h3>", unsafe_allow_html=True)

quick_prompts = [
    "Tell me a joke 😄",
    "Explain quantum computing 🔬",
    "Write a short story 📖",
    "Give me coding tips 💻"
]

cols = st.columns(4)
for idx, prompt in enumerate(quick_prompts):
    with cols[idx]:
        if st.button(prompt, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.conversation_count += 1
            
            with st.spinner("🔮 AI is thinking..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    
                    ai_response = chat_completion.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.session_state.conversation_count += 1
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white; padding: 20px;'>
        <p style='font-size: 14px; opacity: 0.8;'>Built by Ronit ❤️ using Streamlit and Groq AI</p>
    </div>
""", unsafe_allow_html=True)
