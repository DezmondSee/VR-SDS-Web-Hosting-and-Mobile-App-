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

# We keep this as a fallback just in case the AI models are ever deleted or offline
SCAM_KEYWORDS_FALLBACK = [
    "microsoft", "bank", "transfer", "account", "verify", "taxes", "fee", "payment", 
    "urgent", "police", "arrest", "suspend", "compromised", "warrant", "otp"
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

def extract_model_keywords(text, model, vectorizer, top_n=5):
    """
    EXPLAINABLE AI: Asks the trained model which specific words in the text
    triggered the highest scam probability based on its mathematical weights.
    """
    try:
        # 1. Transform the text to find which words the model actually recognizes
        vec = vectorizer.transform([text.lower()])
        feature_names = vectorizer.get_feature_names_out()
        
        # 2. Get the index numbers of the words that exist in this specific text
        present_indices = vec.nonzero()[1]
        if len(present_indices) == 0: return []
            
        # 3. Extract the mathematical weights depending on the model type (Naive Bayes, LogReg, or RandomForest)
        weights = None
        if hasattr(model, 'coef_'): # Logistic Regression / SVM
            weights = model.coef_[0] 
        elif hasattr(model, 'feature_log_prob_'): # Naive Bayes
            weights = model.feature_log_prob_[1] 
        elif hasattr(model, 'feature_importances_'): # Random Forest
            weights = model.feature_importances_
            
        if weights is not None:
            # Pair the words found in the text with their scam severity weight
            word_scores = [(feature_names[i], weights[i]) for i in present_indices]
            # Sort them so the most severe words are at the top
            word_scores.sort(key=lambda x: x[1], reverse=True)
            # Return the actual words
            return [word for word, score in word_scores[:top_n]]
        else:
            # Fallback if model doesn't expose weights: return recognized words longer than 3 letters
            words = [feature_names[i] for i in present_indices]
            return [w for w in words if len(w) > 3][:top_n]
            
    except Exception as e:
        print(f"Keyword extraction error: {e}")
        return []

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
        y, sr_rate = librosa.load(file_path, sr=16000)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr_rate)
        actual_bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr_rate)[0]
        average_pitch = float(np.mean(spectral_centroids))
        
        acoustic_score = 15.0 
        if acoustic_model:
            ml_features = extract_acoustic_features_for_ml(file_path)
            acoustic_score = acoustic_model.predict_proba([ml_features])[0][1] * 100.0
        else:
            if 110 <= actual_bpm <= 145: acoustic_score += 45.0
            if np.std(spectral_centroids) < 900.0: acoustic_score += 40.0

        acoustic_score = min(100.0, acoustic_score)

        # ---------------------------------------------------------
        # 2. NLP ANALYSIS (60% Weight)
        # ---------------------------------------------------------
        transcript = "[Transcription Unavailable]"
        found_red_flags = []
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            sf.write(tmp_wav.name, y, sr_rate)
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_wav.name) as source:
                audio_data = recognizer.record(source)
                try: transcript = recognizer.recognize_google(audio_data).lower()
                except: pass
        if os.path.exists(tmp_wav.name): os.remove(tmp_wav.name)

        nlp_score = 0.0
        if transcript != "[Transcription Unavailable]":
            if text_model and vectorizer:
                vectorized_text = vectorizer.transform([transcript])
                nlp_score = text_model.predict_proba(vectorized_text)[0][1] * 100.0
                
                # 🚀 NEW: Dynamically pull the exact words the AI model flagged!
                found_red_flags = extract_model_keywords(transcript, text_model, vectorizer)
            else:
                found_red_flags = [w for w in SCAM_KEYWORDS_FALLBACK if w in transcript]
                nlp_score = min(100.0, len(set(found_red_flags)) * 20.0)

        # ---------------------------------------------------------
        # 3. APPLY 40/60 HYBRID FORMULA
        # ---------------------------------------------------------
        if transcript == "[Transcription Unavailable]":
            final_probability = acoustic_score 
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
    """TRUE AI LOGIC using Dynamic Model Extraction."""
    nlp, acoustic_model, text_model, vectorizer = load_all_brains()
    
    if text_model and vectorizer:
        vectorized_text = vectorizer.transform([text])
        final_score = text_model.predict_proba(vectorized_text)[0][1] * 100.0
        
        # 🚀 NEW: Dynamically pull the exact words the AI model flagged!
        risk_matches = extract_model_keywords(text, text_model, vectorizer, top_n=6)
    else:
        text_lower = text.lower()
        risk_matches = [w for w in SCAM_KEYWORDS_FALLBACK if w in text_lower]
        final_score = min(99.9, len(risk_matches) * 20.0)

    return {
        "score": round(final_score, 2),
        "verdict": "SCAM" if final_score >= 50.0 else "SAFE",
        "risk_keywords": risk_matches,
        "urgency_flags": [] # Can be removed from UI if desired
    }