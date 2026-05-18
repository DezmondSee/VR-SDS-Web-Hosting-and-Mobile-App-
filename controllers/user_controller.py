from config.db_config import get_db_connection
import pandas as pd

def get_history(user_id):
    """Retrieves all previous scan results for the specific user."""
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    query = "SELECT scan_date, file_name, scam_probability, prediction FROM scan_results WHERE user_id = %s ORDER BY scan_date DESC"
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    return df

def add_trusted_contact(user_id, name, phone):
    """Adds a contact to the allowlist to prevent false positives."""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO trusted_contacts (user_id, contact_name, phone_number) VALUES (%s, %s, %s)", (user_id, name, phone))
        conn.commit()
        return True
    finally:
        conn.close()

def submit_report(user_id, phone, category, description):
    """Submits a manual scam report for Admin review."""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO scam_reports (user_id, reported_number, category, description) VALUES (%s, %s, %s, %s)", (user_id, phone, category, description))
        conn.commit()
        return True
    finally:
        conn.close()