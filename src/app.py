# import streamlit as st
# import requests
# from datetime import datetime
# import time
# import uuid

# # Configuration
# BACKEND_URL = "http://127.0.0.1:8000/api/v1"
# BACKEND_BASE_URL = "http://127.0.0.1:8000"

# st.set_page_config(
#     page_title="LeaseMate Policy Assistant",
#     page_icon="🏠",
#     layout="wide"
# )

# # ------------------------------------------------------------
# # URL Parameter Handling
# # ------------------------------------------------------------
# def get_session_from_url():
#     """Extract session_id from URL query parameters"""
#     query_params = st.query_params
#     return query_params.get("session", None)

# def update_url_with_session(session_id):
#     """Update URL to include session_id"""
#     if session_id:
#         st.query_params["session"] = session_id
#     else:
#         # Clear session param for new chat
#         if "session" in st.query_params:
#             del st.query_params["session"]

# def clear_url_session():
#     """Remove session_id from URL"""
#     if "session" in st.query_params:
#         del st.query_params["session"]

# # Initialize session state
# if "current_session_id" not in st.session_state:
#     # Try to get session from URL first
#     url_session = get_session_from_url()
#     st.session_state.current_session_id = url_session
# if "chat_threads" not in st.session_state:
#     st.session_state.chat_threads = {}  # session_id -> list of messages
# if "thread_titles" not in st.session_state:
#     st.session_state.thread_titles = {}  # session_id -> title
# if "loading_threads" not in st.session_state:
#     st.session_state.loading_threads = False
# if "delete_in_progress" not in st.session_state:
#     st.session_state.delete_in_progress = False
# if "last_deleted" not in st.session_state:
#     st.session_state.last_deleted = None
# if "error_message" not in st.session_state:
#     st.session_state.error_message = None
# if "confirm_delete" not in st.session_state:
#     st.session_state.confirm_delete = {}  # session_id -> bool
# if "session_start_time" not in st.session_state:
#     st.session_state.session_start_time = {}  # track when sessions started
# if "new_chat_token" not in st.session_state:
#     st.session_state.new_chat_token = None
# if "initial_load_done" not in st.session_state:
#     st.session_state.initial_load_done = False

# # ------------------------------------------------------------
# # Helper Functions
# # ------------------------------------------------------------
# def fetch_all_sessions():
#     """Fetch all active sessions from backend"""
#     try:
#         response = requests.get(f"{BACKEND_URL}/sessions", timeout=5)
#         if response.status_code == 200:
#             return response.json()
#     except:
#         pass
#     return []

# def fetch_session_messages(session_id):
#     """Fetch messages for a specific session"""
#     try:
#         response = requests.get(
#             f"{BACKEND_URL}/sessions/{session_id}/messages",
#             params={"limit": 100, "include_full": True},
#             timeout=5
#         )
#         if response.status_code == 200:
#             data = response.json()
#             return data.get("messages", [])
#     except:
#         pass
#     return []

# def generate_thread_title(messages):
#     """Generate a title from the first user message"""
#     for msg in messages:
#         if msg.get("role") == "user":
#             content = msg.get("content", "")
#             # Truncate and clean
#             if len(content) > 30:
#                 return content[:30] + "..."
#             return content
#     return "New Chat"

# def load_all_threads():
#     """Load all active sessions and their messages"""
#     if st.session_state.delete_in_progress:
#         return
        
#     st.session_state.loading_threads = True
    
#     # Get all sessions
#     sessions = fetch_all_sessions()
    
#     # Load messages for each session
#     for session_info in sessions:
#         session_id = session_info["session_id"]
        
#         # Skip if already loaded
#         if session_id in st.session_state.chat_threads:
#             continue
            
#         # Fetch messages
#         messages = fetch_session_messages(session_id)
        
#         if messages:
#             # Store messages
#             st.session_state.chat_threads[session_id] = messages
            
#             # Generate and store title
#             if session_id not in st.session_state.thread_titles:
#                 st.session_state.thread_titles[session_id] = generate_thread_title(messages)
            
#             # Track when this session was loaded
#             if session_id not in st.session_state.session_start_time:
#                 st.session_state.session_start_time[session_id] = time.time()
    
#     st.session_state.loading_threads = False

