# import streamlit as st
# import requests
# import uuid
# import time
# from datetime import datetime

# BACKEND_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com/api/v1"
# BACKEND_BASE_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com"

# st.set_page_config(
#     page_title="LeaseMate Policy Assistant",
#     page_icon="🏠",
#     layout="centered"
# )

# # Custom CSS for typing animation
# st.markdown("""
# <style>
#     .typing-indicator {
#         display: inline-block;
#         font-family: monospace;
#         font-size: 1.2em;
#         color: #666;
#     }
    
#     .typing-indicator::after {
#         content: '▌';
#         animation: blink 1s infinite;
#     }
    
#     @keyframes blink {
#         0%, 100% { opacity: 1; }
#         50% { opacity: 0; }
#     }
    
#     .streaming-text {
#         animation: fadeIn 0.5s;
#     }
    
#     @keyframes fadeIn {
#         from { opacity: 0; transform: translateY(10px); }
#         to { opacity: 1; transform: translateY(0); }
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "session_id" not in st.session_state:
#     st.session_state.session_id = None
# if "history_loaded" not in st.session_state:
#     st.session_state.history_loaded = False
# if "last_check" not in st.session_state:
#     st.session_state.last_check = time.time()

# # Session ID management
# query_params = st.query_params
# url_session_id = query_params.get("session_id")

# if url_session_id and not st.session_state.session_id:
#     st.session_state.session_id = url_session_id
#     st.session_state.history_loaded = False
#     st.rerun()

# if not st.session_state.session_id:
#     try:
#         response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
#         if response.status_code == 200:
#             data = response.json()
#             st.session_state.session_id = data["session_id"]
#             st.query_params["session_id"] = data["session_id"]
#             st.session_state.history_loaded = True
#             st.rerun()
#     except Exception as e:
#         st.session_state.session_id = str(uuid.uuid4())
#         st.query_params["session_id"] = st.session_state.session_id

# # Load conversation history
# if (st.session_state.session_id and 
#     not st.session_state.history_loaded and 
#     len(st.session_state.messages) == 0):
    
#     try:
#         with st.spinner("Loading conversation history..."):
#             response = requests.get(
#                 f"{BACKEND_URL}/sessions/{st.session_state.session_id}/history",
#                 params={"max_messages": 50},
#                 timeout=5
#             )
            
#             if response.status_code == 200:
#                 data = response.json()
#                 messages = data.get("messages", [])
                
#                 if messages:
#                     st.session_state.messages = []
#                     for msg in messages:
#                         st.session_state.messages.append({
#                             "role": msg["role"],
#                             "content": msg["content"]
#                         })
#                     st.success(f"📚 Loaded {len(messages)} messages")
                
#                 st.session_state.history_loaded = True
#                 st.rerun()
                
#             elif response.status_code == 404:
#                 # Session expired, create new one
#                 new_response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
#                 if new_response.status_code == 200:
#                     new_data = new_response.json()
#                     st.session_state.session_id = new_data["session_id"]
#                     st.query_params["session_id"] = new_data["session_id"]
#                     st.session_state.messages = []
#                     st.session_state.history_loaded = True
#                     st.warning("Previous session expired. Started new conversation.")
#                     st.rerun()
#             else:
#                 st.session_state.history_loaded = True
                
#     except Exception as e:
#         print(f"Error loading history: {e}")
#         st.session_state.history_loaded = True

# # Check session expiration periodically
# if time.time() - st.session_state.last_check > 30:  # Check every 30 seconds
#     if st.session_state.session_id:
#         try:
#             response = requests.get(
#                 f"{BACKEND_URL}/sessions/{st.session_state.session_id}/info",
#                 timeout=2
#             )
#             if response.status_code == 200:
#                 info = response.json()
#                 if info.get("is_expired", False):
#                     st.warning("Session expired. Creating new one...")
#                     # Create new session
#                     new_response = requests.post(f"{BACKEND_URL}/sessions/new")
#                     if new_response.status_code == 200:
#                         new_data = new_response.json()
#                         st.session_state.session_id = new_data["session_id"]
#                         st.query_params["session_id"] = new_data["session_id"]
#                         st.session_state.messages = []
#                         st.session_state.history_loaded = True
#                         st.rerun()
#         except:
#             pass
#     st.session_state.last_check = time.time()

# # Sidebar
# with st.sidebar:
#     st.title("💬 Session Management")
    
#     # Session info
#     st.markdown("---")
#     st.markdown("### Current Session")
    
