import streamlit as st
import hashlib
from cryptography.fernet import Fernet
import json
import time
from datetime import datetime, timedelta

# Page metadata
st.set_page_config(
    page_title="SafeNote - Secure Data Manager",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_css():
    st.markdown("""
    <style>
        :root {
            --primary: #1e88e5;
            --primary-dark: #1565c0;
            --primary-light: #bbdefb;
            --secondary: #f5f5f5;
            --text: #212121;
            --text-light: #757575;
            --glass: rgba(255, 255, 255, 0.2);
        }
        
        body {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            color: var(--text);
        }
        
        .main {
            background-color: transparent !important;
        }
        
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select {
            border: 2px solid var(--primary) !important;
            border-radius: 10px !important;
            padding: 10px !important;
            background-color: white !important;
            color: var(--text) !important;
            box-shadow: 0 2px 10px rgba(30, 136, 229, 0.1);
        }
        
        .stButton>button {
            background-color: var(--primary) !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(30, 136, 229, 0.2) !important;
            width: 100% !important;
            margin: 5px 0 !important;
        }
        
        .stButton>button:hover {
            background-color: var(--primary-dark) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(30, 136, 229, 0.3) !important;
        }
        
        .stButton>button:focus {
            box-shadow: 0 0 0 0.2rem rgba(30, 136, 229, 0.5) !important;
        }
        
        /* Sidebar navigation buttons */
        .sidebar .stButton>button {
            margin: 8px 0 !important;
            text-align: left !important;
            padding-left: 20px !important;
        }
        
        /* Glass panel effect */
        .glass-panel {
            background: var(--glass) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
        }
        
        /* Heading with glass effect */
        .glass-heading {
            background: linear-gradient(90deg, rgba(30, 136, 229, 0.7), rgba(30, 136, 229, 0.4)) !important;
            backdrop-filter: blur(5px) !important;
            -webkit-backdrop-filter: blur(5px) !important;
            color: white !important;
            padding: 15px 20px !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1) !important;
            margin-bottom: 25px !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }
        
        .app-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #1e88e5, #0d47a1);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .app-subtitle {
            text-align: center;
            color: var(--primary-dark);
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        
        .success-box {
            padding: 15px;
            background-color: rgba(212, 237, 218, 0.8);
            color: #155724;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #28a745;
        }
        
        .error-box {
            padding: 15px;
            background-color: rgba(248, 215, 218, 0.8);
            color: #721c24;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #dc3545;
        }
        
        .user-badge {
            padding: 8px 15px;
            background-color: var(--primary-light);
            color: var(--primary-dark);
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            display: inline-block;
            margin-left: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        /* Fix for text visibility */
        .stTextArea textarea, 
        .stTextInput input {
            color: var(--text) !important;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-dark);
        }
        
        /* Remove Streamlit default styling */
        .st-emotion-cache-1y4p8pa {
            padding: 2rem 1.5rem;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
        }
        
        /* Hide the selectbox dropdown arrow */
        .stSelectbox>div>div>div>div>svg {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Generate or load encryption key
def get_key():
    if 'fernet_key' not in st.session_state:
        st.session_state.fernet_key = Fernet.generate_key()
    return st.session_state.fernet_key

KEY = get_key()
cipher = Fernet(KEY)

# Initialize session state
if 'user_db' not in st.session_state:
    st.session_state.user_db = {}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_name = ""
    st.session_state.current_page = "Home"

if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}
    
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0
    
if 'lockout_time' not in st.session_state:
    st.session_state.lockout_time = None

# Hash function
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text, passkey):
    encrypted_text = cipher.encrypt(text.encode()).decode()
    hashed_passkey = hash_passkey(passkey)
    return encrypted_text, hashed_passkey

def decrypt_data(encrypted_text, passkey):
    try:
        hashed_passkey = hash_passkey(passkey)
        
        if st.session_state.lockout_time and datetime.now() < st.session_state.lockout_time:
            remaining_time = (st.session_state.lockout_time - datetime.now()).seconds
            st.markdown(f'''
            <div class="error-box">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.5em;">🔒</span>
                    <div>
                        <strong>Account locked</strong><br>
                        Please try again in {remaining_time} seconds
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            return None
        
        for entry_id, entry_data in st.session_state.stored_data.items():
            if entry_data["encrypted_text"] == encrypted_text and entry_data["passkey"] == hashed_passkey:
                st.session_state.failed_attempts = 0
                return cipher.decrypt(encrypted_text.encode()).decode()
        
        st.session_state.failed_attempts += 1
        
        if st.session_state.failed_attempts >= 3:
            st.session_state.lockout_time = datetime.now() + timedelta(minutes=5)
            st.markdown('''
            <div class="error-box">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.5em;">⛔</span>
                    <div>
                        <strong>Too many failed attempts!</strong><br>
                        Your account has been locked for 5 minutes.
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.session_state.failed_attempts = 0
            time.sleep(1)
            st.rerun()
        else:
            attempts_left = 3 - st.session_state.failed_attempts
            st.markdown(f'''
            <div class="error-box">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.5em;">🔐</span>
                    <div>
                        <strong>Incorrect passkey!</strong><br>
                        You have {attempts_left} attempt{'s' if attempts_left > 1 else ''} remaining.
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        return None
    except Exception as e:
        st.markdown(f'''
        <div class="error-box">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5em;">⚠️</span>
                <div>
                    <strong>Decryption failed!</strong><br>
                    The data could not be decrypted. Please check your passkey.
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        return None

def save_data():
    with open('encrypted_data.json', 'w') as f:
        json.dump(st.session_state.stored_data, f)

def load_data():
    try:
        with open('encrypted_data.json', 'r') as f:
            st.session_state.stored_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        st.session_state.stored_data = {}

load_data()

# Login Page
def login_page():
    st.markdown("""
    <div class='app-title'>SafeNote</div>
    <div class='app-subtitle'>Your personal encryption vault</div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.container():
            st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
            
            st.markdown("<h2 style='text-align: center; color: var(--primary-dark);'>Login</h2>", unsafe_allow_html=True)
            
            if st.session_state.lockout_time and datetime.now() < st.session_state.lockout_time:
                remaining_time = (st.session_state.lockout_time - datetime.now()).seconds
                st.markdown(f'''
                <div class="error-box">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:1.5em;">🔒</span>
                        <div>
                            <strong>Account locked</strong><br>
                            Please try again in {remaining_time} seconds
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.session_state.lockout_time = None
                
                username = st.text_input("Username:", key="login_username")
                login_pass = st.text_input("Password:", type="password", key="login_pass")
                
                if st.button("Login", key="login_btn"):
                    if username in st.session_state.user_db:
                        hashed_input = hash_passkey(login_pass)
                        if st.session_state.user_db[username]["password"] == hashed_input:
                            st.session_state.authenticated = True
                            st.session_state.current_user = username
                            st.session_state.user_name = st.session_state.user_db[username]["name"]
                            st.session_state.failed_attempts = 0
                            st.session_state.lockout_time = None
                            st.session_state.current_page = "Home"
                            st.markdown('<div class="success-box">✅ Login successful! Redirecting...</div>', unsafe_allow_html=True)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.session_state.failed_attempts += 1
                            st.markdown('''
                            <div class="error-box">
                                <div style="display:flex; align-items:center; gap:10px;">
                                    <span style="font-size:1.5em;">❌</span>
                                    <div>
                                        <strong>Incorrect password!</strong><br>
                                        Please try again
                                    </div>
                                </div>
                            </div>
                            ''', unsafe_allow_html=True)
                    else:
                        st.markdown('''
                        <div class="error-box">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="font-size:1.5em;">🔍</span>
                                <div>
                                    <strong>User not found!</strong><br>
                                    Please register first
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    if st.session_state.failed_attempts >= 3:
                        st.session_state.lockout_time = datetime.now() + timedelta(minutes=5)
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        with st.container():
            st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: var(--primary-dark);'>Register</h2>", unsafe_allow_html=True)
            
            reg_username = st.text_input("Choose Username:", key="reg_username")
            reg_name = st.text_input("Your Name:", key="reg_name")
            reg_pass = st.text_input("Choose Password:", type="password", key="reg_pass")
            reg_confirm_pass = st.text_input("Confirm Password:", type="password", key="reg_confirm_pass")
            
            if st.button("Register", key="reg_btn"):
                if not reg_username or not reg_pass or not reg_confirm_pass:
                    st.markdown('''
                    <div class="error-box">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.5em;">⚠️</span>
                            <div>
                                <strong>All fields are required!</strong><br>
                                Please fill in all registration fields
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                elif reg_pass != reg_confirm_pass:
                    st.markdown('''
                    <div class="error-box">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.5em;">🔑</span>
                            <div>
                                <strong>Passwords don't match!</strong><br>
                                Please make sure both passwords are identical
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                elif reg_username in st.session_state.user_db:
                    st.markdown('''
                    <div class="error-box">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.5em;">🚫</span>
                            <div>
                                <strong>Username already exists!</strong><br>
                                Please choose a different username
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.session_state.user_db[reg_username] = {
                        "name": reg_name,
                        "password": hash_passkey(reg_pass)
                    }
                    st.markdown('''
                    <div class="success-box">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.5em;">✅</span>
                            <div>
                                <strong>Registration successful!</strong><br>
                                You can now login with your credentials
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# Sidebar navigation
def sidebar_nav():
    st.sidebar.markdown(f"""
    <div style='display: flex; align-items: center; margin-bottom: 30px;'>
        <h2 style='color: var(--primary-dark);'>Welcome</h2>
        <div class='user-badge'>{st.session_state.user_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    menu_options = {
        "Home": "🏠",
        "Store Data": "📥", 
        "Retrieve Data": "📤",
        "Logout": "🚪"
    }
    
    for page, icon in menu_options.items():
        if st.sidebar.button(f"{icon} {page}", key=f"nav_{page}"):
            st.session_state.current_page = page
            if page == "Logout":
                st.session_state.authenticated = False
                st.session_state.current_user = None
            st.rerun()
    
    # Highlight current page button
    st.markdown(f"""
    <style>
        [data-testid="stButton"][key="nav_{st.session_state.current_page}"] > button {{
            background-color: var(--primary-dark) !important;
            box-shadow: 0 0 0 2px white, 0 0 0 4px var(--primary) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# Home Page
def home_page():
    st.markdown("<h1 class='glass-heading'>🏠 SafeNote Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='glass-panel'>
        <h3 style='color: var(--primary-dark);'>Welcome back, {st.session_state.user_name}!</h3>
        <p>Your personal encryption vault for securely storing sensitive data with military-grade protection.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>AES-256 encryption</li>
            <li>SHA-256 password hashing</li>
            <li>Brute-force protection</li>
            <li>Secure data storage</li>
            <li>User-friendly interface</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='glass-panel'>
        <p><b>Storage Status:</b> {len(st.session_state.stored_data)} encrypted entries</p>
        <p><b>Last Login:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

# Store Data Page
def store_data_page():
    st.markdown("<h1 class='glass-heading'>📥 Store New Secret</h1>", unsafe_allow_html=True)
    
    with st.form("store_form"):
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        user_data = st.text_area("Data to Encrypt:", height=150, value="Type your secret here...")
        passkey = st.text_input("Encryption Passkey:", type="password", value="mypassword")
        confirm_passkey = st.text_input("Confirm Passkey:", type="password", value="mypassword")
        
        if st.form_submit_button("Encrypt & Store"):
            if not user_data or not passkey:
                st.markdown('''
                <div class="error-box">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:1.5em;">⚠️</span>
                        <div>
                            <strong>Both fields are required!</strong><br>
                            Please enter data and a passkey
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            elif passkey != confirm_passkey:
                st.markdown('''
                <div class="error-box">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:1.5em;">🔑</span>
                        <div>
                            <strong>Passkeys don't match!</strong><br>
                            Please make sure both passkeys are identical
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                encrypted_text, hashed_passkey = encrypt_data(user_data, passkey)
                entry_id = f"{st.session_state.current_user}_{len(st.session_state.stored_data) + 1}"
                
                st.session_state.stored_data[entry_id] = {
                    "encrypted_text": encrypted_text,
                    "passkey": hashed_passkey,
                    "timestamp": str(datetime.now()),
                    "owner": st.session_state.current_user
                }
                
                save_data()
                st.markdown(f'''
                <div class="success-box">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:1.5em;">✅</span>
                        <div>
                            <strong>Data stored securely!</strong><br>
                            <small>Entry ID: {entry_id}</small>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Retrieve Data Page
def retrieve_data_page():
    st.markdown("<h1 class='glass-heading'>📤 Retrieve Your Secrets</h1>", unsafe_allow_html=True)
    
    # Only show entries belonging to current user
    user_entries = {
        k: v for k, v in st.session_state.stored_data.items() 
        if v.get("owner") == st.session_state.current_user
    }
    entry_ids = list(user_entries.keys())
    
    with st.container():
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        selected_id = st.selectbox("Select Entry:", [""] + entry_ids)
        
        if selected_id:
            encrypted_text = st.session_state.stored_data[selected_id]["encrypted_text"]
            st.text_area("Encrypted Data:", value=encrypted_text, disabled=True)
            
            with st.form("retrieve_form"):
                passkey = st.text_input("Enter Passkey:", type="password", key="retrieve_passkey", value="mypassword")
                
                if st.form_submit_button("Decrypt"):
                    decrypted_text = decrypt_data(encrypted_text, passkey)
                    
                    if decrypted_text:
                        st.markdown(f'''
                        <div class="success-box">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span style="font-size:1.5em;">✅</span>
                                <div>
                                    <strong>Decryption successful!</strong>
                                    <div style='margin-top: 10px; padding: 10px; background-color: rgba(232, 244, 248, 0.8); border-radius: 5px; color: black;'>
                                        {decrypted_text}
                                    </div>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Main App
def main_app():
    sidebar_nav()
    
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Store Data":
        store_data_page()
    elif st.session_state.current_page == "Retrieve Data":
        retrieve_data_page()

# App flow control
if not st.session_state.authenticated:
    login_page()
else:
    main_app()