# def load_specific_session(session_id):
#     """Load a specific session if not already loaded"""
#     if session_id and session_id not in st.session_state.chat_threads:
#         messages = fetch_session_messages(session_id)
#         if messages:
#             st.session_state.chat_threads[session_id] = messages
#             if session_id not in st.session_state.thread_titles:
#                 st.session_state.thread_titles[session_id] = generate_thread_title(messages)
#             if session_id not in st.session_state.session_start_time:
#                 st.session_state.session_start_time[session_id] = time.time()
#             return True
#     return False

# def switch_thread(session_id):
#     """Switch to a different thread and update URL"""
#     st.session_state.current_session_id = session_id
#     st.session_state.error_message = None
    
#     # Update URL with session_id
#     update_url_with_session(session_id)

# def reset_backend_session(session_id):
#     """Reset a specific backend session to clear context"""
#     try:
#         # Try to reset the session context
#         response = requests.post(
#             f"{BACKEND_URL}/sessions/{session_id}/reset",
#             timeout=5
#         )
#         return response.status_code == 200
#     except:
#         return False

# def delete_thread(session_id):
#     """Delete a thread/session"""
#     st.session_state.delete_in_progress = True
#     st.session_state.error_message = None
    
#     try:
#         # Send delete request to backend
#         response = requests.delete(f"{BACKEND_URL}/sessions/{session_id}", timeout=10)
        
#         if response.status_code == 200:
#             # Success - remove from local state
#             if session_id in st.session_state.chat_threads:
#                 del st.session_state.chat_threads[session_id]
#             if session_id in st.session_state.thread_titles:
#                 del st.session_state.thread_titles[session_id]
#             if session_id in st.session_state.confirm_delete:
#                 del st.session_state.confirm_delete[session_id]
#             if session_id in st.session_state.session_start_time:
#                 del st.session_state.session_start_time[session_id]
            
#             # If current session was deleted, clear it and URL
#             if st.session_state.current_session_id == session_id:
#                 st.session_state.current_session_id = None
#                 clear_url_session()
            
#             # Record successful deletion
#             st.session_state.last_deleted = session_id
#             st.session_state.delete_in_progress = False
            
#             # Use a toast for success message
#             st.toast("✅ Thread deleted successfully!", icon="🗑️")
            
#             # Force a complete rerun after a tiny delay
#             time.sleep(0.1)
#             st.rerun()
#         else:
#             # Backend error
#             st.session_state.error_message = f"Failed to delete thread: Server returned {response.status_code}"
#             st.session_state.delete_in_progress = False
            
#     except requests.exceptions.ConnectionError:
#         st.session_state.error_message = "❌ Cannot connect to server. Please check if the backend is running."
#         st.session_state.delete_in_progress = False
#     except requests.exceptions.Timeout:
#         st.session_state.error_message = "❌ Request timed out. Please try again."
#         st.session_state.delete_in_progress = False
#     except Exception as e:
#         st.session_state.error_message = f"❌ An error occurred: {str(e)}"
#         st.session_state.delete_in_progress = False

# def create_new_thread():
#     """Create a new empty thread and clear URL"""
#     # If there was a previous session, just switch away from it
#     st.session_state.current_session_id = None
    
#     # Clear session from URL
#     clear_url_session()
    
#     # Generate a temporary local ID to ensure uniqueness
#     st.session_state.new_chat_token = str(uuid.uuid4())
    
#     # Clear any error messages
#     st.session_state.error_message = None
    
#     # Show a clear indicator that this is a new conversation
#     st.toast("✨ Starting fresh conversation!", icon="🆕")

# def format_timestamp(timestamp_str):
#     """Format timestamp for display"""
#     try:
#         dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
#         now = datetime.now(dt.tzinfo)
#         diff = now - dt
        
#         if diff.days == 0:
#             if diff.seconds < 3600:
#                 return f"{diff.seconds // 60}m ago"
#             else:
#                 return f"{diff.seconds // 3600}h ago"
#         elif diff.days == 1:
#             return "Yesterday"
#         elif diff.days < 7:
#             return f"{diff.days} days ago"
#         else:
#             return dt.strftime("%b %d")
#     except:
#         return ""

# def clear_stale_state():
#     """Clear any stale state that might cause issues"""
#     # Clear error message after 5 seconds
#     if st.session_state.error_message and not st.session_state.delete_in_progress:
#         if "error_time" not in st.session_state:
#             st.session_state.error_time = time.time()
#         elif time.time() - st.session_state.error_time > 5:
#             st.session_state.error_message = None
#             st.session_state.error_time = None