#     # Get session info
#     session_info = None
#     if st.session_state.session_id:
#         try:
#             info_response = requests.get(
#                 f"{BACKEND_URL}/sessions/{st.session_state.session_id}/info",
#                 timeout=2
#             )
#             if info_response.status_code == 200:
#                 session_info = info_response.json()
#         except:
#             pass
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Session ID", f"`{st.session_state.session_id[:8]}...`" if st.session_state.session_id else "None")
#     with col2:
#         st.metric("Messages", len(st.session_state.messages))
    
#     if session_info:
#         expires_in = session_info.get("expires_in_seconds", 0)
#         if expires_in > 0:
#             hours = expires_in // 3600
#             minutes = (expires_in % 3600) // 60
            
#             if hours > 0:
#                 st.info(f"⏰ Expires in {hours}h {minutes}m")
#                 st.progress(min(expires_in / (24 * 3600), 1.0))
#             else:
#                 if minutes < 10:
#                     st.warning(f"⚠️ Expires in {minutes}m")
#                 else:
#                     st.info(f"⏰ Expires in {minutes}m")
#                 st.progress(min(expires_in / (24 * 3600), 1.0))
    
#     st.markdown("---")
#     st.markdown("### Actions")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         if st.button("🆕 New Chat", use_container_width=True, type="primary"):
#             try:
#                 response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
#                 if response.status_code == 200:
#                     data = response.json()
#                     st.session_state.session_id = data["session_id"]
#                     st.session_state.messages = []
#                     st.session_state.history_loaded = True
#                     st.query_params["session_id"] = data["session_id"]
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"Error: {e}")
    
#     with col2:
#         if st.button("🗑️ Delete", use_container_width=True):
#             try:
#                 if st.session_state.session_id:
#                     requests.delete(f"{BACKEND_URL}/sessions/{st.session_state.session_id}", timeout=5)
                
#                 response = requests.post(f"{BACKEND_URL}/sessions/new", timeout=5)
#                 if response.status_code == 200:
#                     data = response.json()
#                     st.session_state.session_id = data["session_id"]
#                     st.session_state.messages = []
#                     st.session_state.history_loaded = True
#                     st.query_params["session_id"] = data["session_id"]
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"Error: {e}")
    
#     st.markdown("---")
    
#     # Admin section
#     with st.expander("🔧 Admin", expanded=False):
#         if st.button("🧹 Cleanup Expired Sessions"):
#             try:
#                 cleanup_response = requests.post(f"{BACKEND_URL}/sessions/cleanup", timeout=5)
#                 if cleanup_response.status_code == 200:
#                     data = cleanup_response.json()
#                     st.success(f"Cleaned up {data.get('removed_sessions', 0)} sessions")
#                 else:
#                     st.error("Cleanup failed")
#             except:
#                 st.error("Could not connect to backend")
        
#         # Show session stats
#         try:
#             stats_response = requests.get(f"{BACKEND_URL}/sessions/stats", timeout=2)
#             if stats_response.status_code == 200:
#                 stats = stats_response.json()
#                 st.metric("Active Sessions", stats.get("active_sessions", 0))
#                 st.metric("Total Messages", stats.get("total_messages_stored", 0))
#                 st.metric("Storage", f"{stats.get('total_size_mb', 0)} MB")
#         except:
#             pass
        
#         st.json({
#             "session_id": st.session_state.session_id[:8] if st.session_state.session_id else None,
#             "messages": len(st.session_state.messages),
#             "history_loaded": st.session_state.history_loaded
#         })

# # Main chat interface
# st.title("🏠 LeaseMate Policy Assistant")
# st.caption("General Policy | JES | REASONING | Conversational AI")

# # Display messages
# if st.session_state.messages:
#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])
# else:
#     with st.chat_message("assistant"):
#         st.markdown("👋 Hello! I'm your LeaseMate Policy Assistant. How can I help you with lease policies today?")

