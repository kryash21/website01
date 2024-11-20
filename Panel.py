import streamlit as st
import os
import json
from pathlib import Path
import hashlib
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Secure File Uploader",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Paths for saving user data and files
USER_DATA_FILE = "user_data.json"
BASE_UPLOAD_FOLDER = "user_files"
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

# Load user data
def load_user_data():
    if not Path(USER_DATA_FILE).exists():
        with open(USER_DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

# Save user data
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication system
def register_user(username, password):
    users = load_user_data()
    if username in users:
        return False, "Username already exists."
    users[username] = {"password": hash_password(password), "files": []}
    save_user_data(users)
    return True, "Registration successful! You can now log in."

def authenticate_user(username, password):
    users = load_user_data()
    if username in users and users[username]["password"] == hash_password(password):
        return True, "Login successful!"
    return False, "Invalid username or password."

# Upload functionality
def save_file(username, uploaded_file):
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, username)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path

# Animated message
def animated_message(message, duration=2):
    placeholder = st.empty()
    for i in range(duration * 10):  # Create a smooth animation effect
        placeholder.markdown(f"<h3 style='text-align:center;'>{message[:i % len(message)]}...</h3>", unsafe_allow_html=True)
        time.sleep(0.1)
    placeholder.empty()

# User interface
def login_page():
    st.title("🔐 Login")
    st.sidebar.success("Select an option above.")
    
    # Animation
    st.markdown("<h4 style='text-align:center;'>Welcome to Secure File Uploader</h4>", unsafe_allow_html=True)
    animated_message("🔒 Verifying Secure Environment", duration=2)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        success, message = authenticate_user(username, password)
        if success:
            st.session_state["username"] = username
            st.success(message)
            animated_message("🔓 Login Successful! Redirecting...", duration=2)
            # After login success, show the upload page or the user's file page
            st.experimental_user()  # Remove this line if you don't want to refresh the page
        else:
            st.error(message)

def register_page():
    st.title("📝 Register")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    if st.button("Register"):
        success, message = register_user(username, password)
        if success:
            st.success(message)
            st.info("Go to the Login page to access your account.")
        else:
            st.error(message)

def upload_page():
    username = st.session_state.get("username")
    st.title(f"📁 Welcome, {username}")
    st.write("Upload your files below:")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file:
        file_path = save_file(username, uploaded_file)
        users = load_user_data()
        users[username]["files"].append(uploaded_file.name)
        save_user_data(users)
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        st.info(f"Saved at: `{file_path}`")

        # Download link
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        st.download_button(
            label="📥 Download File",
            data=file_bytes,
            file_name=uploaded_file.name,
            mime="application/octet-stream",
        )

def user_files_page():
    username = st.session_state.get("username")
    st.title(f"📂 {username}'s Uploaded Files")
    users = load_user_data()
    files = users[username].get("files", [])
    if files:
        for file_name in files:
            file_path = os.path.join(BASE_UPLOAD_FOLDER, username, file_name)
            st.write(f"📄 {file_name}")
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            st.download_button(
                label="📥 Download",
                data=file_bytes,
                file_name=file_name,
                mime="application/octet-stream",
                key=file_name,
            )
    else:
        st.info("No files uploaded yet.")

# Main app logic
if "username" not in st.session_state:
    st.sidebar.title("Navigation")
    option = st.sidebar.radio("Choose an option:", ["Login", "Register"])
    if option == "Login":
        login_page()
    elif option == "Register":
        register_page()
else:
    st.sidebar.title("Navigation")
    option = st.sidebar.radio(
        "Choose an option:",
        ["Upload Files", "View My Files", "Logout"],
    )
    if option == "Upload Files":
        upload_page()
    elif option == "View My Files":
        user_files_page()
    elif option == "Logout":
        del st.session_state["username"]
        st.sidebar.info("You have logged out.")
        st.experimental_rerun()
