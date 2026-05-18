import os
import joblib
from config.db_config import get_db_connection

# Paths to your pre-trained assets
TEXT_MODEL_PATH = "models/text_scam_detector.pkl"

def process_text(user_id, text):
    """Processes text using pre-trained intelligence with standard UI."""
    if not os.path.exists(TEXT_MODEL_PATH):
        return {"error": "AI Engine Offline. Please ensure models exist in the /models folder."}
    
    try:
        model = joblib.load(TEXT_MODEL_PATH)
        prediction = model.predict([text])[0]
        
        # 1 = Scam, 0 = Safe
        verdict = "SCAM" if prediction == 1 or str(prediction).lower() == "scam" else "SAFE"
        confidence = 95 
        
        save_to_db(user_id, "Text Query", confidence, verdict)
        return {"verdict": verdict, "confidence": confidence}
    except Exception as e:
        return {"error": f"Analysis Error: {str(e)}"}

def save_to_db(user_id, file_name, prob, verdict):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO scan_results (user_id, file_name, scam_probability, prediction) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, file_name, prob, verdict))
        conn.commit()
        conn.close()