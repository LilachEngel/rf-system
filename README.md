Real-Time RF Data Pipeline & Monitoring System

מערכת מבוזרת לעיבוד, ניטור ואגירת נתוני רדיו (RF) בזמן אמת. המערכת קולטת חבילות מידע, מבצעת עיבוד נתונים, מזהה חריגות, ושומרת את המידע במסדי נתונים שונים בהתאם לסוג המידע.

ארכיטקטורת המערכת (Architecture)

הארכיטקטורה מורכבת מהרכיבים הבאים:

Producer (producer.py):
מייצר סימולטיבית חבילות נתוני RF רדיו-טכניים ודוחף אותם לתור ההודעות.

Message Broker (Redis):
משמש כתור הודעות מהיר (rf_queue) להעברת הנתונים בין היצרן לצרכן.

Consumer (consumer.py):
שולף את הנתונים מהתור, מחשב ממוצע נע, מזהה חריגות עוצמה, שומר את הנתונים הגולמיים ב-MinIO, את המטא-דאטה ב-PostgreSQL, ואת ההתראות ב-MongoDB.

API Backend (api.py):
שרת FastAPI המספק נקודות קצה (Endpoints) לשליפת הדגימות וההתראות עבור ממשק המשתמש.

Frontend (React + Vite):
ממשק משתמש גרפי (דשבורד) המציג את נתוני המערכת וההתראות בזמן אמת.

הצדקת בחירת מנגנון המקביליות (Concurrency Choice)

עבור רכיב ה-Consumer, בחרתי לעבוד במודל של Single-Threaded Blocking Loop בשילוב תור מנוהל (Redis Blocking Pop - blpop):
סיבה מרכזית: הצרכן מעבד את ההודעות מהתור בצורה טורית ומובנית (FIFO), כאשר כל הודעה עוברת סדרת פעולות עוקבות מול מסדי הנתונים (Redis → MongoDB → MinIO → PostgreSQL).
תקשורת I/O Bound: עיקר הזמן של הצרכן אינו מבוסס על חישובים מתמטיים כבדים (CPU-bound) שדורשים Multiprocessing, אלא על המתנה לתשובות מהרשת וממסדי הנתונים (I/O operations). שימוש ב-blpop חוסך צריכת משאבים מיותרת ומבטיח סנכרון מלא ואמינות גבוהה מבלי לאבד הודעות בדרך.

מדריך הרצה מאפס (סביבת Ubuntu)
הנחיות הרצה מניחות שהטרמינל פתוח בתיקיית הבסיס של הפרויקט

שלב 1: דרישות מערכת מקדימות ובדיקת התקנה
לוודא כי הבאים מותקנים באמצעות הפעלת הפקודות הבאות בטרמינל -

Docker & Docker Compose:

docker --version
docker compose version

Python 3.10+:

python3 --version

Node.js & npm:

node -version
npm -version

שלב 2: הפעלת תשתיות ה-Docker
פתיחת הטרמינל בתיקיית הפרויקט שבה נמצא קובץ docker-compose.yml והרצת:
cd /mnt/c/rf-system/backend
docker compose up -d

שלב 3: התקנת והרצת הBackend - Python
pip install -r requirements.txt

שלב 4: פתיחת 3 חלונות טרמינל נפרדים בתיקיית ה-backend והרצת הבאים:

הפעלת ה-API:
cd /mnt/c/rf-system/backend
python3 -m uvicorn api:app --reload
לצפייה בALERTS כנס לכתובת http://localhost:8000/alerts.

הפעלת ה-Consumer (עיבוד הנתונים):
cd /mnt/c/rf-system/backend
python3 consumer.py

הפעלת ה-Producer (ייצור הנתונים ל-Redis):
cd /mnt/c/rf-system/backend
python3 producer.py

שלב 5: הרצת ה-Frontend - React Dashboard
פתיחת טרמינל חדש, מעבר לתיקיית ה-frontend, התקנת החבילות והפעלת הדשבורד:
cd /mnt/c/rf-system/frontend
npm install
npm run dev

כעת ניתן לגשת לדשבורד דרך הדפדפן בכתובת שתוצג בטרמינל (http://localhost:5173).
