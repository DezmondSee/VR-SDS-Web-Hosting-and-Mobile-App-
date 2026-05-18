import mysql.connector
import os

def get_db_connection():
    try:
        # When running in Docker, we use the service name 'db' 
        # and the internal port 3306.
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=int(os.getenv('DB_PORT', 3306)), 
            user=os.getenv('DB_USER', 'dezmond_admin'),
            password=os.getenv('DB_PASSWORD', 'password123'),
            database=os.getenv('DB_NAME', 'vrsds_enterprise')
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return N