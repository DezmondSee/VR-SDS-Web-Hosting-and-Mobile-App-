import streamlit as st
from views import login_page, admin_dashboard

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        pass

def render_logic():
    load_css("assets/admin_style.css")
    
    role_info = st.session_state.get('admin_role', 'Admin')
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user'] = None

    if not st.session_state['logged_in']:
        login_page.render(title=f"🏢 VR-SDS<br>{role_info} Portal", is_admin_portal=True)
    else:
        user = st.session_state['user']
        
        # Stop standard users completely
        if user['role'] == 'user':
            st.error("🚨 Access Denied: Admin account required.")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()
                
        # ALLOW System Administrators
        elif user['role'] in ['System Administrator', 'Security Analyst', 'Research Lead']:
            st.session_state['admin_role'] = user['role']
            if st.sidebar.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()
            admin_dashboard.render()

        else:
            st.error(f"🚨 Security Violation: Unrecognized role '{user['role']}'.")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="VR-SDS Admin Portal", layout="wide")
    render_logic()