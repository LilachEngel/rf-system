README
Real-Time RF Data Pipeline & Monitoring System


מערכת מבוזרת לעיבוד, ניטור ואגירת נתוני רדיו (RF) בזמן אמת. המערכת קולטת חבילות מידע, מבצעת עיבוד נתונים, מזהה חריגות, ושומרת את המידע במסדי נתונים שונים בהתאם לסוג המידע.




ארכיטקטורת המערכת (Architecture)


הארכיטקטורה מורכבת מהרכיבים הבאים:
1. **Producer (producer.py)**: 
מייצר סימולטיבית חבילות נתוני RF רדיו-טכניים ודוחף אותם לתור ההודעות.
2. **Message Broker (Redis)**: 
משמש כתור הודעות מהיר (rf_queue) להעברת הנתונים בין היצרן לצרכן.
3. **Consumer (consumer.py)**:
 שולף את הנתונים מהתור, מחשב ממוצע נע, מזהה חריגות עוצמה, שומר את הנתונים הגולמיים ב-MinIO, את המטא-דאטה ב-PostgreSQL, ואת ההתראות ב-MongoDB.
4. **API Backend (api.py)**: 
שרת FastAPI המספק נקודות קצה (Endpoints) לשליפת הדגימות וההתראות עבור ממשק המשתמש.
5. **Frontend (React + Vite)**: 
ממשק משתמש גרפי (דשבורד) המציג את נתוני המערכת וההתראות בזמן אמת.




הצדקת בחירת מנגנון המקביליות (Concurrency Choice)


עבור רכיב ה-Consumer, בחרנו לעבוד במודל של Single-Threaded Blocking Loop בשילוב תור מנוהל (Redis Blocking Pop - blpop):
סיבה מרכזית: הצרכן מעבד את ההודעות מהתור בצורה טורית ומובנית (FIFO), כאשר כל הודעה עוברת סדרת פעולות עוקבות מול מסדי הנתונים (Redis → MongoDB → MinIO → PostgreSQL). 
תקשורת I/O Bound: עיקר הזמן של הצרכן אינו מבוסס על חישובים מתמטיים כבדים (CPU-bound) שדורשים Multiprocessing, אלא על המתנה לתשובות מהרשת וממסדי הנתונים (I/O operations). שימוש ב-blpop חוסך צריכת משאבים מיותרת ומבטיח סנכרון מלא ואמינות גבוהה מבלי לאבד הודעות בדרך.




מדריך הרצה מאפס (סביבת Ubuntu)
*הנחיות הרצה מניחות שהטרמינל פתוח בתיקיית הבסיס של הפרויקט*


שלב 1: דרישות מערכת מקדימות ובדיקת התקנה 
לוודא כי הבאים מותקנים באמצעות הפעלת הפקודות הבאות בטרמינל -
1. Docker & Docker Compose:
docker --version
docker compose version
2. Python 3.10+: 
python3 --version


3. Node.js & npm: 
node -version
npm -version
שלב 2: הפעלת תשתיות ה-Docker
פתיחת הטרמינל בתיקיית הפרויקט שבה נמצא קובץ docker-compose.yml והרצת:
docker compose up -d


שלב 3: התקנת והרצת הBackend - Python
cd rf-system/backend
pip install -r requirements.txt






שלב 4: פתיחת 3 חלונות טרמינל נפרדים בתיקיית ה-backend והרצת הבאים:
1. הפעלת ה-API: 
Python3 -m uvicorn api:app --reload
2. הפעלת ה-Consumer (עיבוד הנתונים):
python consumer.py
3. הפעלת ה-Producer (ייצור הנתונים ל-Redis):
python producer.py
שלב 5: הרצת ה-Frontend - React Dashboard
פתיחת טרמינל חדש, מעבר לתיקיית ה-frontend, התקנת החבילות והפעלת הדשבורד:
cd ../frontend
npm install
npm run dev
כעת ניתן לגשת לדשבורד דרך הדפדפן בכתובת שתוצג בטרמינל (http://localhost:5173).
