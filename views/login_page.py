import streamlit as st
from services.auth_service import login_user, register_user, get_security_question, reset_password

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        pass 

def render(title="📱 VR-SDS<br>Scanner", is_admin_portal=False):
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarNav"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    load_css("assets/user_style.css")

    st.markdown(
        f"<h1 style='text-align: center; color: #000000; font-weight: 900; margin-bottom: 20px;'>{title}</h1>", 
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["Sign In", "Register", "Forgot Password"])

    # --- SIGN IN TAB ---
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if u and p:
                user = login_user(u, p)
                if user == "BANNED":
                    st.error("🚫 Account deactivated. Contact Administrator.")
                elif user:
                    st.session_state['user'] = user
                    st.session_state['logged_in'] = True
                    st.success(f"Welcome, {user['username']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials.")
            else:
                st.warning("⚠️ Enter both username and password.")

    # --- REGISTER TAB ---
    with tab2:
        st.markdown("<h3 style='color: #000000; font-weight: bold;'>Create New Account</h3>", unsafe_allow_html=True)
        nu = st.text_input("New Username")
        ne = st.text_input("Email Address")
        np = st.text_input("New Password", type="password")
        
        if is_admin_portal:
            selected_role = st.selectbox("Admin Account Type", ["System Administrator", "Security Analyst", "Research Lead"])
            admin_auth_code = st.text_input("Admin Authorization Code", type="password")
        else:
            selected_role = "user"
            admin_auth_code = None
        
        sec_q = st.selectbox("Security Question", ["What was the name of your first pet?", "Mother's maiden name?", "Primary school name?"])
        sec_a = st.text_input("Security Answer")
        
        if st.button("Register", use_container_width=True):
            if nu and np and ne and sec_a:
                if is_admin_portal and admin_auth_code != "VRSDS-2026":
                    st.error("❌ Invalid Admin Code.")
                else:
                    if register_user(nu, np, ne, sec_q, sec_a, selected_role):
                        st.success(f"✅ {selected_role} Registration Successful! Please Sign In.")
                    else:
                        st.error("❌ Registration failed. Username may already exist.")
            else:
                st.warning("⚠️ All fields required.")

    # --- FORGOT PASSWORD TAB ---
    with tab3:
        st.markdown("<h3 style='color: #000000; font-weight: bold;'>Reset Password</h3>", unsafe_allow_html=True)
        forgot_u = st.text_input("Enter Username to find your account")
        
        if forgot_u:
            q = get_security_question(forgot_u)
            if q:
                st.info(f"**Security Question:** {q}")
                ans = st.text_input("Your Answer", key="reset_ans")
                new_p = st.text_input("Enter New Password", type="password", key="reset_p")
                
                if st.button("Reset Password", use_container_width=True):
                    if ans and new_p:
                        if reset_password(forgot_u, ans, new_p):
                            st.success("✅ Password reset successfully! You can now sign in.")
                        else:
                            st.error("❌ Incorrect security answer.")
                    else:
                        st.warning("⚠️ Please provide both your answer and a new password.")
            elif forgot_u.strip() != "":
                st.error("User not found in database.")