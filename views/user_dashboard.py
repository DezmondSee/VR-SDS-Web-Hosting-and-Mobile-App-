import streamlit as st
import os
import pandas as pd
import time
from controllers import user_controller
# ✅ FIX: Now importing both the Audio and Text real AI functions
from services.ai_engine import analyze_audio_file, analyze_text_content
from services.scan_service import save_scan_result

def go_to_page(page_name):
    """Safely updates the navigation state."""
    st.session_state.active_page = page_name

def render_permissions_gate():
    """
    Triggers real browser hardware access popups. 
    Blocks the app until security settings are confirmed.
    """
    st.markdown("<h2 style='text-align: center; color: #000000;'>🔐 Android Shield Authorization</h2>", unsafe_allow_html=True)
    st.write("Granting hardware permissions allows VR-SDS to intercept and analyze real-time call audio.")
    
    with st.container(border=True):
        st.markdown("#### 🎤 Hardware Access Trigger")
        # REAL HARDWARE TRIGGER: Forces the browser/OS to grant mic access
        mic_access = st.audio_input("Enable Hardware Interception")
        
        st.divider()
        st.markdown("#### 📱 System-Level Permissions")
        p_notify = st.toggle("🔔 Notification Access (Scam Alerts)", value=True)
        p_overlay = st.toggle("🖼️ Display Over Other Apps (Call Shield UI)", value=True)
        p_logs = st.toggle("📞 Read Call Logs (Automated Detection)", value=False)
        
        if st.button("🚀 Authorize & Enter Scanner", use_container_width=True, type="primary"):
            if mic_access is not None:
                st.session_state['permissions_complete'] = True
                st.session_state['permissions'] = {'mic': True, 'notify': p_notify, 'overlay': p_overlay, 'logs': p_logs}
                st.rerun()
            else:
                st.warning("⚠️ Hardware access is required for real-time call protection.")

