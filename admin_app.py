import streamlit as st
from views import login_page, admin_dashboard

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load CSS: {e}")

def render_logic():
    load_css("assets/admin_style.css")
    
    # Get the role or default to 'Admin' if missing/None
    role_info = st.session_state.get('admin_role')
    if not role_info:
        role_info = 'Admin'
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user'] = None

    if not st.session_state['logged_in']:
        # We pass is_admin_portal=True so the login page knows to show the Admin controls
        login_page.render(title=f"🏢 VR-SDS<br>{role_info} Portal", is_admin_portal=True)
    else:
        user = st.session_state['user']
        
        # --- STRICT SECURITY CHECKS ---
        
        # 1. Stop standard users completely
        if user['role'] == 'user':
            st.error("🚨 Access Denied: Admin account required.")
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.rerun()
                
        # 2. ALLOW System Administrators and handle mismatched session flags gracefully
        elif user['role'] == 'System Administrator':
            # Synchronize session state so the portal names look clean
            st.session_state['admin_role'] = 'System Administrator'
            
            if st.sidebar.button("Logout / Switch Portal"):
                st.session_state['logged_in'] = False
                st.session_state['portal'] = None
                st.session_state['admin_role'] = None
                st.rerun()
            admin_dashboard.render()

        # 3. Stop admins from logging into the WRONG admin portal
        elif user['role'] != role_info:
            st.error(f"🚨 Security Violation: Your account is registered as '{user['role']}'. You cannot access the '{role_info}' portal.")
            if st.button("Go Back / Switch Portal"):
                st.session_state['logged_in'] = False
                st.session_state['portal'] = None
                st.session_state['admin_role'] = None
                st.rerun()
                
        # 4. If any other admin role matches perfectly, let them in!
        else:
            if st.sidebar.button("Logout / Switch Portal"):
                st.session_state['logged_in'] = False
                st.session_state['portal'] = None
                st.session_state['admin_role'] = None
                st.rerun()
            admin_dashboard.render()

if __name__ == "__main__":
    st.set_page_config(page_title="VR-SDS Admin Portal", layout="wide")
    render_logic()