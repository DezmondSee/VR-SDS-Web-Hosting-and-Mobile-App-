import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

MODEL_DIR = "models"

def train_model(model_type, dataset_path):
    """Trains or updates AI models and persists them to the models/ folder."""
    try:
        os.makedirs(MODEL_DIR, exist_ok=True)
        # Determine file name based on model type selected in Admin Console
        filename = "text_scam_detector.pkl" if "Text" in model_type else "scam_detector.pkl"
        save_path = os.path.join(MODEL_DIR, filename)
        
        # Placeholder for actual training logic using dataset_path
        # In practice, you would load your .npy files here
        X = np.random.rand(100, 10) 
        y = np.random.randint(0, 2, 100)
        
        clf = RandomForestClassifier()
        clf.fit(X, y)
        
        # Save the "brain" to the models directory
        joblib.dump(clf, save_path)
        
        return True, f"Model successfully saved to {save_path}"
    except Exception as e:
        return False, f"Training failed: {str(e)}"