# # ------------------------------------------------------------
# # Initial Load - Handle URL session
# # ------------------------------------------------------------
# if not st.session_state.initial_load_done:
#     # Load all threads in background
#     load_all_threads()
    
#     # If there's a session in URL, load it specifically
#     url_session = get_session_from_url()
#     if url_session:
#         load_specific_session(url_session)
#         st.session_state.current_session_id = url_session
    
#     st.session_state.initial_load_done = True

# # ------------------------------------------------------------
# # Sidebar - Thread Management
# # ------------------------------------------------------------
# with st.sidebar:
#     st.title("🏠 LeaseMate")
    
#     # New Chat button
#     if st.button("➕ New Chat", use_container_width=True, type="primary", disabled=st.session_state.delete_in_progress):
#         create_new_thread()
#         st.rerun()
    
#     st.divider()
    
#     # Display loading indicator
#     if st.session_state.loading_threads:
#         st.info("Loading conversations...")
    
#     # Display any error message
#     if st.session_state.error_message:
#         st.error(st.session_state.error_message)
#         clear_stale_state()
    
#     # Display all threads
#     if st.session_state.chat_threads:
#         st.caption("YOUR CONVERSATIONS")
        
#         # Sort threads by most recent message
#         sorted_threads = sorted(
#             st.session_state.chat_threads.items(),
#             key=lambda x: max(
#                 (m.get("timestamp", "") for m in x[1] if m.get("timestamp")),
#                 default=""
#             ),
#             reverse=True
#         )
        
#         for session_id, messages in sorted_threads:
#             # Skip if this session was just deleted
#             if session_id == st.session_state.last_deleted:
#                 continue
                
#             title = st.session_state.thread_titles.get(session_id, "Chat")
            
#             # Get last message time
#             last_msg = next(
#                 (m for m in reversed(messages) if m.get("timestamp")),
#                 None
#             )
#             timestamp = format_timestamp(last_msg.get("timestamp")) if last_msg else ""
            
#             # Check if this is the active thread
#             is_active = session_id == st.session_state.current_session_id
            
#             # Use a container to ensure proper alignment
#             with st.container():
#                 # Create columns with better proportions for alignment
#                 col1, col2 = st.columns([0.85, 0.15])
                
#                 with col1:
#                     # Thread button with fixed height
#                     button_key = f"thread_{session_id}"
                    
#                     # Custom CSS for consistent button height and alignment
#                     if is_active:
#                         st.markdown(f"""
#                         <style>
#                             div[key="{button_key}"] button {{
#                                 background-color: #e6f3ff !important;
#                                 border-left: 4px solid #1E88E5 !important;
#                                 font-weight: bold !important;
#                                 height: 45px !important;
#                                 display: flex !important;
#                                 align-items: center !important;
#                                 justify-content: flex-start !important;
#                                 padding: 0 10px !important;
#                                 margin: 2px 0 !important;
#                                 border-radius: 4px !important;
#                                 box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
#                                 white-space: nowrap !important;
#                                 overflow: hidden !important;
#                                 text-overflow: ellipsis !important;
#                                 width: 100% !important;
#                                 line-height: normal !important;
#                             }}
#                             div[key="{button_key}"] button:hover {{
#                                 background-color: #d4e9ff !important;
#                                 border-left: 4px solid #0d47a1 !important;
#                             }}
#                             div[key="{button_key}"] button p {{
#                                 margin: 0 !important;
#                                 line-height: 1.2 !important;
#                             }}
#                         </style>
#                         """, unsafe_allow_html=True)
#                         button_label = f"💬 **{title}**"
#                     else:
#                         st.markdown(f"""
#                         <style>
#                             div[key="{button_key}"] button {{
#                                 height: 45px !important;
#                                 display: flex !important;
#                                 align-items: center !important;
#                                 justify-content: flex-start !important;
#                                 padding: 0 10px !important;
#                                 margin: 2px 0 !important;
#                                 background-color: white !important;
#                                 border: 1px solid #ddd !important;
#                                 border-radius: 4px !important;
#                                 white-space: nowrap !important;
#                                 overflow: hidden !important;
#                                 text-overflow: ellipsis !important;
#                                 width: 100% !important;
#                                 line-height: normal !important;
#                             }}
#                             div[key="{button_key}"] button:hover {{
#                                 background-color: #f5f5f5 !important;
#                                 border-left: 4px solid #999 !important;
#                                 transition: all 0.2s ease;
#                             }}
#                             div[key="{button_key}"] button p {{
#                                 margin: 0 !important;
#                                 line-height: 1.2 !important;
#                             }}
#                         </style>
#                         """, unsafe_allow_html=True)
#                         button_label = f"💬 {title}"
                    
