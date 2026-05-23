import streamlit as st
import requests
import json
from datetime import datetime

# ─────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(
    page_title="EHTMS Admin Dashboard",
    page_icon="🏢",
    layout="wide"
)

# ─────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ─────────────────────────────────────
# AUTHENTICATION HELPERS
# ─────────────────────────────────────
def login(email: str, password: str):
    """Authenticate and store JWT token"""
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        st.session_state.token = data["access_token"]
        st.session_state.user_info = {"email": email}
        return True
    else:
        st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
        return False

def logout():
    """Clear session"""
    st.session_state.token = None
    st.session_state.user_info = None
    st.rerun()

def get_headers():
    """Return auth headers for API requests"""
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

# ─────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────
def login_page():
    """Login UI"""
    st.title("🏢 EHTMS Admin Dashboard")
    st.markdown("### Sign In")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email", placeholder="admin@ehtms.local")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if login(email, password):
                st.rerun()

def sidebar():
    """Navigation sidebar"""
    with st.sidebar:
        st.title(f"👤 {st.session_state.user_info.get('email', 'User')}")
        
        if st.button("Logout", use_container_width=True):
            logout()
        
        st.divider()
        menu = st.radio(
            "Navigation",
            ["📊 Dashboard", "🏢 Organizations", "👥 Users", "📋 Tasks"],
            index=0
        )
        return menu

# ─────────────────────────────────────
# PAGES
# ─────────────────────────────────────
def dashboard_page():
    """Overview dashboard"""
    st.title("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Organizations", "Loading...")
    with col2:
        st.metric("Total Users", "Loading...")
    with col3:
        st.metric("Active Tasks", "Loading...")
    with col4:
        st.metric("Completed Tasks", "Loading...")
    
    st.info("🚀 Dashboard statistics will be populated after API integration.")

def organizations_page():
    """Organization management (Super Admin only)"""
    st.title("🏢 Organizations")
    
    # Create new organization
    with st.expander("➕ Create New Organization"):
        org_name = st.text_input("Organization Name")
        if st.button("Create Organization"):
            if org_name:
                response = requests.post(
                    f"{API_BASE_URL}/org/org",
                    json={"name": org_name},
                    headers=get_headers()
                )
                if response.status_code == 201:
                    st.success(f"Organization '{org_name}' created!")
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    
    # List organizations (placeholder)
    st.subheader("Existing Organizations")
    st.write("Organizations will be listed here after API integration.")

def users_page():
    """User management"""
    st.title("👥 User Management")
    
    tab1, tab2 = st.tabs(["➕ Create User", "📋 User List"])
    
    with tab1:
        st.subheader("Create New User")
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email")
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["worker", "manager", "org_admin"])
        
        if st.button("Create User"):
            if email and username and password:
                # This would call your registration or admin user creation endpoint
                st.info("User creation endpoint integration pending.")
    
    with tab2:
        st.subheader("All Users")
        st.write("User list will be populated after API integration.")

def tasks_page():
    """Task management"""
    st.title("📋 Task Management")
    
    tab1, tab2 = st.tabs(["➕ Assign Task", "📋 Task List"])
    
    with tab1:
        st.subheader("Assign Task to Worker")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Task Title")
            assigned_to = st.text_input("Worker Email")
        with col2:
            description = st.text_area("Description")
            due_date = st.date_input("Due Date")
        
        if st.button("Assign Task"):
            if title and assigned_to:
                response = requests.post(
                    f"{API_BASE_URL}/tasks/assign",
                    json={
                        "title": title,
                        "description": description,
                        "assigned_to_email": assigned_to,
                        "due_date": due_date.isoformat() if due_date else None
                    },
                    headers=get_headers()
                )
                if response.status_code == 201:
                    st.success("Task assigned successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
    
    with tab2:
        st.subheader("All Tasks")
        st.write("Task list will be populated after API integration.")

# ─────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────
def main():
    if not st.session_state.token:
        login_page()
    else:
        menu = sidebar()
        
        if menu == "📊 Dashboard":
            dashboard_page()
        elif menu == "🏢 Organizations":
            organizations_page()
        elif menu == "👥 Users":
            users_page()
        elif menu == "📋 Tasks":
            tasks_page()

if __name__ == "__main__":
    main()