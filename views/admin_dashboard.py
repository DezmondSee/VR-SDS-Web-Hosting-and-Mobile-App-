import streamlit as st
import os
from controllers import admin_controller, training_controller

def render():
    st.sidebar.title("🛡️ Admin Console")
    page = st.sidebar.radio("Navigation", ["📊 Dashboard & Analytics", "👥 User Database", "🤖 Train AI Model"])

    if page == "📊 Dashboard & Analytics":
        st.title("System Analytics")
        stats = admin_controller.get_system_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("Registered Users", stats['users'])
        c2.metric("Scams Blocked", stats['scams'])
        c3.metric("Pending Reports", stats['reports'])
        st.subheader("Scam Trends")
        chart_data = admin_controller.get_scam_trend_data()
        if not chart_data.empty: st.line_chart(data=chart_data, x='date', y='scams_detected')
        else: st.info("No scan data yet.")

    elif page == "👥 User Database":
        st.title("User Management")
        st.dataframe(admin_controller.get_all_users(), hide_index=True)
        with st.form("ban_form"):
            uid = st.number_input("Enter User ID to Ban", min_value=1)
            if st.form_submit_button("Ban User"):
                if admin_controller.ban_user(uid): st.success(f"✅ Banned ID {uid}")
                else: st.error("❌ Failed to ban (User may be an Admin).")

    elif page == "🤖 Train AI Model":
        st.markdown("<h1 style='color: #000000; font-weight: bold;'>AI Training Engine</h1>", unsafe_allow_html=True)
        
        model_type = st.selectbox("Model to Train", ["Text Analysis (SMS/Spam)", "Audio Analysis (Deepfake/Voice)"])
        
        st.write("")
        st.markdown("#### Upload Dataset (.csv)")
        
        # The help text appears when hovering over the question mark
        uploaded = st.file_uploader(
            "Drag and drop file here", 
            type=['csv'],
            help="The system now supports large datasets up to 5GB for high-fidelity training."
        )
        
        # This matches the screenshot's style but with the 5GB limit
        st.caption("Limit 5GB per file • CSV")

        if uploaded and st.button("🚀 Start Training", type="primary", use_container_width=True):
            with st.spinner(f"Processing massive dataset for {model_type}..."):
                os.makedirs("dataset", exist_ok=True)
                path = os.path.join("dataset", uploaded.name)
                with open(path, "wb") as f: 
                    f.write(uploaded.getbuffer())
                
                success, msg = training_controller.train_model(model_type, path)
                
                if success: 
                    st.success(f"✅ {msg}")
                else: 
                    st.error(f"❌ {msg}")
                
                # Cleanup to save local disk space
                if os.path.exists(path):
                    os.remove(path)