#                     # Thread button
#                     if st.button(
#                         button_label,
#                         key=button_key,
#                         use_container_width=True,
#                         help=f"Last message: {timestamp}" if timestamp else "No messages",
#                         disabled=st.session_state.delete_in_progress
#                     ):
#                         switch_thread(session_id)
#                         st.rerun()
                
#                 with col2:
#                     # Delete button container with vertical centering
#                     delete_key = f"delete_{session_id}"
#                     confirm_key = f"confirm_{session_id}"
                    
#                     # Check if this is in confirmation mode
#                     if session_id == st.session_state.current_session_id and session_id in st.session_state.confirm_delete:
#                         # Style for confirm button
#                         st.markdown(f"""
#                         <style>
#                             div[key="{confirm_key}"] button {{
#                                 height: 45px !important;
#                                 width: 45px !important;
#                                 display: flex !important;
#                                 align-items: center !important;
#                                 justify-content: center !important;
#                                 padding: 0 !important;
#                                 margin: 2px 0 !important;
#                                 background-color: #4CAF50 !important;
#                                 color: white !important;
#                                 border: none !important;
#                                 border-radius: 4px !important;
#                                 font-size: 18px !important;
#                                 font-weight: bold !important;
#                                 line-height: 1 !important;
#                             }}
#                             div[key="{confirm_key}"] button:hover {{
#                                 background-color: #45a049 !important;
#                                 transform: scale(1.05) !important;
#                             }}
#                         </style>
#                         """, unsafe_allow_html=True)
                        
#                         # Show confirmation checkmark
#                         if st.button(
#                             "✓",
#                             key=confirm_key,
#                             help="Click to confirm delete",
#                         ):
#                             delete_thread(session_id)
#                     else:
#                         # Style for delete button
#                         st.markdown(f"""
#                         <style>
#                             div[key="{delete_key}"] button {{
#                                 height: 45px !important;
#                                 width: 45px !important;
#                                 display: flex !important;
#                                 align-items: center !important;
#                                 justify-content: center !important;
#                                 padding: 0 !important;
#                                 margin: 2px 0 !important;
#                                 background-color: white !important;
#                                 border: 1px solid #ddd !important;
#                                 border-radius: 4px !important;
#                                 font-size: 18px !important;
#                                 line-height: 1 !important;
#                                 transition: all 0.2s ease !important;
#                             }}
#                             div[key="{delete_key}"] button:hover {{
#                                 background-color: #ffebee !important;
#                                 border-color: #f44336 !important;
#                                 color: #f44336 !important;
#                                 transform: scale(1.05) !important;
#                             }}
#                         </style>
#                         """, unsafe_allow_html=True)
                        
#                         # Normal delete button
#                         if st.button(
#                             "🗑️",
#                             key=delete_key,
#                             help="Delete conversation",
#                             disabled=st.session_state.delete_in_progress
#                         ):
#                             # For current thread, ask for confirmation first
#                             if session_id == st.session_state.current_session_id:
#                                 st.session_state.confirm_delete[session_id] = True
#                                 st.rerun()
#                             else:
#                                 # Delete directly for non-current threads
#                                 delete_thread(session_id)
                
#                 # Show cancel option for active thread in delete confirmation
#                 if session_id == st.session_state.current_session_id and session_id in st.session_state.confirm_delete:
#                     # Add a small cancel button in a new row
#                     col1, col2, col3 = st.columns([2, 2, 2])
#                     with col2:
#                         cancel_key = f"cancel_{session_id}"
#                         st.markdown(f"""
#                         <style>
#                             div[key="{cancel_key}"] button {{
#                                 height: 30px !important;
#                                 width: 100% !important;
#                                 font-size: 12px !important;
#                                 padding: 0 10px !important;
#                                 margin: 5px 0 !important;
#                                 background-color: #f5f5f5 !important;
#                                 border: 1px solid #ddd !important;
#                                 border-radius: 4px !important;
#                                 color: #666 !important;
#                             }}
#                             div[key="{cancel_key}"] button:hover {{
#                                 background-color: #e0e0e0 !important;
#                                 border-color: #999 !important;
#                             }}
#                         </style>
#                         """, unsafe_allow_html=True)
                        
