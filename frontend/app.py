# frontend/app.py
import streamlit as st
import requests

# Base URL pointing to our local FastAPI backend server
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Task Manager", layout="wide")

# --- Initialize Global Session Variables ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "view" not in st.session_state:
    st.session_state.view = "login"  # Options: 'login', 'register', 'dashboard'

# Helper function to generate standardized authorization header tokens
def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# --- 🔐 VIEW 1: USER LOGIN ---
if st.session_state.view == "login":
    st.title("🔑 Task Manager Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not username or not password:
                st.error("Please fill in all credentials.")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        # OAuth2 password request forms send data as form data, not raw JSON
                        response = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
                        if response.status_code == 200:
                            st.session_state.token = response.json().get("access_token")
                            st.session_state.username = username
                            st.session_state.view = "dashboard"
                            st.rerun()
                        else:
                            error_msg = response.json().get("detail", "Authentication failed.")
                            st.error(f"Error: {error_msg}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend server. Is it running?")

    st.write("New here?")
    if st.button("Create an account"):
        st.session_state.view = "register"
        st.rerun()


# --- 📝 VIEW 2: USER REGISTRATION ---
elif st.session_state.view == "register":
    st.title("📝 Create an Account")
    
    with st.form("register_form"):
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not new_username or not new_password:
                st.error("Please complete both fields.")
            else:
                with st.spinner("Registering user..."):
                    try:
                        response = requests.post(f"{API_URL}/register", json={"username": new_username, "password": new_password})
                        if response.status_code == 201:
                            st.success("Registration successful! Proceed to login.")
                            st.session_state.view = "login"
                            st.rerun()
                        else:
                            error_msg = response.json().get("detail", "Registration failed.")
                            st.error(f"Error: {error_msg}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend server.")

    if st.button("Back to Login"):
        st.session_state.view = "login"
        st.rerun()


# --- 📋 VIEW 3: KANBAN TASK BOARD DASHBOARD ---
elif st.session_state.view == "dashboard":
    # Header Row
    top_col1, top_col2 = st.columns([8, 2])
    with top_col1:
        st.title(f"📋 {st.session_state.username}'s Task Board")
    with top_col2:
        if st.button("Log Out", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.view = "login"
            st.rerun()

    st.divider()

    # --- Section: Task Creation Input Form ---
    with st.expander("➕ Create a New Task", expanded=False):
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Task Title")
            description = st.text_area("Task Description (Optional)")
            stage = st.selectbox("Initial Stage", ["Todo", "In Progress", "Done"])
            task_submitted = st.form_submit_button("Add Task")
            
            if task_submitted:
                if not title:
                    st.error("A task title is required.")
                else:
                    with st.spinner("Saving task..."):
                        res = requests.post(f"{API_URL}/tasks", json={"title": title, "description": description, "stage": stage}, headers=get_auth_headers())
                        if res.status_code == 201:
                            st.success("Task created!")
                            st.rerun()
                        else:
                            st.error("Failed to add task.")

    # --- Section: Fetch and Display Kanban Columns ---
    try:
        with st.spinner("Loading tasks..."):
            get_res = requests.get(f"{API_URL}/tasks", headers=get_auth_headers())
            
        if get_res.status_code == 200:
            all_tasks = get_res.json()
            
            # Map out 3 distinct columns matching the mandatory stages
            col_todo, col_progress, col_done = st.columns(3)
            
            stages_map = {
                "Todo": (col_todo, "🔴 To Do"),
                "In Progress": (col_progress, "🟡 In Progress"),
                "Done": (col_done, "🟢 Done")
            }
            
            # Render labels over our Kanban board partitions
            for stage_key, (col_obj, label) in stages_map.items():
                with col_obj:
                    st.markdown(f"### {label}")
                    st.divider()
                    
                    # Filter elements belonging strictly to this column loop
                    stage_tasks = [t for t in all_tasks if t["stage"] == stage_key]
                    
                    if not stage_tasks:
                        st.caption("No tasks in this stage.")
                        
                    for task in stage_tasks:
                        # Draw card design box
                        with st.container(border=True):
                            st.markdown(f"**{task['title']}**")
                            if task["description"]:
                                st.text(task["description"])
                            
                            # Interactive controls inside card structure
                            # Contextual state changes
                            current_index = ["Todo", "In Progress", "Done"].index(stage_key)
                            
                            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
                            
                            # Shift left execution control
                            with btn_col1:
                                if current_index > 0:
                                    if st.button("◀", key=f"left_{task['id']}", help="Move Left"):
                                        prev_stage = ["Todo", "In Progress", "Done"][current_index - 1]
                                        requests.put(f"{API_URL}/tasks/{task['id']}", json={"title": task["title"], "description": task["description"], "stage": prev_stage}, headers=get_auth_headers())
                                        st.rerun()
                            
                            # Remove execution control
                            with btn_col2:
                                if st.button("🗑️", key=f"del_{task['id']}", help="Delete Task"):
                                    requests.delete(f"{API_URL}/tasks/{task['id']}", headers=get_auth_headers())
                                    st.rerun()
                                    
                            # Shift right execution control
                            with btn_col3:
                                if current_index < 2:
                                    if st.button("▶", key=f"right_{task['id']}", help="Move Right"):
                                        next_stage = ["Todo", "In Progress", "Done"][current_index + 1]
                                        requests.put(f"{API_URL}/tasks/{task['id']}", json={"title": task["title"], "description": task["description"], "stage": next_stage}, headers=get_auth_headers())
                                        st.rerun()
        else:
            st.error("Failed to sync structural columns with backend servers.")
    except requests.exceptions.ConnectionError:
        st.error("Lost communication links with operational backends.")