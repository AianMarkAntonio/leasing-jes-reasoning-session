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

# Function to create a new session using backend API
def create_backend_session(existing_session_id=None):
    """Create a new session using the backend /sessions/new endpoint"""
    try:
        new_session_url = f"{BACKEND_BASE_URL}/api/v1/sessions/new"
        
        # Prepare request body if we have an existing session ID to reuse
        payload = {}
        if existing_session_id:
            payload = {"session_id": existing_session_id}
        
        response = requests.post(
            new_session_url,
            json=payload if payload else None,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            
            # Store session info
            st.session_state.session_info = {
                "created_at": data.get("created_at"),
                "message_count": data.get("message_count", 0),
                "updated_at": data.get("updated_at")
            }
            
            return session_id
        else:
            st.error(f"Failed to create session: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return None

# Function to load conversation history
def load_conversation_history(session_id):
    """Load conversation history from backend using /sessions/{session_id}/history endpoint"""
    try:
        history_url = f"{BACKEND_BASE_URL}/api/v1/sessions/{session_id}/history"
        response = requests.get(history_url, timeout=10)
        
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
            
            return True
        elif response.status_code == 404:
            # Session doesn't exist, create new one
            new_session_id = create_backend_session()
            if new_session_id:
                st.session_state.session_id = new_session_id
                st.query_params["session"] = new_session_id
                return True
    except Exception as e:
        st.error(f"Failed to load history: {e}")
        return False

# Function to get session info
def get_session_info(session_id):
    """Get detailed session info using /sessions/{session_id}/info endpoint"""
    try:
        info_url = f"{BACKEND_BASE_URL}/api/v1/sessions/{session_id}/info"
        response = requests.get(info_url, timeout=10)
        
        if response.status_code == 200:
            st.session_state.session_info = response.json()
            return True
    except Exception as e:
        # Non-critical error, just log it
        print(f"Failed to get session info: {e}")
        return False

# Function to delete session
def delete_backend_session(session_id):
    """Delete session using /sessions/{session_id} endpoint"""
    try:
        delete_url = f"{BACKEND_BASE_URL}/api/v1/sessions/{session_id}"
        response = requests.delete(delete_url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting session: {e}")
        return False

# Sidebar for session management
with st.sidebar:
    st.header("🔐 Session Management")
    
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
                        st.query_params["session"] = new_session_id
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Failed to delete session")
    
    # Session info expander
    if st.session_state.session_info:
        with st.expander("📊 Session Info"):
            info = st.session_state.session_info
            st.markdown(f"**Created:** {info.get('created_at', 'N/A')[:10]}")
            st.markdown(f"**Messages:** {info.get('message_count', 0)}")
            st.markdown(f"**Expires:** {info.get('expires_in_hours', 0):.1f} hours")
            
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

# Ensure session exists on backend when app starts
if not st.session_state.session_created:
    with st.spinner("Initializing session..."):
        if st.session_state.session_id:
            # Try to load existing session
            if load_conversation_history(st.session_state.session_id):
                st.session_state.session_created = True
            else:
                # Session might be expired, create new one
                new_session_id = create_backend_session()
                if new_session_id:
                    st.session_state.session_id = new_session_id
                    st.session_state.messages = []
                    st.query_params["session"] = new_session_id
                    st.session_state.session_created = True
        else:
            # No session ID, create new one
            new_session_id = create_backend_session()
            if new_session_id:
                st.session_state.session_id = new_session_id
                st.query_params["session"] = new_session_id
                st.session_state.session_created = True

# Load history if triggered by refresh button
if st.session_state.loading_history and st.session_state.session_id:
    with st.spinner("Loading conversation history..."):
        load_conversation_history(st.session_state.session_id)
        st.session_state.loading_history = False
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your lease policies"):
    if not st.session_state.session_id:
        st.error("No active session. Please refresh the page.")
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
            response = requests.post(
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

                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown("### Answer")
                    st.markdown(answer)

                    if sources:
                        with st.expander("📌 Sources"):
                            for src in sources:
                                file_name = src.get("file_name", "Unknown document")
                                download_url = src.get("download_url")

                                st.markdown(f"**📄 {file_name}**")

                                if download_url:
                                    full_url = f"{BACKEND_BASE_URL}{download_url}"
                                    st.markdown(
                                        f"[⬇️ Source]({full_url})",
                                        unsafe_allow_html=True
                                    )

                                st.markdown("---")

                # Add assistant message to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            else:
                st.error(f"❌ Backend returned an error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection failed: {e}")

# Footer with session stats
if st.session_state.session_id:
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"💬 Messages: {len(st.session_state.messages)}")
    with col2:
        if st.session_state.session_info:
            expires = st.session_state.session_info.get('expires_in_hours', 0)
            st.caption(f"⏱️ Expires: {expires:.1f}h")
    with col3:
        st.caption(f"🔑 Session active")