#                         if st.button(
#                             "Cancel",
#                             key=cancel_key,
#                             help="Cancel deletion",
#                             use_container_width=True
#                         ):
#                             del st.session_state.confirm_delete[session_id]
#                             st.rerun()
    
#     st.divider()
#     st.caption("Ask me about rental rates, security deposits, policy guidelines, and more...")

# # ------------------------------------------------------------
# # Main Chat Area
# # ------------------------------------------------------------
# # Clear any stale confirmations for non-current threads
# current_session = st.session_state.current_session_id
# for session_id in list(st.session_state.confirm_delete.keys()):
#     if session_id != current_session:
#         del st.session_state.confirm_delete[session_id]

# # Sync URL with current session (in case it changed)
# if current_session:
#     update_url_with_session(current_session)
# else:
#     clear_url_session()

# # Display current thread
# if st.session_state.current_session_id:
#     # Load existing thread
#     messages = st.session_state.chat_threads.get(st.session_state.current_session_id, [])
    
#     # Display thread title
#     thread_title = st.session_state.thread_titles.get(st.session_state.current_session_id, "Chat")
#     st.title(f"💬 {thread_title}")
# else:
#     # New thread
#     st.title("💬 New Chat")
    
#     # Show a hint that this is a fresh conversation
#     st.caption("This is a new conversation. Previous context has been cleared.")
#     messages = []

# # Display chat messages
# for message in messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
        
#         # Show sources for assistant messages
#         if message["role"] == "assistant" and "metadata" in message:
#             sources = message["metadata"].get("sources", [])
#             if sources:
#                 with st.expander("📎 View sources"):
#                     for src in sources:
#                         file_name = src.get("file_name", "Document")
#                         download_url = src.get("download_url")
                        
#                         st.markdown(f"**{file_name}**")
#                         if download_url:
#                             full_url = f"{BACKEND_BASE_URL}{download_url}"
#                             st.markdown(f"[⬇️ Download]({full_url})")
#                         st.divider()

# # Chat input
# if prompt := st.chat_input("Ask a question about lease policies...", disabled=st.session_state.delete_in_progress):
#     # Display user message immediately
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     # Show assistant thinking
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 # Prepare request
#                 endpoint = f"{BACKEND_URL}/chat/session"
#                 payload = {"prompt": prompt}
                
#                 # Add session_id if in an existing thread
#                 if st.session_state.current_session_id:
#                     payload["session_id"] = st.session_state.current_session_id
#                 else:
#                     # For new chat, add a flag to indicate fresh start
#                     payload["new_conversation"] = True
#                     # Add a unique token to ensure backend treats it as new
#                     if st.session_state.new_chat_token:
#                         payload["reset_token"] = st.session_state.new_chat_token
                
#                 # Make API call
#                 response = requests.post(
#                     endpoint,
#                     json=payload,
#                     timeout=60
#                 )
                
#                 if response.status_code == 200:
#                     data = response.json()
                    
#                     # Get session_id from response
#                     session_id = data["session_id"]
                    
#                     # Get response data
#                     answer = data.get("answer", "I couldn't find an answer.")
#                     sources = data.get("sources", [])
                    
#                     # Check if the answer contains references to previous conversations
#                     # This is a client-side check to warn about context leakage
#                     if "previous" in answer.lower() or "earlier" in answer.lower() or "before" in answer.lower():
#                         st.warning("⚠️ The response might be referencing previous conversations. If this is a new chat, please try rephrasing your question.")
                    
#                     # Display answer
#                     st.markdown(answer)
                    
#                     # Show sources
#                     if sources:
#                         with st.expander("📎 View sources"):
#                             for src in sources:
#                                 file_name = src.get("file_name", "Document")
#                                 download_url = src.get("download_url")
                                
#                                 st.markdown(f"**{file_name}**")
#                                 if download_url:
#                                     full_url = f"{BACKEND_BASE_URL}{download_url}"
#                                     st.markdown(f"[⬇️ Download]({full_url})")
#                                 st.divider()
                    
#                     # Update local state
#                     if session_id not in st.session_state.chat_threads:
#                         st.session_state.chat_threads[session_id] = []
                    
