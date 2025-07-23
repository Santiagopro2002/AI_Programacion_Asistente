import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    return connection
