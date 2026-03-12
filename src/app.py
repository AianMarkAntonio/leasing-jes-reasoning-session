import streamlit as st
import requests
import uuid
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    /* Status messages styling */
    .status-success {
        color: #0f5132;
        background-color: #d1e7dd;
        border: 1px solid #badbcc;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .status-warning {
        color: #664d03;
        background-color: #fff3cd;
        border: 1px solid #ffecb5;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .status-info {
        color: #055160;
        background-color: #cff4fc;
        border: 1px solid #b6effb;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with proper defaults
def init_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        "messages": [],
        "session_id": None,
        "history_loaded": False,
        "last_check": time.time(),
        "session_creation_in_progress": False,
        "session_creation_retries": 0,
        "max_retries": 3,
        "backend_available": True,
        "last_error": None,
        "initialization_complete": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Helper function to check if session is client-side generated
def is_client_session(session_id):
    """Check if session ID is client-generated (UUID format)"""
    return session_id and len(session_id) == 36 and '-' in session_id

# Function to create session with retry logic
def create_new_session(max_retries=3):
    """Create a new session with retry logic and exponential backoff"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to create session (attempt {attempt + 1}/{max_retries})")
            
            response = requests.post(
                f"{BACKEND_URL}/sessions/new", 
                timeout=30,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and "session_id" in data and data["session_id"]:
                    logger.info(f"Session created successfully: {data['session_id'][:8]}...")
                    st.session_state.backend_available = True
                    return data["session_id"]
                else:
                    logger.warning(f"Invalid response format: {data}")
            else:
                logger.warning(f"Session creation failed with status {response.status_code}: {response.text[:100]}")
            
            # Exponential backoff
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # 1, 2, 4 seconds
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                
        except requests.exceptions.Timeout:
            logger.warning(f"Session creation timeout (attempt {attempt + 1})")
            st.session_state.backend_available = False
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error: {e}")
            st.session_state.backend_available = False
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        except Exception as e:
            logger.error(f"Unexpected error in session creation: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    # If all retries fail, generate a client-side UUID as fallback
    logger.warning("All session creation attempts failed, using client-side UUID")
    st.session_state.backend_available = False
    return str(uuid.uuid4())

# Handle URL session ID parameter
query_params = st.query_params
url_session_id = query_params.get("session_id")

if url_session_id and url_session_id != "None" and url_session_id != st.session_state.session_id:
    logger.info(f"Found session ID in URL: {url_session_id[:8]}...")
    st.session_state.session_id = url_session_id
    st.session_state.history_loaded = False
    st.session_state.session_creation_in_progress = False

# Main session creation logic
if not st.session_state.session_id and not st.session_state.session_creation_in_progress:
    st.session_state.session_creation_in_progress = True
    
    # Show initialization status
    status_container = st.empty()
    
    try:
        # Show initializing message
        status_container.markdown(
            '<div class="status-info">🔄 Initializing session... Please wait.</div>',
            unsafe_allow_html=True
        )
        
        # Attempt to create session
        session_id = create_new_session(max_retries=st.session_state.max_retries)
        
        if session_id:
            st.session_state.session_id = session_id
            st.query_params["session_id"] = session_id
            st.session_state.history_loaded = False  # Will load history separately
            st.session_state.session_creation_retries = 0
            
            # Show success message
            if st.session_state.backend_available:
                status_container.markdown(
                    '<div class="status-success">✅ Session initialized successfully!</div>',
                    unsafe_allow_html=True
                )
            else:
                status_container.markdown(
                    '<div class="status-warning">⚠️ Running in offline mode with local session</div>',
                    unsafe_allow_html=True
                )
            
            time.sleep(1.5)  # Brief pause to show status
            status_container.empty()
            
        else:
            # This should never happen as we always return a UUID
            st.session_state.session_id = str(uuid.uuid4())
            st.query_params["session_id"] = st.session_state.session_id
            status_container.markdown(
                '<div class="status-warning">⚠️ Using local session mode</div>',
                unsafe_allow_html=True
            )
            time.sleep(1.5)
            status_container.empty()
            
    except Exception as e:
        logger.error(f"Critical error in session creation: {e}")
        st.session_state.session_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.session_id
        st.session_state.last_error = str(e)
        
        status_container.markdown(
            f'<div class="status-warning">⚠️ Using local session mode: {str(e)[:50]}</div>',
            unsafe_allow_html=True
        )
        time.sleep(2)
        status_container.empty()
    
    finally:
        st.session_state.session_creation_in_progress = False
        st.session_state.initialization_complete = True
        st.rerun()

# Load conversation history (only for server-side sessions)
if (st.session_state.session_id and 
    not st.session_state.history_loaded and 
    len(st.session_state.messages) == 0 and
    not st.session_state.session_creation_in_progress and
    st.session_state.backend_available and
    not is_client_session(st.session_state.session_id)):
    
    try:
        with st.spinner("Loading conversation history..."):
            logger.info(f"Loading history for session: {st.session_state.session_id[:8]}...")
            
            response = requests.get(
                f"{BACKEND_URL}/sessions/{st.session_state.session_id}/history",
                params={"max_messages": 50},
                timeout=30,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                if messages:
                    st.session_state.messages = []
                    for msg in messages:
                        if msg.get("role") and msg.get("content"):
                            st.session_state.messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                    logger.info(f"Loaded {len(messages)} messages")
                
                st.session_state.history_loaded = True
                
            elif response.status_code == 404:
                # Session expired or not found, mark for recreation
                logger.warning(f"Session {st.session_state.session_id[:8]}... not found on server")
                st.warning("Session not found on server. Creating new one...")
                st.session_state.session_id = None
                st.session_state.history_loaded = False
                st.session_state.backend_available = True  # Backend is available, just session missing
                time.sleep(1)
                st.rerun()
            else:
                logger.warning(f"Failed to load history: {response.status_code}")
                st.session_state.history_loaded = True
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error loading history: {e}")
        st.session_state.backend_available = False
        st.session_state.history_loaded = True
        st.warning("Unable to load conversation history. Running in offline mode.")
        
    except Exception as e:
        logger.error(f"Unexpected error loading history: {e}")
        st.session_state.history_loaded = True
else:
    # Mark history as loaded for client-side sessions or when backend is unavailable
    if (st.session_state.session_id and 
        not st.session_state.history_loaded and 
        (is_client_session(st.session_state.session_id) or not st.session_state.backend_available)):
        st.session_state.history_loaded = True

# Check session expiration periodically
if (time.time() - st.session_state.last_check > 30 and 
    st.session_state.session_id and 
    not st.session_state.session_creation_in_progress and
    st.session_state.backend_available and
    not is_client_session(st.session_state.session_id)):
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/sessions/{st.session_state.session_id}/info",
            timeout=30,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            info = response.json()
            if info.get("is_expired", False):
                logger.info(f"Session {st.session_state.session_id[:8]}... expired, creating new one")
                st.warning("Session expired. Creating new one...")
                st.session_state.session_id = None
                st.session_state.messages = []
                st.session_state.history_loaded = False
                st.rerun()
        elif response.status_code == 404:
            # Session not found, create new one
            logger.info(f"Session {st.session_state.session_id[:8]}... not found, creating new one")
            st.session_state.session_id = None
            st.session_state.messages = []
            st.session_state.history_loaded = False
            st.rerun()
            
    except requests.exceptions.RequestException:
        # Silently fail for expiration checks
        st.session_state.backend_available = False
        
    except Exception as e:
        logger.error(f"Error checking session expiration: {e}")
    
    st.session_state.last_check = time.time()

# Sidebar
with st.sidebar:
    st.title("💬 Session Management")
    
    # Backend status indicator
    if st.session_state.backend_available:
        st.success("🟢 Backend Connected")
    else:
        st.error("🔴 Backend Disconnected (Offline Mode)")
    
    st.markdown("---")
    st.markdown("### Current Session")
    
    # Get session info if backend available
    session_info = None
    if (st.session_state.session_id and 
        st.session_state.backend_available and 
        not is_client_session(st.session_state.session_id)):
        try:
            info_response = requests.get(
                f"{BACKEND_URL}/sessions/{st.session_state.session_id}/info",
                timeout=30,
                headers={"Accept": "application/json"}
            )
            if info_response.status_code == 200:
                session_info = info_response.json()
        except:
            pass
    
    col1, col2 = st.columns(2)
    with col1:
        session_display = st.session_state.session_id
        if session_display:
            display_id = session_display[:8] + "..." if len(session_display) > 8 else session_display
            if is_client_session(session_display):
                display_id += " (local)"
        else:
            display_id = "None"
        st.metric("Session ID", f"`{display_id}`")
    with col2:
        st.metric("Messages", len(st.session_state.messages))
    
    if session_info:
        expires_in = session_info.get("expires_in_seconds", 0)
        created_at = session_info.get("created_at", "")
        
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                st.caption(f"Created: {created.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass
        
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
                with st.spinner("Creating new session..."):
                    # Create new session
                    session_id = create_new_session(max_retries=2)
                    
                    if session_id:
                        st.session_state.session_id = session_id
                        st.session_state.messages = []
                        st.session_state.history_loaded = False
                        st.query_params["session_id"] = session_id
                        st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🗑️ Delete", use_container_width=True):
            try:
                if (st.session_state.session_id and 
                    st.session_state.backend_available and 
                    not is_client_session(st.session_state.session_id)):
                    try:
                        requests.delete(
                            f"{BACKEND_URL}/sessions/{st.session_state.session_id}",
                            timeout=30
                        )
                    except:
                        pass
                
                # Create new session
                session_id = create_new_session(max_retries=2)
                
                if session_id:
                    st.session_state.session_id = session_id
                    st.session_state.messages = []
                    st.session_state.history_loaded = False
                    st.query_params["session_id"] = session_id
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Admin section
    with st.expander("🔧 Admin", expanded=False):
        if st.button("🧹 Cleanup Expired Sessions"):
            if st.session_state.backend_available:
                try:
                    cleanup_response = requests.post(
                        f"{BACKEND_URL}/sessions/cleanup",
                        timeout=30
                    )
                    if cleanup_response.status_code == 200:
                        data = cleanup_response.json()
                        st.success(f"Cleaned up {data.get('removed_sessions', 0)} sessions")
                    else:
                        st.error("Cleanup failed")
                except:
                    st.error("Could not connect to backend")
            else:
                st.warning("Backend not available")
        
        # Show session stats
        if st.session_state.backend_available:
            try:
                stats_response = requests.get(
                    f"{BACKEND_URL}/sessions/stats",
                    timeout=30,
                    headers={"Accept": "application/json"}
                )
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    st.metric("Active Sessions", stats.get("active_sessions", 0))
                    st.metric("Total Messages", stats.get("total_messages_stored", 0))
                    st.metric("Storage", f"{stats.get('total_size_mb', 0):.2f} MB")
            except:
                st.warning("Stats unavailable")
        
        # Debug info
        with st.expander("Debug Info", expanded=False):
            st.json({
                "session_id": st.session_state.session_id[:8] + "..." if st.session_state.session_id else None,
                "is_client_session": is_client_session(st.session_state.session_id) if st.session_state.session_id else False,
                "messages": len(st.session_state.messages),
                "history_loaded": st.session_state.history_loaded,
                "backend_available": st.session_state.backend_available,
                "initialization_complete": st.session_state.initialization_complete
            })

# Main chat interface
st.title("🏠 LeaseMate Policy Assistant")
st.caption("General Policy | JES | REASONING | Conversational AI")

# Show offline mode warning if needed
if not st.session_state.backend_available and st.session_state.session_id:
    st.warning("⚠️ Running in offline mode. Chat history won't be saved.")

# Display messages
if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
else:
    with st.chat_message("assistant"):
        welcome_message = "👋 Hello! I'm your LeaseMate Policy Assistant. How can I help you with lease policies today?"
        if not st.session_state.backend_available:
            welcome_message += "\n\n*(Note: Running in offline mode - chat history won't be saved)*"
        st.markdown(welcome_message)

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
            # Prepare request payload
            payload = {
                "prompt": prompt,
                "session_id": st.session_state.session_id
            }
            
            # Make the API request if backend is available
            if st.session_state.backend_available:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json=payload,
                    timeout=60,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )
            else:
                # Simulate response in offline mode
                response = None
                time.sleep(1)  # Simulate processing
                answer = "I'm currently in offline mode. Please check your connection to the backend service."
                data = {"answer": answer, "sources": [], "session_id": st.session_state.session_id}
            
            # Clear typing indicator
            typing_placeholder.empty()
            
            if st.session_state.backend_available and response.status_code == 200:
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
                streamed_answer = stream_text(answer, delay=0.001)
                
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
                
            elif not st.session_state.backend_available:
                # Handle offline mode response
                answer = "I'm currently in offline mode. Please check your connection to the backend service."
                st.markdown(f"### Answer\n\n{answer}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
            else:
                error_message = f"❌ Backend error: {response.status_code}"
                st.error(error_message)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {error_message}"
                })
                
        except requests.exceptions.Timeout:
            typing_placeholder.empty()
            st.error("❌ Request timeout. Please try again.")
            st.session_state.backend_available = False
            
        except requests.exceptions.ConnectionError as e:
            typing_placeholder.empty()
            st.error("❌ Cannot connect to backend. Running in offline mode.")
            st.session_state.backend_available = False
            
            # Provide offline response
            answer = "I'm currently unable to connect to the backend service. Please check your connection and try again."
            st.markdown(f"### Answer\n\n{answer}")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })
            
        except requests.exceptions.RequestException as e:
            typing_placeholder.empty()
            st.error(f"❌ Connection failed: {e}")
            st.session_state.backend_available = False
            
        except Exception as e:
            typing_placeholder.empty()
            st.error(f"❌ Unexpected error: {e}")
            logger.error(f"Chat error: {e}")

# Footer
st.markdown("---")
st.caption("© 2024 LeaseMate - Policy Assistant")
