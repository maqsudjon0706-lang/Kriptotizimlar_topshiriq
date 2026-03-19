# MAQSUDJON - Kripto Tizimlar Loyihasi
# O'rnatish va ishga tushirish bo'yicha qo'llanma

## 📋 Talablar

- Python 3.10 yoki undan yuqori
- OpenSSL 3.x
- Windows 10/11 (Administrator huquqlari)

## 🔧 1-QADAM: Kutubxonalarni o'rnatish

```bash
python -m pip install -r requirements.txt
```

## 📜 2-QADAM: Sertifikatlarni yaratish

### Windows uchun:
```bash
python setup_certificates.py
```

Bu skript quyidagilarni bajaradi:
- ✅ Root CA (Sertifikatlash Markazi) yaratadi
- ✅ Server sertifikatini yaratadi
- ✅ Client sertifikatini yaratadi
- ✅ Root CA ni Windows Trusted Root ga qo'shadi

**Muhim:** Administrator huquqlari talab qilinadi!

Agar import qilishda xatolik bo'lsa, qo'lda bajaring:
1. `certs\maqsudjon_root_ca.crt` faylini oching
2. "Install Certificate" tugmasini bosing
3. "Local Machine" tanlang
4. "Trusted Root Certification Authorities" ni tanlang
5. Next va Finish

## 🌐 3-QADAM: Veb-serverni ishga tushirish

### HTTPS rejimida (tavsiya etiladi):
```bash
python app.py --https
```

### HTTP rejimida (test uchun):
```bash
python app.py
```

Server quyidagi manzilda ishga tushadi:
- HTTPS: https://localhost
- HTTP: http://localhost:5000

## 👥 Test foydalanuvchilar

### Admin:
- **Login:** admin
- **Parol:** Admin@2026Secure!
- **Rol:** Administrator

### Oddiy foydalanuvchi:
- **Login:** user
- **Parol:** User@2026Secure!
- **Rol:** User

## 🎯 Vazifalar va tekshirish

### ✅ 1-Vazifa: Root CA yaratish
**Tekshirish:**
```bash
openssl x509 -in certs/maqsudjon_root_ca.crt -text -noout
```

**Natija:** Sertifikatda CA:TRUE, keyCertSign, cRLSign ko'rsatilgan bo'lishi kerak.

### ✅ 2-Vazifa: Server sertifikati
**Tekshirish:**
```bash
openssl verify -CAfile certs/maqsudjon_root_ca.crt certs/server.crt
openssl x509 -in certs/server.crt -text -noout
```

**Natija:** Server Auth, SAN da IP va domen ko'rsatilgan.

### ✅ 3-Vazifa: Client sertifikati
**Tekshirish:**
```bash
openssl verify -CAfile certs/maqsudjon_root_ca.crt certs/client.crt
openssl pkcs12 -in certs/client.p12 -info
```

**Natija:** Client Auth, PKCS#12 formatida.

### ✅ 4-Vazifa: Root CA ni tizimga qo'shish
**Tekshirish:**
```bash
certutil -store root
```

Ro'yxatda "MAQSUDJON Root CA" bo'lishi kerak.

### ✅ 5-Vazifa: HTTPS server
Brauzerda https://localhost manziliga o'ting.
**Natija:** Xavfsizlik ogohlantirishi bo'lmasligi kerak (Root CA import qilingan bo'lsa).

### ✅ 6-Vazifa: Login va rol
- Saytga kiring
- Admin bilan kirib, admin panelni tekshiring
- User bilan kirib, admin panelga kira olmasligini tekshiring

### ✅ 7-Vazifa: Argon2id
Ro'yxatdan o'tish sahifasida parol talablari tekshiriladi.
Admin panelda hash qiymatini ko'ring.

**Parametrlar:**
- Standard: time_cost=3, memory_cost=65536, parallelism=4
- High Security: time_cost=6, memory_cost=131072, parallelism=8

### ✅ 8-Vazifa: ECDH + AES-256-GCM
/demo sahifasiga o'ting va shifrlash jarayonini ko'ring.

### ✅ 9-Vazifa: Lokal tarmoqda sinov
1. Kompyuteringizning lokal IP manzilini aniqlang:
   ```bash
   ipconfig
   ```

2. Boshqa qurilmadan (telefon yoki ikkinchi kompyuter) kiriting:
   ```
   https://[SIZNING_IP_MANZIL]
   ```

3. Brauzer xavfsizlik ogohlantirishi bermasligi kerak!

## 📊 Baholash mezoni

| № | Mezoni | Ball |
|---|--------|------|
| 1 | Root CA to'g'ri yaratish | 2 |
| 2 | Server sertifikati | 2 |
| 3 | Client sertifikati + 2FA | 2 |
| 4 | Root CA ni tizimga qo'shish | 1 |
| 5 | HTTPS server ishlashi | 1 |
| 6 | Login va rol mexanizmi | 2 |
| 7 | Argon2id sozlash | 1 |
| 8 | ECDH + AES-256-GCM | 1 |
| **JAMI** | | **12** |

## 📁 Fayl tuzilmasi

```
MAQSUD/
├── app.py                      # Flask serveri
├── setup_certificates.py       # Sertifikatlar yaratish
├── requirements.txt            # Python kutubxonalar
├── README.md                   # Ushbu fayl
├── certs/                      # Sertifikatlar papkasi
│   ├── maqsudjon_root_ca.key   # Root CA private key
│   ├── maqsudjon_root_ca.crt   # Root CA certificate
│   ├── server.key              # Server private key
│   ├── server.csr              # Server CSR
│   ├── server.crt              # Server certificate
│   ├── client.key              # Client private key
│   ├── client.csr              # Client CSR
│   ├── client.crt              # Client certificate
│   └── client.p12              # Client PKCS#12 (brauzer uchun)
└── users.db                    # Foydalanuvchilar bazasi
```

## 🔍 Muhim eslatmalar

1. **Xavfsizlik:** Bu test muhiti! Production uchun boshqa sertifikatlardan foydalaning.

2. **Port 443:** HTTPS rejimida port 443 administrator huquqlarini talab qiladi.
   
   PowerShell administrator rejimida ishga tushiring:
   - Start menyu → "PowerShell" → "Run as administrator"
   - `cd d:\DARS\KRIPTOTIZIMLAR\MAQSUD`
   - `python app.py --https`

3. **Firewall:** Agar boshqa qurilmalardan kirish kerak bo'lsa, firewall da 443-portni oching.

4. **Sertifikat muddati:** Sertifikatlar 365 kun amal qiladi.

## 🆘 Yordam

Agar muammo yuzaga kelsa:

1. **Python versiyasi:** `python --version`
2. **OpenSSL versiyasi:** `openssl version`
3. **Kutubxonalar:** `pip list`

Barcha chiqishlarni skrinshot qilib oling va loyiha hisobotiga qo'shing!

## 📸 Skrinshotlar ro'yxati

Hisobot uchun quyidagi skrinshotlarni oling:

1. Root CA sertifikati ma'lumotlari
2. Server sertifikati ma'lumotlari
3. Client sertifikati ma'lumotlari
4. Windows Trusted Root da MAQSUDJON Root CA
5. HTTPS sayti brauzerda
6. Login sahifasi
7. Admin panel
8. Argon2id hash bazada
9. /demo sahifasi (ECDH + AES demo)
10. Boshqa qurilmadan kirish

---

**Talaba:** MAQSUDJON  
**Sana:** 2026  
**Fan:** Kripto Tizimlar
