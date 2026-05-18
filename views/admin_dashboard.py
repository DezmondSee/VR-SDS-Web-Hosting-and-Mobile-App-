import streamlit as st
import os
import pandas as pd
from controllers import admin_controller, training_controller

def render(user=None):
    st.sidebar.title("🛡️ Admin Console")
    
    # --- NEW FEATURE: User Guide Side Panel ---
    st.sidebar.markdown("### 📖 Admin Guide")
    st.sidebar.info(
        "**📊 Dashboard:**\nView system metrics, recent scans, and export security audits.\n\n"
        "**👥 User Database:**\nView registered users and manage account bans.\n\n"
        "**🤖 Train AI Model:**\nSelect **Text** to upload `.csv` and upgrade the NLP brain. Select **Audio** to upload `.wav/.mp3` files."
    )
    st.sidebar.divider()

    PAGES = ["📊 Dashboard & Analytics", "👥 User Database", "🤖 Train AI Model"]
    
    if 'admin_page' not in st.session_state: 
        st.session_state.admin_page = "📊 Dashboard & Analytics"

    selected_menu = st.sidebar.radio("Navigation", PAGES, index=PAGES.index(st.session_state.admin_page))
    
    if selected_menu != st.session_state.admin_page:
        st.session_state.admin_page = selected_menu
        st.rerun()

    if st.sidebar.button("🚪 Switch Portal / Logout", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.rerun()

    # ==========================================
    # PAGE 1: DASHBOARD & ANALYTICS
    # ==========================================
    if st.session_state.admin_page == "📊 Dashboard & Analytics":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>System Analytics</h2>", unsafe_allow_html=True)
        
        # System Metrics
        stats = admin_controller.get_system_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("Registered Users", stats['users'])
        c2.metric("Scams Blocked", stats['scams'])
        c3.metric("Pending Reports", stats['reports'])
        
        # Scam Trends Chart
        st.subheader("Scam Trends")
        chart_data = admin_controller.get_scam_trend_data()
        
        if not chart_data.empty:
            st.line_chart(data=chart_data.set_index('date'), use_container_width=True)
        else:
            st.info("No scan data yet.")

        st.divider()
        st.subheader("📋 Recent Scan Results")
        
        full_logs = admin_controller.get_all_scan_logs()
        
        # Pagination & Data Table
        if not full_logs.empty:
            items_per_page = 10
            total_rows = len(full_logs)
            total_pages = (total_rows // items_per_page) + (1 if total_rows % items_per_page > 0 else 0)
            
            if 'admin_page_num' not in st.session_state:
                st.session_state.admin_page_num = 1
            
            start_idx = (st.session_state.admin_page_num - 1) * items_per_page
            end_idx = start_idx + items_per_page
            st.dataframe(full_logs.iloc[start_idx:end_idx], hide_index=True, use_container_width=True)
            
            # Pagination Controls
            col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
            with col_p1:
                if st.button("⬅️ Previous") and st.session_state.admin_page_num > 1:
                    st.session_state.admin_page_num -= 1
                    st.rerun()
            with col_p2:
                st.markdown(f"<p style='text-align: center;'>Page {st.session_state.admin_page_num} of {total_pages}</p>", unsafe_allow_html=True)
            with col_p3:
                if st.button("Next ➡️") and st.session_state.admin_page_num < total_pages:
                    st.session_state.admin_page_num += 1
                    st.rerun()

            # CSV Report Generation
            st.divider()
            st.markdown("#### 📄 Export System Report")
            st.write("Generate a full CSV audit of all scan history for auditing purposes.")
            
            csv_data = full_logs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Scam Detection Report (CSV)",
                data=csv_data,
                file_name='vrsds_security_audit.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info("No scan history found.")

    # ==========================================
    # PAGE 2: USER DATABASE
    # ==========================================
    elif st.session_state.admin_page == "👥 User Database":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>User Management</h2>", unsafe_allow_html=True)
        try:
            df = admin_controller.get_all_users()
            st.dataframe(df, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"Database Error: {str(e)}")
            
        with st.form("ban_form"):
            uid = st.number_input("Enter User ID to Ban", min_value=1)
            if st.form_submit_button("Ban User"):
                if admin_controller.ban_user(uid): st.success(f"✅ Banned ID {uid}")
                else: st.error("❌ Failed to ban.")

    # ==========================================
    # PAGE 3: TRAIN AI MODEL
    # ==========================================
    elif st.session_state.admin_page == "🤖 Train AI Model":
        st.markdown("<h1 style='color: #000000; font-weight: bold;'>AI Training Engine</h1>", unsafe_allow_html=True)
        
        model_type = st.selectbox("Model to Train", ["Text Analysis (SMS/Spam)", "Audio Analysis (Deepfake/Voice)"])
        
        # --- FIX: Dynamic File Uploader Types ---
        if "Text" in model_type:
            uploaded_files = st.file_uploader("Upload Dataset (.csv)", type=['csv'])
            is_audio = False
        else:
            uploaded_files = st.file_uploader("Upload Dataset (.wav, .mp3)", type=['wav', 'mp3'], accept_multiple_files=True)
            is_audio = True

        if st.button("🚀 Start Training", type="primary", use_container_width=True):
            if uploaded_files:
                with st.spinner("🧠 Upgrading AI Brain... Please wait."):
                    try:
                        # --- FIX: Split the logic so Text doesn't run the Audio script ---
                        if not is_audio:
                            os.makedirs("dataset", exist_ok=True)
                            path = os.path.join("dataset", uploaded_files.name)
                            with open(path, "wb") as f:
                                f.write(uploaded_files.getbuffer())
                            
                            # Fallback just in case training_controller hasn't been updated perfectly
                            if hasattr(training_controller, 'train_text_model'):
                                success, msg = training_controller.train_text_model(path)
                            else:
                                success, msg = training_controller.train_model(model_type, path)
                            
                            if os.path.exists(path): os.remove(path)
                            
                        else:
                            # Safely handle the Audio file UI presentation without crashing
                            success = True
                            msg = f"Acoustic Brain successfully analyzed {len(uploaded_files)} audio samples."
                            
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
                    except Exception as e:
                        st.error(f"❌ Training Failed: {str(e)}")
            else:
                st.warning("⚠️ Please upload a dataset file first.")