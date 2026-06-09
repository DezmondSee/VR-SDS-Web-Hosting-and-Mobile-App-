import mysql.connector
import os
from dotenv import load_dotenv

# This tells Python to open your .env file and load the variables!
load_dotenv()

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="vr-sds-dezmondsee0-7d7b.e.aivencloud.com",
            port=19711,
            user="avnadmin",
            password=os.getenv("AIVEN_PASSWORD"),
            database="defaultdb"
        )
        return conn
    except Exception as e:
        import streamlit as st
        st.error(f"Database connection failed: {e}")
        return None