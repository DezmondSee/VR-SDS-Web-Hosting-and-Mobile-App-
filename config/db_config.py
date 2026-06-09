import mysql.connector

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
        print(f"Database connection failed: {e}")
        return None