import streamlit as st
from views import login_page, user_dashboard

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        pass

def render_logic():
    load_css("assets/user_style.css")
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user'] = None

    if not st.session_state['logged_in']:
        login_page.render(title="📱 VR-SDS<br>Scanner", is_admin_portal=False)
    else:
        user = st.session_state['user']
        if user['role'] != 'user':
            st.error("🚨 Admins must use the Web Portal. This interface is for standard users.")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()
        else:
            if st.sidebar.button("🚪 Logout"):
                st.session_state.clear()
                st.rerun()
            user_dashboard.render(user)

if __name__ == "__main__":
    st.set_page_config(page_title="VR-SDS Mobile App", layout="centered")
    render_logic()