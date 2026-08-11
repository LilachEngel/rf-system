from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
from minio import Minio
import psycopg2
from pymongo import MongoClient

# PostgreSQL
def get_pg_connection():
    return psycopg2.connect(
        dbname="rf_db", user="user", password="password", host="localhost", cursor_factory=RealDictCursor
    )
# MongoDB
mongo_client = MongoClient("mongodb://127.0.0.1:27017/")
mongo_db = mongo_client["rf_alerts_db"]

# MinIO
minio_client = Minio(
    "localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
)
BUCKET_NAME = "rf-data"

# יצירת אפליקציית FastAPI עם כותרת וגרסה
app = FastAPI(title="RF Data Pipeline API", version="1.0")

# הגדרת CORS לאפשר גישה מכל מקור לדשבורד של ה-React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# יצירת טבלת samples אוטומטית בעליית השרת 
try:
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS samples (
                    id VARCHAR(255) PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    frequency FLOAT,
                    amplitude FLOAT,
                    status VARCHAR(50),
                    raw_data_path VARCHAR(255)
                );
            """)
            conn.commit()
except Exception as e:
    print(f"Warning: Could not auto-create PostgreSQL table: {e}")


# GET /samples: שליפת 50 הדגימות האחרונות עם פילטור אופציונלי לפי תדר 
@app.get("/samples")
def get_samples(frequency: float = Query(None, description="סינון אופציונלי לפי תדר")):
    conn = get_pg_connection()
    cursor = conn.cursor()

    if frequency is not None:
        query = "SELECT * FROM samples WHERE frequency = %s ORDER BY timestamp DESC LIMIT 50;"
        cursor.execute(query, (frequency,))
    else:
        query = "SELECT * FROM samples ORDER BY timestamp DESC LIMIT 50;"
        cursor.execute(query)

    samples = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"count": len(samples), "samples": samples}


# GET /samples/{id}/raw: שליפת המערך הגולמי מ-MinIO לפי מזהה
@app.get("/samples/{id}/raw")
def get_sample_raw(id: str):
    conn = get_pg_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT raw_data_path FROM samples WHERE id = %s;", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row or not row["raw_data_path"]:
        raise HTTPException(status_code=404, detail="Sample or raw data path not found in database")

    file_path = row["raw_data_path"]

    try:
        response = minio_client.get_object(BUCKET_NAME, file_path)
        data = response.read().decode('utf-8')
        response.close()
        response.release_conn()
        return {"id": id, "file_path": file_path, "raw_data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch from MinIO: {str(e)}")


# GET /alerts: שליפת כל התראות החריגה מ-MongoDB
@app.get("/alerts")
def get_alerts():
    try:
        alerts_cursor = mongo_db.alerts.find()
        alerts = []
        for alert in alerts_cursor:
            alert["_id"] = str(alert["_id"])
            alerts.append(alert)
        return {"count": len(alerts), "alerts": alerts}
    except Exception as e:
        # נדפיס את השגיאה המדויקת לטרמינל כדי שנדע מה קרה אם תהיה בעיה
        print(f"Error fetching alerts from Mongo: {e}")
        raise HTTPException(status_code=500, detail=str(e))
