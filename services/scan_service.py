from config.db_config import get_db_connection
import streamlit as st

def save_scan_result(user_id, file_name, scam_probability, prediction):
    """Saves the AI scan result into the MySQL database."""
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO scan_results (user_id, file_name, scam_probability, prediction) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, file_name, float(scam_probability), prediction))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"🚨 Database Error saving result: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()