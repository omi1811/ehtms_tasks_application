#GENERATED CODE - NOT MINE XD
import streamlit as st
import requests
from datetime import datetime, timedelta
import os

# 🌐 API Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(page_title="EHTMS Dashboard", layout="wide")
st.title("️ EHTMS Task Command Center")

# 🔐 Auth State
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# 🔹 Helper: Auth Headers
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

# 🔹 Login/Register Tab
if not st.session_state.token:
    tab1, tab2 = st.tabs(["🔑 Login", " Register"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.session_state.user = email
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Login failed"))
            except Exception as e:
                st.error(f"API Error: {e}")

    with tab2:
        r_email = st.text_input("Email", key="reg_email")
        r_user = st.text_input("Username", key="reg_user")
        r_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            try:
                res = requests.post(f"{API_URL}/auth/register", json={"email": r_email, "username": r_user, "password": r_pass})
                if res.status_code == 201:
                    st.success("Registered! Switch to Login tab.")
                else:
                    st.error(res.json().get("detail", "Registration failed"))
            except Exception as e:
                st.error(f"API Error: {e}")

else:
    #  Authenticated Dashboard
    col1, col2 = st.columns([4, 1])
    with col1: st.subheader(f"Welcome, {st.session_state.user}")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

    tabs = st.tabs(["📋 Tasks", " Calendar", "📊 Stats", "️ Memory", "📤 Upload & Complete"])

    with tabs[0]:  # 📋 Tasks
        status_filter = st.selectbox("Filter by Status", ["all", "pending", "in_progress", "complete", "archived"])
        if st.button(" Refresh Tasks"):
            try:
                params = {"status_filter": status_filter} if status_filter != "all" else {}
                res = requests.get(f"{API_URL}/tasks", headers=auth_headers(), params=params)
                if res.status_code == 200:
                    tasks = res.json()
                    for t in tasks:
                        st.markdown(f"**{t['title']}** | `{t['status']}` | Due: `{t.get('due_date','N/A')}` | ID: `{t['id']}`")
                else:
                    st.error("Failed to fetch tasks")
            except Exception as e:
                st.error(f"API Error: {e}")
        
        with st.expander("➕ Create New Task"):
            t_title = st.text_input("Title")
            t_desc = st.text_area("Description")
            t_due = st.date_input("Due Date", datetime.now() + timedelta(days=7))
            if st.button("Create Task"):
                try:
                    res = requests.post(f"{API_URL}/tasks", headers=auth_headers(), 
                                        json={"title": t_title, "description": t_desc, "due_date": t_due.isoformat()})
                    if res.status_code == 201:
                        st.success("Task created!")
                    else:
                        st.error(res.json().get("detail", "Create failed"))
                except Exception as e:
                    st.error(f"API Error: {e}")

    with tabs[1]:  # 📅 Calendar
        col_a, col_b = st.columns(2)
        start_d = col_a.date_input("Start Date", datetime.now())
        end_d = col_b.date_input("End Date", datetime.now() + timedelta(days=30))
        if st.button("📅 Load Calendar View"):
            try:
                params = {"start_date": start_d.strftime("%d-%m-%Y"), "end_date": end_d.strftime("%d-%m-%Y")}
                res = requests.get(f"{API_URL}/tasks/calendar", headers=auth_headers(), params=params)
                if res.status_code == 200:
                    for t in res.json():
                        st.markdown(f" **{t['title']}** | Due: `{t['due_date'][:10]}` | Status: `{t['status']}`")
                else:
                    st.error("Failed to load calendar")
            except Exception as e:
                st.error(f"API Error: {e}")

    with tabs[2]:  # 📊 Stats
        if st.button("📊 Load Monthly Stats"):
            try:
                res = requests.get(f"{API_URL}/tasks/stats", headers=auth_headers())
                if res.status_code == 200:
                    s = res.json()
                    st.metric("Total Tasks", s["total"])
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Pending", s["pending"])
                    c2.metric("In Progress", s["in_progress"])
                    c3.metric("Complete", s["complete"])
                    c4.metric("Archived", s["archived"])
                else:
                    st.error("Failed to load stats")
            except Exception as e:
                st.error(f"API Error: {e}")

    with tabs[3]:  # 🗄️ Memory
        if st.button("🗄️ Load Memory/Archive"):
            try:
                res = requests.get(f"{API_URL}/tasks/memory", headers=auth_headers())
                if res.status_code == 200:
                    for t in res.json():
                        st.markdown(f"✅ **{t['title']}** | Completed: `{t.get('completed_at','N/A')[:10]}` | Status: `{t['status']}`")
                else:
                    st.error("Failed to load memory")
            except Exception as e:
                st.error(f"API Error: {e}")

    with tabs[4]:  # 📤 Upload & Complete
        task_id = st.number_input("Task ID to Complete", min_value=1, step=1)
        uploaded = st.file_uploader("Upload Proof Photo", type=["jpg", "png", "webp"])
        if st.button("📤 Upload & Complete"):
            if uploaded and task_id:
                try:
                    # 1. Upload
                    files = {"file": (uploaded.name, uploaded, uploaded.type)}
                    res_up = requests.post(f"{API_URL}/upload", headers=auth_headers(), files=files)
                    if res_up.status_code == 201:
                        file_url = res_up.json()["file_url"]
                        # 2. Complete
                        res_comp = requests.patch(f"{API_URL}/tasks/{task_id}/complete", headers=auth_headers(), 
                                                  json={"image_url": file_url})
                        if res_comp.status_code == 200:
                            st.success("Task completed & proof attached!")
                        else:
                            st.error(res_comp.json().get("detail", "Complete failed"))
                    else:
                        st.error(res_up.json().get("detail", "Upload failed"))
                except Exception as e:
                    st.error(f"API Error: {e}")
            else:
                st.warning("Enter Task ID and select a photo.")