# בדיקת משתני סביבה - Environment Variables Check

## בעיה: האימות לא עובד ב-localhost

אם אתה רואה "אימות לא מוגדר" בדף האימות, זה אומר ש-Next.js לא קורא את משתני הסביבה.

## שלבים לבדיקה

### 1. בדוק שהקובץ קיים
הקובץ **חייב** להיות כאן:
```
frontend/
├── .env.local          ← כאן!
├── next.config.js
└── package.json
```

**לא** בתיקיית השורש!

### 2. בדוק את תוכן הקובץ
פתח `frontend/.env.local` וודא שהוא נראה כך:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**חשוב:**
- שמות המשתנים **חייבים** להתחיל ב-`NEXT_PUBLIC_`
- אין רווחים מסביב ל-`=`
- אין גרשיים (לא צריך)
- הערכים לא ריקים

### 3. הפעל מחדש את השרת
**חשוב מאוד:** אחרי יצירה או שינוי של `.env.local`, **חייב** להפעיל מחדש את השרת:

```bash
# עצור את השרת (Ctrl+C)
# ואז הפעל מחדש:
cd frontend
npm run dev
```

Next.js קורא משתני סביבה רק בהפעלה!

### 4. בדוק בקונסול של הדפדפן
אחרי הפעלה מחדש, פתח את קונסול הדפדפן (F12) ותחפש:

```
[Auth Debug] Environment Variables
  NEXT_PUBLIC_SUPABASE_URL: ✅ SET או ❌ MISSING
  NEXT_PUBLIC_SUPABASE_ANON_KEY: ✅ SET או ❌ MISSING
```

אם אתה רואה "MISSING", המשתנים לא נקראים.

## בעיות נפוצות

### בעיה 1: הקובץ במקום הלא נכון
❌ **לא נכון:** `.env.local` בתיקיית השורש  
✅ **נכון:** `frontend/.env.local`

### בעיה 2: שמות משתנים שגויים
❌ **לא נכון:** `SUPABASE_URL` (חסר `NEXT_PUBLIC_`)  
✅ **נכון:** `NEXT_PUBLIC_SUPABASE_URL`

### בעיה 3: השרת לא הופעל מחדש
❌ **לא נכון:** יצרת `.env.local` אבל לא הפעלת מחדש  
✅ **נכון:** הפעל מחדש את השרת אחרי יצירה/שינוי

### בעיה 4: טעות בשם המשתנה
ודא:
- `NEXT_PUBLIC_SUPABASE_URL` (לא `SUPABASE_URL`)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (לא `ANON_KEY` או `SUPABASE_KEY`)

### בעיה 5: ערכים ריקים
ודא שהערכים לא ריקים:
```env
# לא נכון:
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=

# נכון:
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## רשימת בדיקה

- [ ] קובץ `.env.local` קיים בתיקיית `frontend/`
- [ ] הקובץ מכיל `NEXT_PUBLIC_SUPABASE_URL` (עם הקידומת הנכונה)
- [ ] הקובץ מכיל `NEXT_PUBLIC_SUPABASE_ANON_KEY` (עם הקידומת הנכונה)
- [ ] הערכים לא ריקים
- [ ] אין רווחים מסביב ל-`=`
- [ ] השרת הופעל מחדש אחרי יצירה/שינוי הקובץ
- [ ] הקונסול של הדפדפן מציג "SET" עבור שני המשתנים

## עדיין לא עובד?

1. בדוק את הקונסול של הדפדפן - יש הודעות debug
2. ודא שהקובץ לא ב-gitignore (זה בסדר שהוא שם, אבל ודא שהוא קיים)
3. נסה לנקות את ה-cache של הדפדפן ורענון קשיח (Ctrl+Shift+R)
4. בדוק אם יש כמה קבצי `.env.local` (צריך להיות רק אחד ב-`frontend/`)