#                     # Add messages to thread
#                     st.session_state.chat_threads[session_id].append({
#                         "role": "user",
#                         "content": prompt,
#                         "timestamp": datetime.now().isoformat()
#                     })
                    
#                     st.session_state.chat_threads[session_id].append({
#                         "role": "assistant",
#                         "content": answer,
#                         "metadata": {"sources": sources},
#                         "timestamp": datetime.now().isoformat()
#                     })
                    
#                     # Generate/update thread title
#                     if session_id not in st.session_state.thread_titles:
#                         st.session_state.thread_titles[session_id] = generate_thread_title(
#                             st.session_state.chat_threads[session_id]
#                         )
                    
#                     # Track session start time
#                     if session_id not in st.session_state.session_start_time:
#                         st.session_state.session_start_time[session_id] = time.time()
                    
#                     # Set as current session and update URL
#                     st.session_state.current_session_id = session_id
#                     update_url_with_session(session_id)
                    
#                     # Clear any delete confirmations
#                     if session_id in st.session_state.confirm_delete:
#                         del st.session_state.confirm_delete[session_id]
                    
#                     # Clear new chat token
#                     if "new_chat_token" in st.session_state:
#                         st.session_state.new_chat_token = None
                    
#                     # Rerun to update UI
#                     st.rerun()
#                 else:
#                     st.error(f"Error: {response.status_code}")
                    
#             except requests.exceptions.ConnectionError:
#                 st.error("❌ Cannot connect to server. Please check if the backend is running.")
#             except Exception as e:
#                 st.error(f"❌ An error occurred: {str(e)}")

import streamlit as st
import requests
from datetime import datetime
import time
import uuid

# ============================================================
# Configuration
# ============================================================
BACKEND_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com/api/v1"
BACKEND_BASE_URL = "https://cvmuu2vznj.ap-southeast-1.awsapprunner.com"

st.set_page_config(
    page_title="LeaseMate Policy Assistant",
    page_icon="🏠",
    layout="wide"
)

# ============================================================
# URL Helpers
# ============================================================
def get_session_from_url():
    return st.query_params.get("session", None)

def update_url_with_session(session_id):
    if session_id:
        st.query_params["session"] = session_id
    else:
        st.query_params.pop("session", None)

def clear_url_session():
    st.query_params.pop("session", None)