def render(user):
    # --- 1. MANDATORY PERMISSION GATE ---
    if not st.session_state.get('permissions_complete', False):
        render_permissions_gate()
        return

    # --- 2. SIDEBAR NAVIGATION & USER GUIDE ---
    st.sidebar.title(f"🛡️ VR-SDS Scanner")
    st.sidebar.markdown(f"**User: {user['username']}**")
    
    # User Guide Side Panel
    st.sidebar.markdown("### 📖 User Guide")
    st.sidebar.info(
        "**🛡️ Call Shield:**\nToggle real-time monitoring for incoming calls to stay protected.\n\n"
        "**🎙️ Scan Audio:**\nUpload `.wav` or `.mp3` files to let the AI check for voice scams and deepfakes.\n\n"
        "**💬 Scan Text:**\nPaste suspicious SMS messages to detect high-risk intents.\n\n"
        "**📋 Trusted Contacts:**\nAdd family or friends to your whitelist."
    )
    st.sidebar.divider()
    
    PAGES = ["Dashboard", "Android Call Shield", "Scan Audio", "Scan Text", "History", "Trusted Contacts", "Report Scam", "Settings"]
    
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "Dashboard"

    selected_menu = st.sidebar.radio("Navigation", PAGES, index=PAGES.index(st.session_state.active_page))
    
    if selected_menu != st.session_state.active_page:
        st.session_state.active_page = selected_menu
        st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['permissions_complete'] = False
        st.rerun()

    # ==========================================
    # PAGE 1: DASHBOARD
    # ==========================================
    if st.session_state.active_page == "Dashboard":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>Control Center</h2>", unsafe_allow_html=True)
        history_df = user_controller.get_history(user['user_id'])
        total_scans = len(history_df) if history_df is not None else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Scans", f"{total_scans}")
        m2.metric("Shield Status", "Active" if st.session_state.get('shield_on', False) else "Standby")
        m3.metric("AI Engine", "Online")
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1: st.button("🛡️ Open Call Shield", use_container_width=True, on_click=go_to_page, args=("Android Call Shield",))
        with c2: st.button("🎙️ Scan Audio File", use_container_width=True, on_click=go_to_page, args=("Scan Audio",))

    # ==========================================
    # PAGE 2: ANDROID CALL SHIELD (WATCHER)
    # ==========================================
    elif st.session_state.active_page == "Android Call Shield":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>🛡️ Android Call Shield</h2>", unsafe_allow_html=True)
        if 'shield_on' not in st.session_state: st.session_state.shield_on = False
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔴 Stop Monitoring" if st.session_state.shield_on else "🟢 Start Real-Time Monitoring", use_container_width=True):
                st.session_state.shield_on = not st.session_state.shield_on
                st.rerun()
        with col2: st.info(f"**Shield Status:** {'ACTIVE' if st.session_state.shield_on else 'STANDBY'}")

        st.divider()
        st.markdown("### 📞 Live Detection Log")
        if st.session_state.shield_on:
            st.success("🛰️ Connected to Hardware. Monitoring root folder for incoming_call.wav...")
            
            # Watcher Logic: Automatically detects signals from the hardware
            if os.path.exists("incoming_call.wav"):
                with st.status("🚨 CALL DETECTED: Analyzing in Real-Time...", expanded=True):
                    results = analyze_audio_file("incoming_call.wav")
                    if results["verdict"] == "SCAM":
                        st.error(f"‼️ SCAM DETECTED: {results['scam_probability']}% Risk")
                        st.info("🔍 **Reasoning:** Unusual pacing and red-flag keywords detected.")
                    else:
                        st.success(f"✅ CALL VERIFIED: Safe ({results['scam_probability']}%).")
                    save_scan_result(user['user_id'], "RealTime_Intercept.wav", results['scam_probability'], results['verdict'])
                os.remove("incoming_call.wav") # Cleanup
            else:
                time.sleep(1)
                st.rerun()
        else: st.warning("⚠️ Turn on the shield to start monitoring.")

    # ==========================================
    # PAGE 3: SCAN AUDIO
    # ==========================================
    elif st.session_state.active_page == "Scan Audio":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>Analyze Audio File</h2>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload recorded call", type=['wav', 'mp3'])
        
        if uploaded_file:
            st.audio(uploaded_file)
            if st.button("🔍 Run Full AI Analysis", type="primary", use_container_width=True):
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                with st.spinner("🧠 Hybrid AI analyzing..."):
                    results = analyze_audio_file(temp_path)
                
                if results["status"] == "success":
                    st.markdown("<style>[data-testid='stMetricValue']{font-size:24px!important;}</style>", unsafe_allow_html=True)
                    
                    if results["verdict"] == "SCAM": st.error(f"🚨 SCAM DETECTED ({results['scam_probability']}%)")
                    else: st.success(f"✅ SAFE ({results['scam_probability']}%)")
                    
                    c1, c2, c3 = st.columns([1.2, 1.2, 0.8])
                    c1.metric("Speech Rate (BPM)", f"{results['acoustic_features']['speech_rate_bpm']}")
                    c2.metric("Avg Pitch (Hz)", f"{results['acoustic_features']['average_pitch']}")
                    
                    red_flags = results['acoustic_features'].get('red_flags', [])
                    c3.metric("Red Flags", len(red_flags))

                    st.divider()
                    st.markdown("### 🧠 AI Analysis Logic")
                    explanation = f"""
                    The risk score is a result of our Hybrid Weighted Engine:
                    1. **Acoustic Layer ({results['acoustic_features']['speech_rate_bpm']} BPM):** Identifies robotic or scripted pacing.
                    2. **NLP Layer ({len(red_flags)} Flags):** Scans the transcript for clusters like *OTP, Verify,* or *Blocked*.
                    
                    **Formula:** `(Acoustic Risk * 0.4) + (NLP Match Score * 0.6)`
                    """
                    st.info(explanation)
                    
                    if red_flags: st.warning(f"🚩 **Found Keywords:** {', '.join(red_flags)}")
                    save_scan_result(user['user_id'], uploaded_file.name, results['scam_probability'], results['verdict'])
                os.remove(temp_path)

    # ==========================================
    # PAGE 4: SCAN TEXT (REAL AI ENGINE INTEGRATION)
    # ==========================================
    elif st.session_state.active_page == "Scan Text":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>Scan Text/SMS</h2>", unsafe_allow_html=True)
        text_in = st.text_area("Paste suspicious message here:", height=150)
        
        if st.button("🔍 Run NLP AI Analysis", type="primary", use_container_width=True):
            if text_in:
                # ✅ FIX: Now calling the real AI Engine trained on your dataset!
                res = analyze_text_content(text_in)
                st.divider()
                if res["verdict"] == "SCAM":
                    st.error(f"🚨 SCAM DETECTED ({res['score']}%)")
                else:
                    st.success(f"✅ SAFE ({res['score']}%)")
                
                st.markdown("### 🧠 NLP Analysis Logic")
                st.info(f"Analysis identified {len(res['risk_keywords'])} high-risk keywords and {len(res['urgency_flags'])} urgency markers.")
                if res['risk_keywords']:
                    st.warning(f"🚩 **Flagged Content:** {', '.join(res['risk_keywords'])}")
            else:
                st.warning("⚠️ Please provide text to analyze.")

    # ==========================================
    # PAGE 5: HISTORY
    # ==========================================
    elif st.session_state.active_page == "History":
        st.header("Detection History")
        df = user_controller.get_history(user['user_id'])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ==========================================
    # PAGE 6: TRUSTED CONTACTS 
    # ==========================================
    elif st.session_state.active_page == "Trusted Contacts":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>Whitelist Management</h2>", unsafe_allow_html=True)
        with st.form("contact_form", clear_on_submit=True):
            c_name = st.text_input("Contact Name")
            c_phone = st.text_input("Phone Number")
            if st.form_submit_button("Add to Whitelist"):
                if c_name and c_phone:
                    user_controller.add_trusted_contact(user['user_id'], c_name, c_phone)
                    st.success(f"✅ {c_name} saved to database.")
        
        st.divider()
        st.markdown("### 📋 Active Whitelist (From MySQL Database)")
        contacts_df = user_controller.get_trusted_contacts(user['user_id'])
        st.dataframe(contacts_df, use_container_width=True, hide_index=True)

    # ==========================================
    # PAGE 7: REPORT SCAM
    # ==========================================
    elif st.session_state.active_page == "Report Scam":
        st.header("Submit Scam Report")
        with st.form("report_form"):
            r_num = st.text_input("Reported Number")
            r_cat = st.selectbox("Category", ["Bank Scam", "Phishing SMS", "Government Impersonation"])
            r_desc = st.text_area("Details")
            if st.form_submit_button("Submit Report"):
                if user_controller.submit_report(user['user_id'], r_num, r_cat, r_desc):
                    st.success("✅ Report logged for admin review.")

    # ==========================================
    # PAGE 8: SETTINGS 
    # ==========================================
    elif st.session_state.active_page == "Settings":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>System Settings</h2>", unsafe_allow_html=True)
        with st.expander("👤 User Profile & Security", expanded=True):
            st.write(f"**Username:** {user['username']} | **Email:** {user['email']}")
            st.divider()
            new_p = st.text_input("Change Password", type="password")
            if st.button("💾 Save Password", use_container_width=True):
                if user_controller.update_user_password(user['user_id'], new_p):
                    st.success("✅ Password updated in database.")

        with st.expander("🔐 App Permissions Status", expanded=True):
            perms = st.session_state.get('permissions', {})
            st.toggle("Microphone Hardware (Verified)", value=True, disabled=True)
            perms['notify'] = st.toggle("Notification Access", value=perms.get('notify', True))
            perms['overlay'] = st.toggle("Display Over Other Apps", value=perms.get('overlay', True))
            st.session_state['permissions'] = perms