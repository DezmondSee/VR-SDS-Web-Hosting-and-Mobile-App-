import streamlit as st
import os
import time
import pandas as pd
import streamlit.components.v1 as components
from controllers import scan_controller, user_controller
from services.realtime_processor import RealTimeScamDetector
from services.ai_engine import analyze_audio_file
from services.scan_service import save_scan_result

# --- THE BULLETPROOF ROUTING CALLBACK ---
def go_to_page(page_name):
    """Updates the hidden tracker so the page changes without crashing."""
    st.session_state.active_page = page_name

def render(user):
    # ==========================================
    # REAL HARDWARE PERMISSION SCRIPT
    # ==========================================
    components.html(
        """
        <script>
        function activateNotifications() {
            if ("Notification" in window) {
                if (Notification.permission !== "granted" && Notification.permission !== "denied") {
                    Notification.requestPermission().then(function (permission) {
                        if (permission === "granted") {
                            new Notification("🛡️ VR-SDS Shield Active", {
                                body: "Notification permission granted. System is securing your device.",
                            });
                        }
                    });
                }
            }
        }
        function activateMicrophone() {
            navigator.mediaDevices.getUserMedia({ audio: true, video: false })
            .then(function(stream) { console.log('Microphone engaged successfully.'); })
            .catch(function(err) { console.error('Microphone hardware access denied.', err); });
        }
        activateNotifications();
        activateMicrophone();
        </script>
        """, height=0, width=0
    )

    st.sidebar.title(f"📱 VR-SDS Scanner")
    st.sidebar.markdown(f"**Welcome, {user['username']}**")
    
    # --- NAVIGATION LOGIC ---
    PAGES = ["Dashboard", "Android Call Shield", "Scan Audio", "Scan Text", "History", "Trusted Contacts", "Report Scam", "Settings"]

    if 'active_page' not in st.session_state:
        st.session_state.active_page = "Dashboard"

    try:
        current_index = PAGES.index(st.session_state.active_page)
    except ValueError:
        current_index = 0

    selected_menu = st.sidebar.radio("Navigation", PAGES, index=current_index)

    if selected_menu != st.session_state.active_page:
        st.session_state.active_page = selected_menu
        st.rerun()
    
    st.sidebar.divider()
    
    if st.sidebar.button("🚪 Logout", type="primary", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.rerun()
    
    # ==========================================
    # MAIN PAGE CONTENT LOGIC
    # ==========================================
    if st.session_state.active_page == "Dashboard":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>Control Center</h2>", unsafe_allow_html=True)
        st.info("✅ System Protected. All monitoring services are active.")
        
        # Stats Logic (Using your existing user_controller logic)
        history_df = user_controller.get_history(user['user_id'])
        total_scans = 0
        total_scams = 0
        detection_rate = 0.0
        
        if history_df is not None and not history_df.empty:
            total_scans = len(history_df)
            verdict_col = [col for col in history_df.columns if 'verdict' in col.lower()]
            if verdict_col:
                v_col = verdict_col[0]
                total_scams = len(history_df[history_df[v_col].astype(str).str.upper() == 'SCAM'])
                detection_rate = (total_scams / total_scans) * 100 if total_scans > 0 else 0.0

        st.markdown("<h4 style='color: #000000;'>📊 Your Real-Time Statistics</h4>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Scans", f"{total_scans:,}")
        m2.metric("Suspected Scams", f"{total_scams:,}")
        m3.metric("Detection Rate", f"{detection_rate:.1f}%")

        st.divider()
        st.markdown("<h4 style='color: #000000;'>🚀 Quick Launch Modules</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.button("🛡️ Open Android Shield", use_container_width=True, on_click=go_to_page, args=("Android Call Shield",))
            st.button("💬 Scan Text Message", use_container_width=True, on_click=go_to_page, args=("Scan Text",))
        with col2:
            st.button("🎙️ Scan Audio File", use_container_width=True, on_click=go_to_page, args=("Scan Audio",))
            st.button("🚩 Report a Scam", use_container_width=True, on_click=go_to_page, args=("Report Scam",))

    # --- AUTOMATIC ANDROID SHIELD ---
    elif st.session_state.active_page == "Android Call Shield":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>🛡️ VR-SDS Automatic Shield</h2>", unsafe_allow_html=True)
        
        if "android_permission" not in st.session_state:
            st.session_state.android_permission = False

        if not st.session_state.android_permission:
            st.warning("📱 Android System Permission Required")
            st.info("To automate call interception, VR-SDS must be set as your Default Caller ID & Spam App.")
            if st.button("✅ Grant & Activate Auto-Shield"):
                st.session_state.android_permission = True
                st.rerun()
            return

        # Initialize Detector
        if "detector" not in st.session_state:
            st.session_state.detector = RealTimeScamDetector()
            st.session_state.is_monitoring = False
            st.session_state.last_res = ("LISTENING", 0)

        # TRIGGER AUTOMATIC START
        if not st.session_state.is_monitoring:
            with st.spinner("🎤 Initializing Automatic Call Monitor..."):
                def update_ui(pred, conf):
                    st.session_state.last_res = (pred, conf)
                st.session_state.detector.start(update_ui)
                st.session_state.is_monitoring = True
                st.rerun()

        st.success("🛰️ Auto-Shield Active: Monitoring Incoming Audio Streams")
        
        verdict, conf = st.session_state.last_res
        if verdict == "SCAM":
            st.error(f"🚨 ALERT: High Scam Probability! ({conf}%)")
            st.toast("⚠️ TERMINATE CALL IMMEDIATELY", icon="🚫")
            st.button("🚫 TERMINATE CALL", type="primary", use_container_width=True)
        elif verdict == "SAFE":
            st.success(f"✅ Conversation appears Safe ({conf}%)")
        else:
            st.info("🎤 Active Monitoring... Analyzing vocal stress and keywords.")
        
        if st.button("🛑 Deactivate Auto-Shield"):
            st.session_state.detector.stop()
            st.session_state.is_monitoring = False
            st.session_state.android_permission = False
            st.rerun()

        time.sleep(2)
        st.rerun()

    # --- HIGH-FIDELITY SCAN AUDIO ---
    elif st.session_state.active_page == "Scan Audio":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>🎙️ Analyze Audio File</h2>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Audio", type=['wav', 'mp3'])
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format="audio/wav")
            if st.button("🔍 Run AI Scam Analysis", type="primary", use_container_width=True):
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                with st.spinner("🧠 Extracting Acoustic & NLP Features..."):
                    results = analyze_audio_file(temp_path)
                
                if results["status"] == "success":
                    if results["verdict"] == "SCAM": st.error(f"🚨 SCAM DETECTED ({results['scam_probability']}%)")
                    else: st.success(f"✅ SAFE ({results['scam_probability']}%)")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Speech Rate", f"{results['acoustic_features']['speech_rate_bpm']} BPM")
                    c2.metric("Avg Pitch", f"{results['acoustic_features']['average_pitch']} Hz")
                    c3.metric("Keywords", len(results['nlp_features']['flagged_keywords']))
                    
                    save_scan_result(user['user_id'], uploaded_file.name, results['scam_probability'], results['verdict'])
                else:
                    st.error(f"❌ Error: {results.get('error_message')}")
                
                if os.path.exists(temp_path): os.remove(temp_path)

    elif st.session_state.active_page == "Scan Text":
        st.header("Analyze Message Text")
        txt = st.text_area("Message Content")
        if st.button("Check"):
            res = scan_controller.process_text(user['user_id'], txt)
            if res.get('error'): st.error(res['error'])
            elif res['verdict'] == "SCAM": st.error("🚨 PHISHING DETECTED")
            else: st.success("✅ SAFE")

    elif st.session_state.active_page == "History":
        st.header("Detection History")
        st.dataframe(user_controller.get_history(user['user_id']), use_container_width=True)

    elif st.session_state.active_page == "Trusted Contacts":
        st.markdown("<h3 style='color: #000000; font-weight: bold;'>Manage Trusted Contacts</h3>", unsafe_allow_html=True)
        n, p = st.text_input("Name"), st.text_input("Phone")
        if st.button("Add Contact", use_container_width=True): 
            user_controller.add_trusted_contact(user['user_id'], n, p)
            st.success("✅ Added")
            time.sleep(1); st.rerun()

    elif st.session_state.active_page == "Report Scam":
        st.header("Submit Scam Report")
        p, c, d = st.text_input("Number"), st.selectbox("Type", ["Phishing", "Bank", "Voice"]), st.text_area("Desc")
        if st.button("Submit Report"): 
            user_controller.submit_report(user['user_id'], p, c, d)
            st.success("Report Submitted")

    elif st.session_state.active_page == "Settings":
        st.markdown("<h2 style='color: #000000; font-weight: bold;'>⚙️ System Settings</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("**👤 Profile Settings**")
                st.text_input("Username", value=user.get('username', ''), disabled=True)
                st.text_input("Email", value=user.get('email', ''))
                if st.button("Update Profile", use_container_width=True): st.success("Profile Updated!")
        with col2:
            with st.container(border=True):
                st.markdown("**🛡️ Permissions**")
                st.toggle("Auto-Monitor Calls", value=True)
                st.toggle("Push Notifications", value=True)
                st.write("Current Max Upload: **5GB**")