# # Chat input
# if prompt := st.chat_input("Ask a question about your lease policies"):
#     # Add user message
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     st.session_state.messages.append({
#         "role": "user",
#         "content": prompt
#     })
    
#     # Create a placeholder for the assistant's response with typing indicator
#     with st.chat_message("assistant"):
#         # Show typing indicator
#         typing_placeholder = st.empty()
#         typing_placeholder.markdown('<div class="typing-indicator">Assistant is thinking</div>', unsafe_allow_html=True)
        
#         try:
#             # Make the API request
#             response = requests.post(
#                 f"{BACKEND_URL}/chat",
#                 json={
#                     "prompt": prompt,
#                     "session_id": st.session_state.session_id
#                 },
#                 timeout=60
#             )
            
#             # Clear typing indicator
#             typing_placeholder.empty()
            
#             if response.status_code == 200:
#                 data = response.json()
#                 answer = data.get("answer", "No answer returned.")
#                 sources = data.get("sources", [])
#                 backend_session_id = data.get("session_id", st.session_state.session_id)
                
#                 # Update session_id if needed
#                 if backend_session_id != st.session_state.session_id:
#                     st.session_state.session_id = backend_session_id
#                     st.query_params["session_id"] = backend_session_id
                
#                 # Function to stream text with typing effect
#                 def stream_text(text, delay=0.001):
#                     """Stream text with a typing animation effect"""
#                     text_placeholder = st.empty()
#                     displayed_text = ""
                    
#                     for char in text:
#                         displayed_text += char
#                         text_placeholder.markdown(f"### Answer\n\n{displayed_text}<span class='typing-indicator'></span>", unsafe_allow_html=True)
#                         time.sleep(delay)
                    
#                     # Final display without cursor
#                     text_placeholder.markdown(f"### Answer\n\n{displayed_text}", unsafe_allow_html=True)
#                     return displayed_text
                
#                 # Stream the answer with typing effect
#                 streamed_answer = stream_text(answer, delay=0.001)  # Adjust delay for faster/slower typing
                
#                 # Display sources after typing animation
#                 if sources:
#                     with st.expander("📌 Sources"):
#                         for src in sources:
#                             file_name = src.get("file_name", "Unknown")
#                             download_url = src.get("download_url")
                            
#                             col1, col2 = st.columns([3, 1])
#                             with col1:
#                                 st.markdown(f"**📄 {file_name}**")
#                             with col2:
#                                 if download_url:
#                                     full_url = f"{BACKEND_BASE_URL}{download_url}"
#                                     st.markdown(f"[⬇️ Download]({full_url})")
                
#                 # Add the complete message to session state
#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": answer
#                 })
                
#             else:
#                 st.error(f"❌ Backend error: {response.status_code}")
                
#         except requests.exceptions.RequestException as e:
#             typing_placeholder.empty()
#             st.error(f"❌ Connection failed: {e}")

import streamlit as st
import requests
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BACKEND_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com/api/v1/chat"
BACKEND_BASE_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com"

st.set_page_config(
    page_title="LeaseMate Policy Assistant",
    page_icon="🏠",
    layout="centered"
)

# Initialize session state variables
if "session_id" not in st.session_state:
    # Check if there's a saved session in URL params
    params = st.query_params
    if "session" in params:
        st.session_state.session_id = params["session"]
    else:
        st.session_state.session_id = None  # Will be created by backend
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "session_created" not in st.session_state:
    st.session_state.session_created = False
    
if "session_info" not in st.session_state:
    st.session_state.session_info = None
    
if "loading_history" not in st.session_state:
    st.session_state.loading_history = False
    
# Flag to track if initial load is complete
if "initial_load_complete" not in st.session_state:
    st.session_state.initial_load_complete = False
    
# Flag to track if we need to force reload
if "force_reload_needed" not in st.session_state:
    st.session_state.force_reload_needed = False
    
# Track backend connection status
if "backend_connected" not in st.session_state:
    st.session_state.backend_connected = False
    
# Track retry attempts
if "retry_count" not in st.session_state:
    st.session_state.retry_count = 0

# Very fast typing effect settings (no user controls)
TYPING_SPEED = 0.003  # Very fast - 0.003 seconds per character (about 333 chars per second)

# Function to display text with very fast typing effect
def typewriter_text(text):
    """Display text with a very fast typewriter effect"""
    # Create a placeholder for the typing effect
    type_placeholder = st.empty()
    
    # Display characters very quickly
    displayed_text = ""
    for char in text:
        displayed_text += char
        type_placeholder.markdown(displayed_text + "▌")  # Add cursor
        time.sleep(TYPING_SPEED)
    
    # Remove cursor and show final text
    type_placeholder.markdown(text)
    return text

# Function to display assistant response with very fast typing effect
def display_assistant_response(answer, sources, base_url):
    """Display assistant response with very fast typing effect for the answer"""
    
    with st.chat_message("assistant"):
        # Display "Answer" header first
        st.markdown("### Answer")
        
        # Apply very fast typing effect to the answer
        # Use a placeholder for the answer with typing effect
        answer_placeholder = st.empty()
        
        # Type out the answer very quickly
        displayed_answer = ""
        for char in answer:
            displayed_answer += char
            answer_placeholder.markdown(displayed_answer + "▌")
            time.sleep(TYPING_SPEED)
        
        # Show final answer without cursor
        answer_placeholder.markdown(displayed_answer)
        
        # Display sources (these appear instantly after typing completes)
        if sources:
            with st.expander("📌 Sources"):
                for src in sources:
                    file_name = src.get("file_name", "Unknown document")
                    download_url = src.get("download_url")
                    
                    st.markdown(f"**📄 {file_name}**")
                    
                    if download_url:
                        full_url = f"{base_url}{download_url}"
                        st.markdown(
                            f"[⬇️ Source]({full_url})",
                            unsafe_allow_html=True
                        )
                    
                    st.markdown("---")

# Function to create a session with retry logic
def create_requests_session():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Function to check backend connection
def check_backend_connection():
    """Check if backend is accessible"""
    try:
        # Try to access the docs or a simple endpoint
        response = requests.get(f"{BACKEND_BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

# Function to create a new session using backend API
def create_backend_session(existing_session_id=None):
    """Create a new session using the backend /sessions/new endpoint"""
    try:
        new_session_url = f"{BACKEND_BASE_URL}/api/v1/sessions/new"
        
        # Prepare request body if we have an existing session ID to reuse
        payload = {}
        if existing_session_id:
            payload = {"session_id": existing_session_id}
        
        session = create_requests_session()
        response = session.post(
            new_session_url,
            json=payload if payload else None,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            
            # Get session info immediately after creation
            get_session_info(session_id)
            
            st.session_state.backend_connected = True
            st.session_state.retry_count = 0
            
            return session_id
        else:
            st.error(f"Failed to create session: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError as e:
        st.session_state.backend_connected = False
        st.session_state.retry_count += 1
        
        if st.session_state.retry_count < 3:
            st.warning(f"⚠️ Backend connection failed. Retrying... (Attempt {st.session_state.retry_count}/3)")
            time.sleep(2)
            return create_backend_session(existing_session_id)
        else:
            st.error("❌ Cannot connect to backend server. Please ensure it's running at http://127.0.0.1:8000")
            return None
    except Exception as e:
        st.error(f"Error creating session: {e}")
        st.session_state.backend_connected = False
        return None

# Function to load conversation history
def load_conversation_history(session_id):
    """Load conversation history from backend using /sessions/{session_id}/history endpoint"""
    try:
        history_url = f"{BACKEND_BASE_URL}/api/v1/sessions/{session_id}/history"
        session = create_requests_session()
        response = session.get(history_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            
            # Clear existing messages and load from history
            st.session_state.messages = []
            for msg in messages:
                st.session_state.messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Also get detailed session info
            get_session_info(session_id)
            
            st.session_state.backend_connected = True
            
            return True
        elif response.status_code == 404:
            # Session doesn't exist, create new one
            new_session_id = create_backend_session()
            if new_session_id:
                st.session_state.session_id = new_session_id
                st.query_params["session"] = new_session_id
                return True
            return False
    except requests.exceptions.ConnectionError:
        st.session_state.backend_connected = False
        st.error("❌ Lost connection to backend server")
        return False
    except Exception as e:
        st.error(f"Failed to load history: {e}")
        return False

# UPDATED: Function to get session info using your endpoint
def get_session_info(session_id):
    """Get detailed session info using /sessions/{session_id}/info endpoint"""
    try:
        info_url = f"{BACKEND_BASE_URL}/api/v1/sessions/{session_id}/info"
        session = create_requests_session()
        response = session.get(info_url, timeout=10)
        
        if response.status_code == 200:
            st.session_state.session_info = response.json()
            return True
        elif response.status_code == 404:
            # Session not found, will need to create new one
            st.session_state.session_info = None
            return False
    except Exception as e:
        # Non-critical error, just log it
        print(f"Failed to get session info: {e}")
        return False

# Function to delete session
def delete_backend_session(session_id):
    """Delete session using /sessions/{session_id} endpoint"""
    try:
        delete_url = f"{BACKEND_BASE_URL}/api/v1/sessions/{session_id}"
        session = create_requests_session()
        response = session.delete(delete_url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting session: {e}")
        return False

# NEW: Function to calculate expiration status
def get_expiration_status(session_info):
    """Calculate expiration status from session info"""
    if not session_info:
        return "Unknown", 0
    
    # Check if session_info has expiration fields
    created_at = session_info.get('created_at')
    expires_at = session_info.get('expires_at')
    expires_in_seconds = session_info.get('expires_in_seconds')
    
    if expires_in_seconds is not None:
        hours = expires_in_seconds / 3600
        if expires_in_seconds <= 0:
            return "Expired", 0
        elif expires_in_seconds < 300:  # Less than 5 minutes
            return "Expiring soon", hours
        else:
            return "Active", hours
    elif expires_at and created_at:
        # Calculate based on timestamps if available
        try:
            # Parse timestamps (adjust format as needed)
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            remaining = (expires - datetime.now().astimezone()).total_seconds()
            hours = remaining / 3600
            if remaining <= 0:
                return "Expired", 0
            elif remaining < 300:
                return "Expiring soon", hours
            else:
                return "Active", hours
        except:
            return "Active", 24  # Default to 24 hours if can't parse
    else:
        return "Active", 24  # Default to 24 hours

# Sidebar for session management
with st.sidebar:
    st.header("🔐 Session Management")
    
    # Display backend connection status
    if st.session_state.backend_connected:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Disconnected")
        if st.button("🔄 Retry Connection", use_container_width=True):
            st.session_state.retry_count = 0
            st.session_state.initial_load_complete = False
            st.rerun()
    
    st.divider()
    
    # Display current session info
    if st.session_state.session_id:
        st.caption(f"Session ID: `{st.session_state.session_id[:8]}...`")
    else:
        st.caption("No active session")
    
    # Session actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🆕 New Session", use_container_width=True):
            # Create new session using backend
            with st.spinner("Creating new session..."):
                new_session_id = create_backend_session()
                if new_session_id:
                    st.session_state.session_id = new_session_id
                    st.session_state.messages = []
                    st.session_state.session_info = None
                    st.session_state.initial_load_complete = False
                    st.query_params["session"] = new_session_id
                    st.rerun()
                else:
                    st.error("Failed to create new session")
    
    with col2:
        if st.button("🗑️ Delete Current", use_container_width=True) and st.session_state.session_id:
            # Delete current session
            with st.spinner("Deleting session..."):
                if delete_backend_session(st.session_state.session_id):
                    st.success("Session deleted!")
                    # Create new session automatically
                    new_session_id = create_backend_session()
                    if new_session_id:
                        st.session_state.session_id = new_session_id
                        st.session_state.messages = []
                        st.session_state.session_info = None
                        st.session_state.initial_load_complete = False
                        st.query_params["session"] = new_session_id
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Failed to delete session")
    
    # UPDATED: Session info expander with proper expiration display
    if st.session_state.session_info:
        with st.expander("📊 Session Info"):
            info = st.session_state.session_info
            st.markdown(f"**Created:** {info.get('created_at', 'N/A')}")
            st.markdown(f"**Messages:** {info.get('message_count', 0)}")
            
            # Display expiration information
            status, hours = get_expiration_status(info)
            
            if status == "Expired":
                st.markdown(f"**Status:** ❌ Expired")
                if st.button("🔄 Create New Session", use_container_width=True):
                    new_session_id = create_backend_session()
                    if new_session_id:
                        st.session_state.session_id = new_session_id
                        st.session_state.messages = []
                        st.query_params["session"] = new_session_id
                        st.rerun()
            elif status == "Expiring soon":
                st.markdown(f"**Status:** ⚠️ {status}")
                st.markdown(f"**Expires in:** {hours:.1f} hours ({hours*60:.0f} minutes)")
                st.progress(max(0, min(1, hours/24)), text=f"{hours:.1f}h remaining")
            else:
                st.markdown(f"**Status:** ✅ {status}")
                st.markdown(f"**Expires in:** {hours:.1f} hours")
                st.progress(max(0, min(1, hours/24)), text=f"{hours:.1f}h remaining")
            
            if info.get('topics'):
                st.markdown("**Recent Topics:**")
                for topic in info['topics'][-3:]:
                    st.markdown(f"- {topic}")
    
    # Add a separator
    st.divider()
    
    # Quick actions
    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh Session", use_container_width=True) and st.session_state.session_id:
        st.session_state.loading_history = True
        st.rerun()

# Main app logic
st.title("🏠 LeaseMate Policy Assistant")
st.caption("General Policy | JES | REASONING")

# Check backend connection first
if not st.session_state.backend_connected:
    st.warning("⚠️ Waiting for backend connection...")
    if check_backend_connection():
        st.session_state.backend_connected = True
        st.session_state.initial_load_complete = False
        st.rerun()

# Ensure session exists on backend when app starts with force reload
if not st.session_state.initial_load_complete and st.session_state.backend_connected:
    with st.spinner("Initializing session..."):
        if st.session_state.session_id:
            # Try to load existing session
            if load_conversation_history(st.session_state.session_id):
                st.session_state.session_created = True
                st.session_state.initial_load_complete = True
                st.session_state.force_reload_needed = True
            else:
                # Session might be expired, create new one
                new_session_id = create_backend_session()
                if new_session_id:
                    st.session_state.session_id = new_session_id
                    st.session_state.messages = []
                    st.query_params["session"] = new_session_id
                    st.session_state.session_created = True
                    st.session_state.initial_load_complete = True
                    st.session_state.force_reload_needed = True
        else:
            # No session ID, create new one
            new_session_id = create_backend_session()
            if new_session_id:
                st.session_state.session_id = new_session_id
                st.query_params["session"] = new_session_id
                st.session_state.session_created = True
                st.session_state.initial_load_complete = True
                st.session_state.force_reload_needed = True

# Perform force reload after initial load is complete
if st.session_state.force_reload_needed and st.session_state.backend_connected:
    st.session_state.force_reload_needed = False
    with st.spinner("Force reloading session data..."):
        if st.session_state.session_id:
            load_conversation_history(st.session_state.session_id)
            time.sleep(0.5)
            st.rerun()

# Load history if triggered by refresh button
if st.session_state.loading_history and st.session_state.session_id:
    with st.spinner("Loading conversation history..."):
        load_conversation_history(st.session_state.session_id)
        st.session_state.loading_history = False
        st.rerun()

# Display connection warning if backend is down
if not st.session_state.backend_connected:
    st.error("""
    ### 🔌 Backend Server Not Connected
    
    Please ensure your FastAPI backend is running:
    
    1. Open a terminal
    2. Navigate to your backend directory
    3. Run: `uvicorn main:app --reload --port 8000`
    4. Refresh this page
    
    If you're using a different port or URL, update the BACKEND_URL variables in the code.
    """)
    st.stop()

# Check if session is expired before displaying messages
if st.session_state.session_info:
    status, _ = get_expiration_status(st.session_state.session_info)
    if status == "Expired":
        st.warning("⚠️ Your session has expired. Please create a new session.")
        if st.button("🆕 Create New Session"):
            new_session_id = create_backend_session()
            if new_session_id:
                st.session_state.session_id = new_session_id
                st.session_state.messages = []
                st.query_params["session"] = new_session_id
                st.rerun()
        st.stop()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your lease policies"):
    if not st.session_state.session_id:
        st.error("No active session. Please refresh the page.")
        st.stop()
    
    if not st.session_state.backend_connected:
        st.error("Backend not connected. Please check your server.")
        st.stop()
    
    # Check if session is expired before sending message
    if st.session_state.session_info:
        status, _ = get_expiration_status(st.session_state.session_info)
        if status == "Expired":
            st.error("Your session has expired. Please create a new session.")
            st.stop()
    
    # Add user message to UI
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Show spinner while processing
    with st.spinner("Searching policies..."):
        try:
            # Send request with session_id
            session = create_requests_session()
            response = session.post(
                BACKEND_URL,
                json={
                    "prompt": prompt,
                    "session_id": st.session_state.session_id
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])
                
                # Refresh session info after message
                get_session_info(st.session_state.session_id)

                # Display assistant response with very fast typing effect
                display_assistant_response(answer, sources, BACKEND_BASE_URL)

                # Add assistant message to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            else:
                st.error(f"❌ Backend returned an error: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Lost connection to backend server")
            st.session_state.backend_connected = False
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Footer with session stats
if st.session_state.session_id and st.session_state.backend_connected and st.session_state.session_info:
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"💬 Messages: {len(st.session_state.messages)}")
    with col2:
        status, hours = get_expiration_status(st.session_state.session_info)
        if status == "Expired":
            st.caption(f"⏱️ Session: Expired")
        elif status == "Expiring soon":
            st.caption(f"⏱️ Expires: {hours:.1f}h ⚠️")
        else:
            st.caption(f"⏱️ Expires: {hours:.1f}h")
    with col3:
        st.caption(f"🔑 Session active")
