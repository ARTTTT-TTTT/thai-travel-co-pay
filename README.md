# ✈️ Thai Travel Co Pay

[![Status: Development](https://img.shields.io/badge/Status-Development-yellow)]()

---

## 🛠️ Tech Stack

| Technology | Icon                                                                                                     |
| ---------- | -------------------------------------------------------------------------------------------------------- |
| Python     | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)    |
| FastAPI    | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) |
| SQLite     | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)    |

## ▶️ API Flow

[ POST "/auth/register" ]

↓

[ POST "/auth/login" { (email/phone_number/citizen_id) + password} ]

↓

[ ได้ refresh_token ]

↓

[ ถ้า login ครั้งแรก PATCH "/auth/pin/setup" (ส่ง refresh_token(header) + pin(body)) ]

↓

[ สำเร็จ → ได้ access_token ]

↓

[ ถ้า login ครั้งต่อๆไป หรือ access_token หมดอายุ POST "/auth/pin/access" (ส่ง refresh_token(header) + pin(body)) ]

↓

[ สำเร็จ → ได้ access_token ]

↓

[ ใส่ access_token(header) ในทุก API ต่อไปนี้ ]

↓

[ GET "/users/me" ]

↓

[ POST "/provinces" ]

↓

[ GET "/provinces"  { (optional: ?city_tier=SECONDARY) }]

↓

[ POST "/users/me/travel-plans" ]

↓

[ GET "/users/me/travel-plans" ]