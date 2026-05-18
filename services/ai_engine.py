import librosa
import numpy as np
import spacy
import spacy.cli
import speech_recognition as sr
import os
import joblib
import streamlit as st
import soundfile as sf
import tempfile

# --- THE SCIPY BUG FIX ---
import scipy.signal
import scipy.signal.windows
if not hasattr(scipy.signal, 'hann'):
    scipy.signal.hann = scipy.signal.windows.hann

# Paths and Configuration
MODEL_PATH = "models/scam_detector.pkl"
TEXT_MODEL_PATH = "models/text_scam_detector.pkl"
VECTORIZER_PATH = "models/text_vectorizer.pkl"

SCAM_KEYWORDS = [
    "microsoft", "technical department", "windows support", "certified technician", "security checkup", "virus",
    "bank", "transfer", "account", "verify", "taxes", "fee", "payment", 
    "overdrawn", "transaction", "credit card", "underwriting", "interest rate", 
    "lower your rate", "debt", "loan", "irs", "lhdn", "customs", "fine", 
    "wire", "frozen", "balance", "routing number", "wire transfer", "insufficient funds",
    "unpaid", "invoice", "billing", "deduct", "deduction", "tax return", 
    "bank negara", "bnm", "kwsp", "epf", "zelle", "cashapp",
    "urgent", "police", "arrest", "suspend", "compromised", "warrant",
    "legal action", "final notice", "ignore", "immediate", "lawsuit", "jail",
    "court", "investigation", "penalty", "illegal", "pdrm", "bukit aman", 
    "maca", "sprm", "money laundering", "drugs", "contraband", "magistrate",
    "supreme court", "officer", "inspector", "detained", "warrant of arrest"
]

@st.cache_resource
def load_all_brains():
    try:
        nlp_model = spacy.load("en_core_web_sm")
    except OSError:
        spacy.cli.download("en_core_web_sm")
        nlp_model = spacy.load("en_core_web_sm")
    
    # LOAD THE REAL TRAINED MODELS
    acoustic_brain = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
    text_brain = joblib.load(TEXT_MODEL_PATH) if os.path.exists(TEXT_MODEL_PATH) else None
    vectorizer = joblib.load(VECTORIZER_PATH) if os.path.exists(VECTORIZER_PATH) else None
    
    return nlp_model, acoustic_brain, text_brain, vectorizer

def extract_acoustic_features_for_ml(file_path):
    """Extracts the exact 180 features needed for the Random Forest AI."""
    y, sr = librosa.load(file_path, duration=3, res_type='kaiser_fast')
    mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T, axis=0)
    return np.hstack([mfccs, chroma, mel])

