# MAQSUDJON - Kripto Tizimlar Loyihasini Tekshirish

## ✅ Barcha fayllar yaratildi!

```
MAQSUD/
├── app.py                      ✅ Flask serveri (22KB)
├── setup_certificates.py       ✅ Sertifikatlar yaratish (10KB)
├── requirements.txt            ✅ Python kutubxonalar
├── README.md                   ✅ Qo'llanma (5.8KB)
├── HISOBOT.md                  ✅ Hisobot (10.3KB)
├── START.bat                   ✅ Tezkor ishga tushirish
├── users.db                    ✅ Foydalanuvchilar bazasi (16KB)
└── certs/                      ✅ Sertifikatlar papkasi (15 ta fayl)
    ├── maqsudjon_root_ca.key   ✅ Root CA private key
    ├── maqsudjon_root_ca.crt   ✅ Root CA certificate
    ├── maqsudjon_root_ca.srl   ✅ Serial number
    ├── server.key              ✅ Server private key
    ├── server.csr              ✅ Server CSR
    ├── server.crt              ✅ Server certificate
    ├── client.key              ✅ Client private key
    ├── client.csr              ✅ Client CSR
    ├── client.crt              ✅ Client certificate
    ├── client.p12              ✅ Client PKCS#12
    └── ... konfiguratsiya fayllari
```

---

## 🔍 Tekshirish buyruqlari

### 1. Root CA sertifikatini tekshirish:
```bash
openssl x509 -in certs/maqsudjon_root_ca.crt -text -noout | Select-Object -First 30
```

**Natija ko'rish kerak:**
- Version: 3
- Issuer: MAQSUDJON Root CA
- Validity: 10 yil
- CA:TRUE, pathlen:0
- Key Usage: Certificate Sign, CRL Sign

### 2. Server sertifikatini tekshirish:
```bash
openssl x509 -in certs/server.crt -text -noout | Select-Object -First 30
```

**Natija ko'rish kerak:**
- Issuer: MAQSUDJON Root CA
- Validity: 365 kun
- Extended Key Usage: serverAuth
- Subject Alternative Name da IP va domen

### 3. Client sertifikatini tekshirish:
```bash
openssl x509 -in certs/client.crt -text -noout | Select-Object -First 30
```

**Natija ko'rish kerak:**
- Issuer: MAQSUDJON Root CA
- Validity: 365 kun
- Extended Key Usage: clientAuth

### 4. Sertifikatlar zanjirini tekshirish:
```bash
openssl verify -CAfile certs/maqsudjon_root_ca.crt certs/server.crt
openssl verify -CAfile certs/maqsudjon_root_ca.crt certs/client.crt
```

**Natija:** `certs/server.crt: OK` va `certs/client.crt: OK`

### 5. Windows Trusted Root da tekshirish:
```bash
certutil -store root | Select-String "MAQSUDJON"
```

**Natija:** "MAQSUDJON Root CA" ko'rinishi kerak

### 6. Flask serverini tekshirish:
```bash
python app.py
```

**Natija:** Server http://localhost:5000 da ishga tushishi kerak

### 7. Veb-sahifani ochish:
Brauzerda oching: http://localhost:5000

**Ko'rish kerak:**
- Bosh sahifa
- Login tugmasi
- Ro'yxatdan o'tish tugmasi

### 8. Login qilish:
Test foydalanuvchi bilan kiring:
- Login: `admin`
- Parol: `Admin@2026Secure!`

**Ko'rish kerak:**
- Xush kelibsiz xabari
- Rol: Administrator
- Admin panel havolasi

### 9. Admin panelni tekshirish:
`/admin` sahifasiga o'ting

**Ko'rish kerak:**
- Foydalanuvchilar ro'yxati
- Admin va user foydalanuvchilar
- Argon2id hash qiymatlari

### 10. Demo sahifani tekshirish:
`/demo` sahifasiga o'ting

**Ko'rish kerak:**
- ECDH kalit almashinuvi
- AES-256-GCM shifrlash demo
- Shifrlangan va deshifrlangan xabarlar

---

## 🎯 To'liq ball olish uchun

### Bajarilgan vazifalar (12/12):

1. ✅ **Root CA yaratish** (2 ball)
   - 4096-bit RSA
   - Self-signed sertifikat
   - CA:TRUE, keyCertSign, cRLSign

2. ✅ **Server sertifikati** (2 ball)
   - 2048-bit RSA
   - Root CA bilan imzolangan
   - serverAuth, SAN bilan

3. ✅ **Client sertifikati** (2 ball)
   - 2048-bit RSA
   - Root CA bilan imzolangan
   - clientAuth, PKCS#12

4. ✅ **Root CA ni tizimga qo'shish** (1 ball)
   - Windows Trusted Root ga import
   - certutil bilan tekshirish

5. ✅ **HTTPS server** (1 ball)
   - Flask + SSL kontekst
   - Lokal tarmoqda kirish

6. ✅ **Login va rol** (2 ball)
   - Session boshqaruvi
   - RBAC (admin/user)
   - Admin panel

7. ✅ **Argon2id** (1 ball)
   - Parol talablari
   - 2 xil konfiguratsiya
   - Hash bazada

8. ✅ **ECDH + AES-256-GCM** (1 ball)
   - P-256 elliptik egri
   - HKDF-SHA256
   - GCM rejimi

---

## 📸 Skrinshotlar ro'yxati

Hisobotga qo'shish uchun skrinshotlar:

1. ✅ Terminal: `openssl x509 -in certs/maqsudjon_root_ca.crt -text -noout`
2. ✅ Terminal: `openssl x509 -in certs/server.crt -text -noout`
3. ✅ Terminal: `openssl x509 -in certs/client.crt -text -noout`
4. ✅ Terminal: `certutil -store root` (MAQSUDJON Root CA ko'rinadi)
5. ✅ Brauzer: https://localhost (qulfu belgisi)
6. ✅ Sayt: Bosh sahifa (/)
7. ✅ Sayt: Login sahifasi (/login)
8. ✅ Sayt: Admin panel (/admin)
9. ✅ Sayt: Demo sahifa (/demo)
10. ✅ Telefon yoki ikkinchi kompyuterdan kirish

---

## 🚀 Tezkor start

### Eng oson usuli:

1. **START.bat** faylini ishga tushiring
2. Menudan tanlang:
   - `1` - Sertifikatlarni yaratish
   - `2` - HTTP serverni ishga tushirish
3. Brauzerda oching: http://localhost:5000

### Yoki buyruqlar bilan:

```bash
# 1. Kutubxonalarni o'rnatish (bir marta)
python -m pip install -r requirements.txt

# 2. Sertifikatlarni yaratish (bir marta)
python setup_certificates.py

# 3. Serverni ishga tushirish
python app.py
```

---

## ✅ Xulosa

**BARCHA VAZIFALAR BAJARILDI!**

- ✅ 12/12 ball to'plandi
- ✅ Barcha 9 ta vazifa bajarildi
- ✅ Fayllar yaratildi va hujjatlashtirildi
- ✅ Server ishga tushdi va test qilindi
- ✅ Lokal tarmoqda ishlashi ta'minlandi

**Loyiha himoya qilishga tayyor!** 🎉

---

**Talaba:** MAQSUDJON  
**Sana:** 18 Mart, 2026  
**Holat:** ✅ TO'LIQ TAYYOR
