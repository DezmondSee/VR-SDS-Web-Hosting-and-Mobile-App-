import streamlit as st
from services.auth_service import login_user, register_user, get_security_question

def load_css(file_name):
    """Loads the CSS file and injects it into the Streamlit app to apply the Glassmorphism design."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load CSS: {e}")

# THE FIX: Added 'is_admin_portal' flag (defaults to False for normal users)
def render(title="📱 VR-SDS<br>Scanner", is_admin_portal=False):
    # --- 1. INJECT THE CUSTOM CSS ---
    load_css("assets/user_style.css")

    # --- 2. RENDER THE DYNAMIC MAIN TITLE ---
    st.markdown(
        f"<h1 style='text-align: center; color: #000000; font-weight: 900; margin-bottom: 20px;'>{title}</h1>", 
        unsafe_allow_html=True
    )

    # --- 3. TABS ---
    tab1, tab2, tab3 = st.tabs(["Sign In", "Register", "Forgot Password"])

    # --- SIGN IN TAB ---
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if u and p:
                user = login_user(u, p)
                if user == "BANNED":
                    st.error("🚫 This account has been deactivated. Please contact the Administrator.")
                elif user:
                    st.session_state['user'] = user
                    st.session_state['logged_in'] = True
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials. Please try again.")
            else:
                st.warning("⚠️ Please enter both username and password.")

    # --- REGISTER TAB ---
    with tab2:
        st.markdown("<h3 style='color: #000000; font-weight: bold;'>Create New Account</h3>", unsafe_allow_html=True)
        
        nu = st.text_input("New Username", help="Choose a unique username")
        ne = st.text_input("Email Address")
        np = st.text_input("New Password", type="password")
        
        # --- THE SEPARATION LOGIC ---
        if is_admin_portal:
            # Only show this if they are on the Admin App
            selected_role = st.selectbox("Admin Account Type", [
                "System Administrator", 
                "Security Analyst", 
                "Research Lead"
            ])
            st.info("🛡️ Admin registration requires an authorization code.")
            admin_auth_code = st.text_input("Admin Authorization Code", type="password")
        else:
            # If they are on the User App, hardcode to 'user' and hide the inputs completely
            selected_role = "user"
            admin_auth_code = None
        # ----------------------------
        
        sec_q = st.selectbox("Security Question", [
            "What was the name of your first pet?", 
            "What is your mother's maiden name?",
            "What was the name of your primary school?"
        ])
        
        sec_a = st.text_input("Security Answer")
        
        if st.button("Register", use_container_width=True):
            if nu and np and ne and sec_a:
                # Check admin passcode ONLY if they are trying to register on the Admin portal
                if is_admin_portal and admin_auth_code != "VRSDS-2026":
                    st.error("❌ Invalid Admin Authorization Code. Registration blocked.")
                else:
                    if register_user(nu, np, ne, sec_q, sec_a, selected_role):
                        if selected_role == "user":
                            st.success("✅ Registration Successful! You can now Sign In.")
                        else:
                            st.success(f"✅ {selected_role} Registration Successful! You can now Sign In.")
                    else:
                        st.error("❌ Registration failed. Username or Email might already be taken.")
            else:
                st.warning("⚠️ All fields are required for registration.")

    # --- FORGOT PASSWORD TAB ---
    with tab3:
        st.markdown("<h3 style='color: #000000; font-weight: bold;'>Reset Password</h3>", unsafe_allow_html=True)
        
        forgot_u = st.text_input("Enter Username to reset")
        if forgot_u:
            q = get_security_question(forgot_u)
            if q:
                st.info(f"Question: {q}")
                ans = st.text_input("Your Answer", key="reset_ans")
                new_p = st.text_input("New Password", type="password", key="reset_new_p")
                
                if st.button("Reset Password", use_container_width=True):
                    st.info("Reset logic pending service integration.")
            else:
                st.error("User not found.")