def analyze_audio_file(file_path):
    """TRUE AI HYBRID LOGIC: Combines ML Acoustic predictions with ML NLP predictions."""
    results = {"status": "success", "transcript": "", "acoustic_features": {}, "scam_probability": 0.0, "verdict": "SAFE"}

    try:
        nlp, acoustic_model, text_model, vectorizer = load_all_brains()

        # ---------------------------------------------------------
        # 1. ACOUSTIC ANALYSIS (40% Weight)
        # ---------------------------------------------------------
        # A. UI Dashboard Metrics (BPM & Pitch)
        y, sr_rate = librosa.load(file_path, sr=16000)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr_rate)
        actual_bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr_rate)[0]
        average_pitch = float(np.mean(spectral_centroids))
        
        # B. TRUE MACHINE LEARNING SCORE
        acoustic_score = 15.0 # Fallback baseline
        if acoustic_model:
            # Extract the 180 features and ask the AI model for probability
            ml_features = extract_acoustic_features_for_ml(file_path)
            # predict_proba returns [Safe_Prob, Scam_Prob]. We want index 1 (* 100 for percentage)
            acoustic_score = acoustic_model.predict_proba([ml_features])[0][1] * 100.0
        else:
            # Fallback if model missing
            if 110 <= actual_bpm <= 145: acoustic_score += 45.0
            if np.std(spectral_centroids) < 900.0: acoustic_score += 40.0

        acoustic_score = min(100.0, acoustic_score)

        # ---------------------------------------------------------
        # 2. NLP ANALYSIS (60% Weight)
        # ---------------------------------------------------------
        transcript = "[Transcription Unavailable]"
        found_red_flags = []
        
        # Transcribe Audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            sf.write(tmp_wav.name, y, sr_rate)
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_wav.name) as source:
                audio_data = recognizer.record(source)
                try: transcript = recognizer.recognize_google(audio_data).lower()
                except: pass
        if os.path.exists(tmp_wav.name): os.remove(tmp_wav.name)

        # TRUE MACHINE LEARNING TEXT SCORE
        nlp_score = 0.0
        if transcript != "[Transcription Unavailable]":
            # Extract keywords for the UI dashboard display
            found_red_flags = [w for w in SCAM_KEYWORDS if w in transcript]
            
            if text_model and vectorizer:
                # Use the trained Naive Bayes AI to score the text
                vectorized_text = vectorizer.transform([transcript])
                nlp_score = text_model.predict_proba(vectorized_text)[0][1] * 100.0
            else:
                # Fallback if model missing
                nlp_score = min(100.0, len(set(found_red_flags)) * 20.0)

        # ---------------------------------------------------------
        # 3. APPLY 40/60 HYBRID FORMULA
        # ---------------------------------------------------------
        # Final Risk = (ML Acoustic * 0.4) + (ML NLP * 0.6)
        if transcript == "[Transcription Unavailable]":
            final_probability = acoustic_score # If no speaking, rely 100% on audio traits
        else:
            final_probability = (acoustic_score * 0.4) + (nlp_score * 0.6)

        results.update({
            "transcript": transcript,
            "scam_probability": round(final_probability, 2),
            "verdict": "SCAM" if final_probability >= 50.0 else "SAFE",
            "acoustic_features": {
                "average_pitch": round(average_pitch, 2),
                "speech_rate_bpm": round(actual_bpm, 1),
                "red_flags": found_red_flags
            }
        })
        return results

    except Exception as e:
        return {"status": "error", "error_message": str(e)}
def analyze_text_content(text):
    """TRUE AI LOGIC + HYBRID SAFETY NET for Scan Text Module."""
    nlp, acoustic_model, text_model, vectorizer = load_all_brains()
    
    # 1. Expanded Local & Financial Keywords
    high_risk = ["otp", "verify", "blocked", "login", "bank", "maybank", "account", "pdrn", "court", "transfer", "ringgit", "rm", "million", "prize", "fee", "pay", "winner", "tax"]
    urgency = ["immediately", "now", "urgent", "action", "24 hours", "penalty", "last notice", "need to"]
    
    # FIX: Use substring matching so "rm100000" triggers "rm" and "fees" triggers "fee"
    text_lower = text.lower()
    risk_matches = [w for w in high_risk if w in text_lower]
    urgency_matches = [w for w in urgency if w in text_lower]

    # 2. Calculate the "Safety Net" Keyword Score
    base_score = len(risk_matches) * 20.0
    multiplier = 1.4 if urgency_matches else 1.0
    keyword_score = min(99.9, base_score * multiplier)

    # 3. Apply the Hybrid Decision Engine
    if text_model and vectorizer:
        vectorized_text = vectorizer.transform([text])
        ml_score = text_model.predict_proba(vectorized_text)[0][1] * 100.0
        
        # HYBRID BRIDGE: Combine Machine Learning with the Keyword Safety Net
        final_score = max(ml_score, keyword_score * 0.75) 
    else:
        final_score = keyword_score
        
    final_score = min(99.9, final_score)

    return {
        "score": round(final_score, 2),
        "verdict": "SCAM" if final_score >= 50.0 else "SAFE",
        "risk_keywords": risk_matches,
        "urgency_flags": urgency_matches
    }