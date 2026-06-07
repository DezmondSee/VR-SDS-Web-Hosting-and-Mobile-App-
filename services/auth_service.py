from config.db_config import get_db_connection
import streamlit as st

def login_user(username, password):
    """
    Direct string comparison for testing. 
    Matches 'admin123' from schema.sql exactly.
    """
    conn = get_db_connection()
    if not conn: 
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # .strip() removes hidden spaces that cause "Invalid Credentials"
        u_input = str(username).strip()
        p_input = str(password).strip()
        
        # Look for the user in the database
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (u_input,))
        user = cursor.fetchone()
        
        if user:
            # Direct check against the password_hash column
            db_pass = str(user['password_hash']).strip()
            
            if p_input == db_pass:
                if not user.get('is_active', True): 
                    return "BANNED"
                return user
                
        return None
    except Exception as e:
        st.error(f"Login Error: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def register_user(username, password, email, sec_question, sec_answer, role="user"):
    """Registers users without encryption for easy testing."""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users 
            (username, password_hash, email, security_question, security_answer, is_active, role) 
            VALUES (%s, %s, %s, %s, %s, 1, %s)
        """, (username.strip(), password.strip(), email.strip(), sec_question, sec_answer.lower().strip(), role))
        conn.commit()
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"REAL DATABASE ERROR: {e}")
        return False
    finally: 
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_security_question(username):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT security_question FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user['security_question'] if user else None

def reset_password(username, sec_answer, new_password):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash=%s WHERE username=%s AND security_answer=%s", 
                   (new_password.strip(), username.strip(), sec_answer.lower().strip()))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success