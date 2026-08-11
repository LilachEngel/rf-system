# Real-Time RF Data Pipeline & Monitoring System

מערכת מבוזרת לעיבוד, ניטור ואגירת נתוני רדיו (RF) בזמן אמת. המערכת קולטת חבילות מידע, מעבדת אותן, מזהה חריגות ושומרת את הכל במסדי הנתונים המתאימים.

## ארכיטקטורת המערכת

1. **Producer (`producer.py`)**: מייצר סימולציית חבילות נתוני RF ודוחף אותן לתור ההודעות.
2. **Message Broker (Redis)**: משמש כתור הודעות מהיר (`rf_queue`) שמעביר את הנתונים מהיצרן לצרכן.
3. **Consumer (`consumer.py`)**: שולף את הנתונים מהתור, מחשב ממוצע נע, מזהה חריגות עוצמה, ושומר את הנתונים הגולמיים ב-MinIO, המטא-דאטה ב-PostgreSQL וההתראות ב-MongoDB.
4. **API Backend (`api.py`)**: שרת FastAPI שמספק Endpoints לשליפת הדגימות וההתראות לממשק.
5. **Frontend (React + Vite)**: דשבורד גרפי שמציג את נתוני המערכת וההתראות בזמן אמת.

## בחירת מנגנון המקביליות (Concurrency)

עבור ה-Consumer בחרנו לעבוד במודל של Single-Threaded Blocking Loop בשילוב תור מנוהל (`Redis Blocking Pop - blpop`):

* **למה בחרנו בזה?** הצרכן מעבד את ההודעות בצורה טורית ומסודרת (FIFO), כאשר כל הודעה עוברת סדרת פעולות עוקבות מול מסדי הנתונים (Redis → MongoDB → MinIO → PostgreSQL).
* **תקשורת I/O Bound**: עיקר העבודה כאן היא לא חישובים מתמטיים כבדים שדורשים Multiprocessing, אלא המתנה לתשובות מהרשת וממסדי הנתונים. השימוש ב-`blpop` חוסך עומס מיותר, שומר על סנכרון מלא ומונע איבוד הודעות בדרך.

## מדריך הרצה (סביבת Ubuntu)

### שלב 1: דרישות מערכת

לוודא שהכל מותקן:

* Docker & Docker Compose
* Python 3.10+
* Node.js & npm

### שלב 2: הפעלת תשתיות ה-Docker

```bash
cd backend
docker compose up -d

```

### שלב 3: התקנת ספריות ל-Backend

```bash
pip install -r requirements.txt

```

### שלב 4: הרצת ה-Backend

פתחי 3 טרמינלים נפרדים והריצי בכל אחד מהם:

1. **הפעלת ה-API**:
`python3 -m uvicorn api:app --reload`
*(לצפייה בהתראות אפשר להיכנס ל: `http://localhost:8000/alerts`)*
2. **הפעלת ה-Consumer**:
`python3 consumer.py`
3. **הפעלת ה-Producer**:
`python3 producer.py`

### שלב 5: הרצת ה-Frontend

```bash
cd ../frontend
npm install
npm run dev

```

אפשר להיכנס לדשבורד דרך הכתובת שתוצג בטרמינל (בדרך כלל `http://localhost:5173`).
