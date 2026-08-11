import json
import random
import time
import uuid
import redis

# הגדרת חיבור ל-Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

QUEUE_NAME = "rf_queue"

def generate_rf_packet():    
    # מזהה ייחודי לחבילה (Key)
    packet_key = str(uuid.uuid4())
    
    # הגדרת פרמטרים רדיו-טכניים
    rbw = round(random.choice([0.1, 0.25, 0.5, 1.0]), 2)  # Resolution Bandwidth
    start_freq = round(random.uniform(2400.0, 2450.0), 2)  # תדר התחלה ב-MHz
    end_freq = round(start_freq + random.uniform(10.0, 50.0), 2)  # תדר סוף ב-MHz
    
    # חישוב כמות הנקודות: (תדר סוף פחות תדר התחלה חלקי ה-RBW)
    num_points = max(1, int((end_freq - start_freq) / rbw))
    
    # מערך דגימות באורך משתנה 
    samples = [round(random.uniform(-120.0, -20.0), 2) for _ in range(num_points)]
    
    # ערך בוליאני המעיד על סיום עיבוד של הדגימה
    is_finished = random.choice([True, False])
    
    # מבנה ה-Value המלא
    packet_value = {
        "timestamp": time.time(),
        "rbw": rbw,
        "start_frequency_mhz": start_freq,
        "end_frequency_mhz": end_freq,
        "num_points": num_points,
        "samples": samples,
        "is_finished": is_finished
    }
    
    return packet_key, packet_value

def main():
    print("Starting Precise RF Data Producer... Press Ctrl+C to stop.")
    while True:
        # יצירת המפתח והערך
        key, value = generate_rf_packet()
        
        # אריזה למבנה כולל שמכיל את ה-Key וה-Value כמבוקש
        message = {
            "key": key,
            "value": value
        }
        
        # דחיפה ישירה ל-Redis
        redis_client.rpush(QUEUE_NAME, json.dumps(message))
        
        print(f"Sent Packet ID: {key} | Points: {value['num_points']} | Finished: {value['is_finished']}")
        
        # המתנה של שנייה בין חבילה לחבילה
        time.sleep(1)

if __name__ == "__main__":
    main()
