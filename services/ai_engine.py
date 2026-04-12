import librosa
import numpy as np
import spacy
import speech_recognition as sr
import os

# Load the NLP model for textual feature extraction
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Define High-Risk Scam Keywords
SCAM_KEYWORDS = [
    "urgent", "bank", "transfer", "police", "arrest", "suspend", 
    "password", "otp", "pin", "compromised", "account", "verify",
    "winner", "lottery", "fee", "taxes", "gift card", "crypto", "bitcoin"
]

def analyze_audio_file(file_path):
    """
    Core AI Engine: Fulfills Section 3.0 of the FYP Proposal.
    Extracts acoustic features and linguistic patterns to detect scams.
    """
    results = {
        "status": "success",
        "transcript": "",
        "acoustic_features": {},
        "nlp_features": {},
        "scam_probability": 0.0,
        "verdict": "SAFE"
    }
    
    try:
        # --- 1. ACOUSTIC FEATURE EXTRACTION (librosa) ---
        # Extracts voice tone, speech rate, and pitch variation
        y, sr_rate = librosa.load(file_path, sr=None)
        
        # Calculate Pitch (Spectral Centroid)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr_rate)[0]
        avg_pitch = float(np.mean(spectral_centroids))
        
        # Calculate Speech Rate (Tempo)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr_rate)
        avg_tempo = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
        
        results["acoustic_features"] = {
            "average_pitch": round(avg_pitch, 2),
            "speech_rate_bpm": round(avg_tempo, 2)
        }

        # --- 2. SPEECH-TO-TEXT ---
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            try:
                transcript = recognizer.recognize_google(audio_data).lower()
                results["transcript"] = transcript
            except sr.UnknownValueError:
                results["transcript"] = "[Could not understand audio]"
            except sr.RequestError:
                results["transcript"] = "[Offline - Cannot reach transcription service]"

        # --- 3. NLP FEATURE EXTRACTION (spaCy) ---
        doc = nlp(results["transcript"])
        
        found_keywords = []
        for token in doc:
            if token.lemma_.lower() in SCAM_KEYWORDS:
                found_keywords.append(token.lemma_.lower())
                
        # Remove duplicates
        found_keywords = list(set(found_keywords))
        results["nlp_features"]["flagged_keywords"] = found_keywords
        
        # --- 4. HYBRID SCORING ALGORITHM ---
        risk_score = 0.0
        
        # Textual Risk (Heavily weighted)
        if len(found_keywords) > 0:
            risk_score += (len(found_keywords) * 20.0) # 20% risk per keyword
            
        # Acoustic Risk (Scammers often speak fast and with raised pitch/stress)
        if avg_tempo > 130: 
            risk_score += 15.0
        if avg_pitch > 2000: 
            risk_score += 15.0
            
        # Cap the probability at 98.5% for realism
        final_probability = min(risk_score, 98.5)
        results["scam_probability"] = round(final_probability, 2)
        
        # Verdict Threshold
        if final_probability >= 50.0:
            results["verdict"] = "SCAM"
        else:
            results["verdict"] = "SAFE"
            
        return results

    except Exception as e:
        results["status"] = "error"
        results["error_message"] = str(e)
        return results