import json
import redis
import time
from pymongo import MongoClient
import psycopg2
from minio import Minio 
import io

# הגדרות חיבור
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
mongo_client = MongoClient("mongodb://127.0.0.1:27017/")
mongo_db = mongo_client["rf_alerts_db"]
pg_conn = psycopg2.connect("dbname=rf_db user=user password=password host=localhost") 
minio_client = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)

# יצירת באקט ב-MinIO אם לא קיים
if not minio_client.bucket_exists("rf-data"):
    minio_client.make_bucket("rf-data")

def process_data():
    print("Consumer started, waiting for data...")
    while True:
        # קריאה מהתור (Blocking pop)
        _, message_json = redis_client.blpop("rf_queue")
        msg = json.loads(message_json)
        key = msg['key']
        val = msg['value']
        
        # חישוב ממוצע נע (חלון של 5 דגימות אחרונות) 
        samples = val['samples']
        moving_avg = sum(samples[-5:]) / len(samples[-5:]) if samples else 0
        
        # זיהוי חריגות (מעל -40 dBm) ושמירה ב-MongoDB 
        if any(s > -40 for s in samples):
            alert = {
                "packet_id": key,
                "start_freq": val['start_frequency_mhz'],
                "end_freq": val['end_frequency_mhz'],
                "timestamp": val['timestamp'],
                "samples_window": samples[-5:],
                "average": round(moving_avg, 2)
            }
            mongo_db.alerts.insert_one(alert)
            print(f"!!! Alert detected for packet {key}")

        # שמירת ה-samples כ-JSON ב-MinIO
        file_content = json.dumps(samples).encode('utf-8')
        file_name = f"{key}.json"
        
        minio_client.put_object(
            "rf-data", 
            file_name, 
            io.BytesIO(file_content), 
            len(file_content)
        )

        # שמירת Metadata ב-PostgreSQL (מותאם לטבלת samples שה-API דורש)
        cur = pg_conn.cursor()
        
        # טבלה קיימת עם המבנה הנכון
        cur.execute("""
            CREATE TABLE IF NOT EXISTS samples (
                id VARCHAR(50) PRIMARY KEY,
                frequency FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_data_path VARCHAR(255)
            )
        """)
        
        # שליפת התדר (start_frequency_mhz כברירת מחדל לשדה frequency)
        frequency = val.get('start_frequency_mhz', 0.0)
        
        # הכנסת הנתונים לטבלה (עם התמודדות אם ה-ID כבר קיים)
        cur.execute(
            "INSERT INTO samples (id, frequency, raw_data_path) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;",
            (key, frequency, file_name)
        )
        
        pg_conn.commit()
        cur.close()

        # עדכון הסטטוס הבוליאני
        val['is_finished'] = True
        print(f"Processed packet {key}. Status: {val['is_finished']}")

if __name__ == "__main__":
    process_data()
