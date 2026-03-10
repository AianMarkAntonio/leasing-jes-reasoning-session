import streamlit as st
import requests
import uuid
import time
from datetime import datetime

BACKEND_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com/api/v1"
BACKEND_BASE_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com"

st.set_page_config(
    page_title="LeaseMate Policy Assistant",
    page_icon="🏠",
    layout="centered"
)

# Custom CSS for typing animation
st.markdown("""
<style>
    .typing-indicator {
        display: inline-block;
        font-family: monospace;
        font-size: 1.2em;
        color: #666;
    }
    
    .typing-indicator::after {
        content: '▌';
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    
    .streaming-text {
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False
if "last_check" not in st.session_state:
    st.session_state.last_check = time.time()

# Session ID management
query_params = st.query_params
url_session_id = query_params.get("session_id")

if url_session_id and not st.session_state.session_id:
    st.session_state.session_id = url_session_id
    st.session_state.history_loaded = False
    st.rerun()

if not st.session_state.session_id:
    try:
        response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data["session_id"]
            st.query_params["session_id"] = data["session_id"]
            st.session_state.history_loaded = True
            st.rerun()
    except Exception as e:
        st.session_state.session_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.session_id

# Load conversation history
if (st.session_state.session_id and 
    not st.session_state.history_loaded and 
    len(st.session_state.messages) == 0):
    
    try:
        with st.spinner("Loading conversation history..."):
            response = requests.get(
                f"{BACKEND_URL}/sessions/{st.session_state.session_id}/history",
                params={"max_messages": 50},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                if messages:
                    st.session_state.messages = []
                    for msg in messages:
                        st.session_state.messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    st.success(f"📚 Loaded {len(messages)} messages")
                
                st.session_state.history_loaded = True
                st.rerun()
                
            elif response.status_code == 404:
                # Session expired, create new one
                new_response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
                if new_response.status_code == 200:
                    new_data = new_response.json()
                    st.session_state.session_id = new_data["session_id"]
                    st.query_params["session_id"] = new_data["session_id"]
                    st.session_state.messages = []
                    st.session_state.history_loaded = True
                    st.warning("Previous session expired. Started new conversation.")
                    st.rerun()
            else:
                st.session_state.history_loaded = True
                
    except Exception as e:
        print(f"Error loading history: {e}")
        st.session_state.history_loaded = True

# Check session expiration periodically
if time.time() - st.session_state.last_check > 30:  # Check every 30 seconds
    if st.session_state.session_id:
        try:
            response = requests.get(
                f"{BACKEND_URL}/sessions/{st.session_state.session_id}/info",
                timeout=2
            )
            if response.status_code == 200:
                info = response.json()
                if info.get("is_expired", False):
                    st.warning("Session expired. Creating new one...")
                    # Create new session
                    new_response = requests.post(f"{BACKEND_URL}/sessions/new")
                    if new_response.status_code == 200:
                        new_data = new_response.json()
                        st.session_state.session_id = new_data["session_id"]
                        st.query_params["session_id"] = new_data["session_id"]
                        st.session_state.messages = []
                        st.session_state.history_loaded = True
                        st.rerun()
        except:
            pass
    st.session_state.last_check = time.time()

# Sidebar
with st.sidebar:
    st.title("💬 Session Management")
    
    # Session info
    st.markdown("---")
    st.markdown("### Current Session")
    
    # Get session info
    session_info = None
    if st.session_state.session_id:
        try:
            info_response = requests.get(
                f"{BACKEND_URL}/sessions/{st.session_state.session_id}/info",
                timeout=2
            )
            if info_response.status_code == 200:
                session_info = info_response.json()
        except:
            pass
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Session ID", f"`{st.session_state.session_id[:8]}...`" if st.session_state.session_id else "None")
    with col2:
        st.metric("Messages", len(st.session_state.messages))
    
    if session_info:
        expires_in = session_info.get("expires_in_seconds", 0)
        if expires_in > 0:
            hours = expires_in // 3600
            minutes = (expires_in % 3600) // 60
            
            if hours > 0:
                st.info(f"⏰ Expires in {hours}h {minutes}m")
                st.progress(min(expires_in / (24 * 3600), 1.0))
            else:
                if minutes < 10:
                    st.warning(f"⚠️ Expires in {minutes}m")
                else:
                    st.info(f"⏰ Expires in {minutes}m")
                st.progress(min(expires_in / (24 * 3600), 1.0))
    
    st.markdown("---")
    st.markdown("### Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🆕 New Chat", use_container_width=True, type="primary"):
            try:
                response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.messages = []
                    st.session_state.history_loaded = True
                    st.query_params["session_id"] = data["session_id"]
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🗑️ Delete", use_container_width=True):
            try:
                if st.session_state.session_id:
                    requests.delete(f"{BACKEND_URL}/sessions/{st.session_state.session_id}", timeout=5)
                
                response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.messages = []
                    st.session_state.history_loaded = True
                    st.query_params["session_id"] = data["session_id"]
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Admin section
    with st.expander("🔧 Admin", expanded=False):
        if st.button("🧹 Cleanup Expired Sessions"):
            try:
                cleanup_response = requests.post(f"{BACKEND_URL}/sessions/cleanup", timeout=5)
                if cleanup_response.status_code == 200:
                    data = cleanup_response.json()
                    st.success(f"Cleaned up {data.get('removed_sessions', 0)} sessions")
                else:
                    st.error("Cleanup failed")
            except:
                st.error("Could not connect to backend")
        
        # Show session stats
        try:
            stats_response = requests.get(f"{BACKEND_URL}/sessions/stats", timeout=2)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                st.metric("Active Sessions", stats.get("active_sessions", 0))
                st.metric("Total Messages", stats.get("total_messages_stored", 0))
                st.metric("Storage", f"{stats.get('total_size_mb', 0)} MB")
        except:
            pass
        
        st.json({
            "session_id": st.session_state.session_id[:8] if st.session_state.session_id else None,
            "messages": len(st.session_state.messages),
            "history_loaded": st.session_state.history_loaded
        })

# Main chat interface
st.title("🏠 LeaseMate Policy Assistant")
st.caption("General Policy | JES | REASONING | Conversational AI")

# Display messages
if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
else:
    with st.chat_message("assistant"):
        st.markdown("👋 Hello! I'm your LeaseMate Policy Assistant. How can I help you with lease policies today?")

# Chat input
if prompt := st.chat_input("Ask a question about your lease policies"):
    # Add user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Create a placeholder for the assistant's response with typing indicator
    with st.chat_message("assistant"):
        # Show typing indicator
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing-indicator">Assistant is thinking</div>', unsafe_allow_html=True)
        
        try:
            # Make the API request
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "prompt": prompt,
                    "session_id": st.session_state.session_id
                },
                timeout=60
            )
            
            # Clear typing indicator
            typing_placeholder.empty()
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])
                backend_session_id = data.get("session_id", st.session_state.session_id)
                
                # Update session_id if needed
                if backend_session_id != st.session_state.session_id:
                    st.session_state.session_id = backend_session_id
                    st.query_params["session_id"] = backend_session_id
                
                # Function to stream text with typing effect
                def stream_text(text, delay=0.001):
                    """Stream text with a typing animation effect"""
                    text_placeholder = st.empty()
                    displayed_text = ""
                    
                    for char in text:
                        displayed_text += char
                        text_placeholder.markdown(f"### Answer\n\n{displayed_text}<span class='typing-indicator'></span>", unsafe_allow_html=True)
                        time.sleep(delay)
                    
                    # Final display without cursor
                    text_placeholder.markdown(f"### Answer\n\n{displayed_text}", unsafe_allow_html=True)
                    return displayed_text
                
                # Stream the answer with typing effect
                streamed_answer = stream_text(answer, delay=0.001)  # Adjust delay for faster/slower typing
                
                # Display sources after typing animation
                if sources:
                    with st.expander("📌 Sources"):
                        for src in sources:
                            file_name = src.get("file_name", "Unknown")
                            download_url = src.get("download_url")
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**📄 {file_name}**")
                            with col2:
                                if download_url:
                                    full_url = f"{BACKEND_BASE_URL}{download_url}"
                                    st.markdown(f"[⬇️ Download]({full_url})")
                
                # Add the complete message to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
                
            else:
                st.error(f"❌ Backend error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            typing_placeholder.empty()
            st.error(f"❌ Connection failed: {e}")