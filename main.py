import streamlit as st

def main():
    st.set_page_config(page_title="VR-SDS Multi-Portal", layout="centered")

    # Initialize portal session state
    if 'portal' not in st.session_state:
        st.session_state['portal'] = None

    # --- STEP 1: PORTAL SELECTION ---
    if st.session_state['portal'] is None:
        st.title("🛡️ VR-SDS Scam Detection System")
        st.subheader("Select Access Portal")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📱 User Portal", use_container_width=True):
                st.session_state['portal'] = 'user'
                st.rerun()
        with c2:
            if st.button("🔑 Admin Portal", use_container_width=True):
                st.session_state['portal'] = 'admin'
                st.rerun()

    # --- STEP 2: LAUNCH PORTAL LOGIC ---
    else:
        if st.session_state['portal'] == 'admin':
            import admin_app
            admin_app.render_logic()
        else:
            import user_app
            user_app.render_logic()

        # --- UPDATED: SIDEBAR ONLY SHOWS AFTER LOGIN ---
        if st.session_state.get('logged_in'):
            st.sidebar.divider()
            if st.sidebar.button("🔄 Switch Portal / Logout", use_container_width=True):
                # Clear all session data to return to the start
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()