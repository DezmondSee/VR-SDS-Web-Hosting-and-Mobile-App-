from config.db_config import get_db_connection
import pandas as pd

def get_system_stats():
    """Fetches real-time counts for the Admin Dashboard."""
    conn = get_db_connection()
    stats = {'users': 0, 'scams': 0, 'reports': 0}
    if not conn: return stats
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scan_results WHERE prediction = 'SCAM'")
        stats['scams'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scam_reports")
        stats['reports'] = cursor.fetchone()[0]
    finally:
        conn.close()
    return stats

def get_all_users():
    """Retrieves user database excluding sensitive password data."""
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    df = pd.read_sql("SELECT user_id, username, email, role, is_active FROM users", conn)
    conn.close()
    return df

def ban_user(user_id):
    """Deactivates a user account (Prevents banning Admins)."""
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 0 WHERE user_id = %s AND role != 'System Administrator'", (user_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def get_scam_trend_data():
    """Aggregates scam detections by date for the line chart."""
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    query = """
        SELECT DATE(scan_date) as date, COUNT(*) as scams_detected 
        FROM scan_results 
        WHERE prediction = 'SCAM' 
        GROUP BY DATE(scan_date)
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df