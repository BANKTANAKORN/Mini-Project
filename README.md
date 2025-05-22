# Mini-Project: "ระบบจัดการผู้ใช้ + การจองห้องประชุม (User + Room Booking API)"

---

## ฟีเจอร์หลัก

- จัดการผู้ใช้งาน (User)
- จัดการห้องประชุม (Room)
- จองห้องประชุม พร้อมตรวจสอบเวลาซ้อนทับและห้ามจองห้องเวลาย้อนหลัง
- ยกเลิกการจอง (ถ้าต้องการ)
- ตรวจสอบการจองตามวันและห้อง

---

## วิธีติดตั้งและใช้งาน

### 1. Clone โปรเจกต์

```bash
git clone https://github.com/BANKTANAKORN/Mini-Project.git
cd Mini-Project
```

### 2. สร้าง Virtual Environment

#### สำหรับ macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### สำหรับ Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 4. สร้างฐานข้อมูลด้วย Flask-Migrate

```bash
export FLASK_APP=run.py  # สำหรับ macOS / Linux
# หรือใช้ set FLASK_APP=run.py สำหรับ Windows

flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## การรันแอป

```bash
flask run
```

ระบบจะรันที่ `http://127.0.0.1:5000/`

---

## ตัวอย่าง Endpoint

### POST /api/users  
สร้างผู้ใช้งานใหม่  
```json
{
  "name": "Test",
  "email": "test@example.com",
  "department": "IT"
}
```

### GET /api/users/<users_id>   
ดึงข้อมูลผู้ใช้ตาม id

### POST /api/rooms  
สร้างห้องใหม่  
```json
{
  "room_name": "Meeting Room A",
  "floor": "3",
  "capacity": 10
}
```

### POST /api/bookings  
จองห้องประชุม  
```json
{
  "user_id": 1,
  "room_id": 1,
  "start_time": "2025-05-23T10:00:00",
  "end_time": "2025-05-23T11:00:00"
}
```

### GET /api/bookings?room_id=1&date=2025-05-23  
ดูการจองห้องของวันที่กำหนด

### DELETE /api/bookings/<booking_id>  
ยกเลิกการจอง

---

## การทดสอบ

คุณสามารถรันการทดสอบได้ในโฟลเดอร์ `tests/`  
```bash
pytest tests/test_api.py  
```
```bash
pytest tests/test_models.py  
```
```bash
pytest tests/test_services.py  
```

---

## ข้อมูลเพิ่มเติม

- ระบบใช้ SQLite เป็นฐานข้อมูลหลัก
- สามารถเปลี่ยน `DATABASE_URL` ผ่าน `.env` ได้
- โครงสร้างโปรเจกต์แยกตามมาตรฐาน Flask (Blueprint + Services + Models)

---

## โครงสร้างโปรเจกต์

```
Mini-Project/
│
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── models.py
│   ├── services.py
│
├── tests/
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_api.py
│
├── instance/
│   ├── db.sqlite          # ไฟล์ฐานข้อมูล
│
├── migrations/            # ไฟล์สำหรับ Flask-Migrate
├── run.py                 # จุดรันแอป
├── requirements.txt
├── .env
└── README.md
```