# ============================================================
# Session State Initialization
# ============================================================
defaults = {
    "current_session_id": get_session_from_url(),
    "chat_threads": {},
    "thread_titles": {},
    "loading_threads": False,
    "delete_in_progress": False,
    "error_message": None,
    "session_start_time": {},
    "new_chat_token": None,
    "initial_load_done": False,
    "delete_target": None,   # modal delete target
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# Backend Helpers
# ============================================================
def fetch_all_sessions():
    try:
        r = requests.get(f"{BACKEND_URL}/sessions", timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def fetch_session_messages(session_id):
    try:
        r = requests.get(
            f"{BACKEND_URL}/sessions/{session_id}/messages",
            params={"limit": 100, "include_full": True},
            timeout=5
        )
        if r.status_code == 200:
            return r.json().get("messages", [])
    except:
        pass
    return []

def generate_thread_title(messages):
    for m in messages:
        if m.get("role") == "user":
            text = m.get("content", "")
            return text[:30] + "..." if len(text) > 30 else text
    return "New Chat"

# ============================================================
# Thread Loading
# ============================================================
def load_all_threads():
    if st.session_state.delete_in_progress:
        return

    st.session_state.loading_threads = True

    for s in fetch_all_sessions():
        sid = s["session_id"]
        if sid in st.session_state.chat_threads:
            continue

        msgs = fetch_session_messages(sid)
        if msgs:
            st.session_state.chat_threads[sid] = msgs
            st.session_state.thread_titles[sid] = generate_thread_title(msgs)
            st.session_state.session_start_time[sid] = time.time()

    st.session_state.loading_threads = False

def switch_thread(session_id):
    st.session_state.current_session_id = session_id
    update_url_with_session(session_id)

# ============================================================
# Delete Logic (FIXED)
# ============================================================
def delete_thread(session_id):
    st.session_state.delete_in_progress = True
    st.session_state.error_message = None

    try:
        response = requests.delete(
            f"{BACKEND_URL}/sessions/{session_id}",
            timeout=10
        )

        if response.status_code != 200:
            st.session_state.error_message = (
                f"Failed to delete conversation "
                f"(status {response.status_code})"
            )
            st.session_state.delete_in_progress = False
            return

        # Success
        st.session_state.chat_threads.pop(session_id, None)
        st.session_state.thread_titles.pop(session_id, None)
        st.session_state.session_start_time.pop(session_id, None)

        if st.session_state.current_session_id == session_id:
            st.session_state.current_session_id = None
            clear_url_session()

        st.toast("🗑️ Conversation deleted", icon="✅")
        st.session_state.delete_in_progress = False
        st.rerun()

    except requests.exceptions.Timeout:
        st.session_state.error_message = "❌ Delete request timed out."
        st.session_state.delete_in_progress = False

    except requests.exceptions.ConnectionError:
        st.session_state.error_message = "❌ Cannot connect to backend."
        st.session_state.delete_in_progress = False

# ============================================================
# Delete Confirmation Modal
# ============================================================
@st.dialog("Delete conversation?")
def delete_confirmation_modal(session_id):
    title = st.session_state.thread_titles.get(session_id, "This conversation")

    st.markdown(
        f"""
        ### 🗑️ Delete **{title}**
        This action **cannot be undone**.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.delete_target = None
            st.rerun()

    with col2:
        if st.button("🗑️ Delete", type="primary", use_container_width=True):
            st.session_state.delete_target = None
            delete_thread(session_id)

# ============================================================
# Initial Load
# ============================================================
if not st.session_state.initial_load_done:
    load_all_threads()
    st.session_state.initial_load_done = True

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.title("🏠 LeaseMate")

    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.current_session_id = None
        clear_url_session()
        st.toast("✨ New conversation started")
        st.rerun()

    st.divider()

    if st.session_state.loading_threads:
        st.info("Loading conversations...")

    for sid, msgs in st.session_state.chat_threads.items():
        col1, col2 = st.columns([0.85, 0.15])

        with col1:
            if st.button(
                f"💬 {st.session_state.thread_titles.get(sid)}",
                use_container_width=True,
                key=f"thread_{sid}"
            ):
                switch_thread(sid)
                st.rerun()

        with col2:
            if st.button(
                "🗑️",
                key=f"delete_{sid}",
                help="Delete conversation"
            ):
                st.session_state.delete_target = sid
                st.rerun()

# ============================================================
# Trigger Delete Modal
# ============================================================
if st.session_state.delete_target:
    delete_confirmation_modal(st.session_state.delete_target)

# ============================================================
# Main Chat Area
# ============================================================
if st.session_state.current_session_id:
    st.title(f"💬 {st.session_state.thread_titles.get(st.session_state.current_session_id)}")
    messages = st.session_state.chat_threads.get(st.session_state.current_session_id, [])
else:
    st.title("💬 New Chat")
    messages = []

# ============================================================
# Render Messages (WITH DOWNLOAD FEATURE)
# ============================================================
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # 📎 Download feature (restored)
        if message["role"] == "assistant" and "metadata" in message:
            sources = message["metadata"].get("sources", [])
            if sources:
                with st.expander("📎 View sources"):
                    for src in sources:
                        file_name = src.get("file_name", "Document")
                        download_url = src.get("download_url")

                        st.markdown(f"**{file_name}**")
                        if download_url:
                            full_url = f"{BACKEND_BASE_URL}{download_url}"
                            st.markdown(f"[⬇️ Download]({full_url})")
                        st.divider()

# ============================================================
# Chat Input
# ============================================================
if prompt := st.chat_input("Ask about lease policies…"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {"prompt": prompt}

            if st.session_state.current_session_id:
                payload["session_id"] = st.session_state.current_session_id
            else:
                payload["new_conversation"] = True
                payload["reset_token"] = str(uuid.uuid4())

            response = requests.post(
                f"{BACKEND_URL}/chat/session",
                json=payload,
                timeout=60
            )

            data = response.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            session_id = data["session_id"]

            st.markdown(answer)

            st.session_state.chat_threads.setdefault(session_id, []).extend([
                {
                    "role": "user",
                    "content": prompt,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant",
                    "content": answer,
                    "metadata": {"sources": sources},
                    "timestamp": datetime.now().isoformat()
                }
            ])

            st.session_state.thread_titles.setdefault(
                session_id,
                generate_thread_title(st.session_state.chat_threads[session_id])
            )

            st.session_state.current_session_id = session_id
            update_url_with_session(session_id)
            st.rerun()