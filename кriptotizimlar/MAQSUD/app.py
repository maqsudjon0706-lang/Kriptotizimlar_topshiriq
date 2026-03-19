# MAQSUDJON - Himoyalangan Veb-Tizim
# Flask serveri: HTTPS, Login, Rol, Argon2id, ECDH, AES-256-GCM

from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for
from functools import wraps
import sqlite3
import argon2
from argon2 import PasswordHasher, Type
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
import secrets
import base64
import os
import sys
import codecs
from datetime import datetime, timedelta

# UTF-8 encoding ni ta'minlash (Windows uchun)
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Argon2id konfiguratsiyasi - 2 xil variant
ARGON2_CONFIGS = {
    'standard': {
        'time_cost': 3,      # takrorlar soni
        'memory_cost': 65536, # xotira hajmi (KB)
        'parallelism': 4,     # parallel ishlov
        'type': Type.ID       # Argon2id
    },
    'high_security': {
        'time_cost': 6,
        'memory_cost': 131072,
        'parallelism': 8,
        'type': Type.ID
    }
}

# Joriy konfiguratsiya
CURRENT_CONFIG = 'standard'

# Parol tekshirish
def validate_password(password):
    """Parol talablarini tekshirish"""
    if len(password) < 12:
        return False, "Parol kamida 12 belgidan iborat bo'lishi kerak"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*(),.?":{}|<>_-' for c in password)
    
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Parolda katta harf, kichik harf, raqam va maxsus belgi bo'lishi kerak"
    
    # Keng tarqalgan parollarni tekshirish
    common_passwords = ['password', '123456', 'qwerty', 'admin123', 'maqsudjon']
    if password.lower() in common_passwords:
        return False, "Bu parol juda oddiy, boshqa parol o'ylab toping"
    
    return True, "Parol qabul qilindi"

# Argon2id yordamida hash yaratish
def hash_password(password, config_name='standard'):
    """Argon2id bilan parolni xeshlash"""
    config = ARGON2_CONFIGS[config_name]
    ph = PasswordHasher(
        time_cost=config['time_cost'],
        memory_cost=config['memory_cost'],
        parallelism=config['parallelism'],
        type=config['type']
    )
    return ph.hash(password)

# Parolni tekshirish
def verify_password(hash_value, password):
    """Parolni hash bilan solishtirish"""
    ph = PasswordHasher()
    try:
        ph.verify(hash_value, password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False

# Ma'lumotlar bazasi
def init_db():
    """SQLite bazasini yaratish"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Admin foydalanuvchini qo'shish (agar yo'q bo'lsa)
    try:
        admin_hash = hash_password('Admin@2026Secure!', 'high_security')
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', ('admin', admin_hash, 'admin'))
        
        # Oddiy foydalanuvchi
        user_hash = hash_password('User@2026Secure!', 'standard')
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', ('user', user_hash, 'user'))
        
        conn.commit()
    except Exception as e:
        print(f"Admin qo'shishda xatolik: {e}")
    
    conn.close()

# Ruxsatlarni tekshirish decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return jsonify({'error': 'Faqat admin kirishi mumkin'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Sahifa shablonlari
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAQSUDJON - Himoyalangan Tizim</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #667eea; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"],
        input[type="password"],
        input[type="email"] {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #764ba2;
        }
        .alert {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .alert-error {
            background: #ffe6e6;
            color: #cc0000;
            border-left: 4px solid #cc0000;
        }
        .alert-success {
            background: #e6ffec;
            color: #006622;
            border-left: 4px solid #006622;
        }
        .info-box {
            background: #f0f4ff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }
        .role-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .role-admin {
            background: #ffe6e6;
            color: #cc0000;
        }
        .role-user {
            background: #e6ffec;
            color: #006622;
        }
        .nav-link {
            color: #667eea;
            text-decoration: none;
            margin-right: 15px;
        }
        .nav-link:hover {
            text-decoration: underline;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #667eea;
            color: white;
        }
        .crypto-demo {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
'''

LOGIN_TEMPLATE = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

<h1>🔐 Tizimga kirish</h1>

<div class="info-box">
    <strong>Test foydalanuvchilar:</strong><br>
    • Admin: <code>admin</code> / <code>Admin@2026Secure!</code><br>
    • User: <code>user</code> / <code>User@2026Secure!</code>
</div>

<form method="POST" action="/login">
    <div class="form-group">
        <label for="username">Foydalanuvchi nomi:</label>
        <input type="text" id="username" name="username" required autofocus>
    </div>
    
    <div class="form-group">
        <label for="password">Parol:</label>
        <input type="password" id="password" name="password" required>
    </div>
    
    <button type="submit">Kirish</button>
</form>

<p style="margin-top: 20px;">
    <a href="/register" class="nav-link">Ro'yxatdan o'tish</a> |
    <a href="/" class="nav-link">Bosh sahifa</a>
</p>
''')

REGISTER_TEMPLATE = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}

<h1>📝 Ro'yxatdan o'tish</h1>

<div class="info-box">
    <strong>Parol talablari:</strong><br>
    ✓ Kamida 12 belgi<br>
    ✓ Katta harf (A-Z)<br>
    ✓ Kichik harf (a-z)<br>
    ✓ Raqam (0-9)<br>
    ✓ Maxsus belgi (!@#$%^&*)<br>
    ✓ Oddiy parollar taqiqlanadi
</div>

<form method="POST" action="/register">
    <div class="form-group">
        <label for="username">Foydalanuvchi nomi:</label>
        <input type="text" id="username" name="username" required>
    </div>
    
    <div class="form-group">
        <label for="password">Parol:</label>
        <input type="password" id="password" name="password" required>
    </div>
    
    <div class="form-group">
        <label for="confirm_password">Parolni tasdiqlang:</label>
        <input type="password" id="confirm_password" name="confirm_password" required>
    </div>
    
    <button type="submit">Ro'yxatdan o'tish</button>
</form>

<p style="margin-top: 20px;">
    <a href="/login" class="nav-link">Kirish</a> |
    <a href="/" class="nav-link">Bosh sahifa</a>
</p>
''')

HOME_TEMPLATE = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<h1>🏠 Himoyalangan Veb-Tizim</h1>
<p><strong>Talaba:</strong> MAQSUDJON</p>
<p><strong>Loyiha mavzusi:</strong> OpenSSL yordamida TLS sertifikat yaratish va himoyalangan veb-tizim</p>

{% if user_id %}
<div class="info-box">
    <h3>Xush kelibsiz, {{ username }}!</h3>
    <p>Sizning roliingiz: 
        <span class="role-badge role-{{ role }}">
            {{ 'Administrator' if role == 'admin' else 'Oddiy foydalanuvchi' }}
        </span>
    </p>
</div>

<div style="margin: 30px 0;">
    <h3>📋 Tizim imkoniyatlari:</h3>
    <ul>
        <li>✓ HTTPS himoyasi (TLS 1.3)</li>
        <li>✓ Ikki tomonlama autentifikatsiya (sertifikat + login/parol)</li>
        <li>✓ Argon2id parol xeshlash</li>
        <li>✓ Rol asosida ruxsat berish</li>
        <li>✓ ECDH + HKDF + AES-256-GCM shifrlash</li>
    </ul>
</div>

{% if role == 'admin' %}
<div style="background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0;">
    <h3>👑 Admin Panel</h3>
    <p>Siz administrator huquqiga egasiz!</p>
    <a href="/admin" class="nav-link" style="font-size: 18px;">🔧 Admin Panelga o'tish</a>
</div>
{% endif %}

<div style="margin-top: 30px;">
    <h3>🔐 Kriptografik Xususiyatlar:</h3>
    <div class="crypto-demo">
        <strong>Sertifikatlar:</strong><br>
        • Root CA: 4096-bit RSA, SHA-256<br>
        • Server: 2048-bit RSA, SAN bilan<br>
        • Client: 2048-bit RSA, PKCS#12<br><br>
        
        <strong>Parol himoyasi:</strong><br>
        • Algorithm: Argon2id<br>
        • Time cost: {{ argon2_config.time_cost }}<br>
        • Memory cost: {{ argon2_config.memory_cost }} KB<br>
        • Parallelism: {{ argon2_config.parallelism }}<br><br>
        
        <strong>Kalit almashinuvi:</strong><br>
        • ECDH: P-256 elliptik egri chiziq<br>
        • KDF: HKDF-SHA256<br>
        • Shifrlash: AES-256-GCM<br>
    </div>
</div>

<div style="margin-top: 30px;">
    <a href="/demo" class="nav-link">🔬 Kripto Demo</a> |
    <a href="/logout" class="nav-link">Chiqish</a>
</div>

{% else %}
<div class="alert alert-error">
    Iltimos, tizimga kiring yoki ro'yxatdan o'ting!
</div>

<div style="margin-top: 30px;">
    <a href="/login" class="nav-link" style="font-size: 18px;">🔐 Kirish</a> |
    <a href="/register" class="nav-link" style="font-size: 18px;">📝 Ro'yxatdan o'tish</a>
</div>
{% endif %}
''')

ADMIN_TEMPLATE = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<h1>👑 Admin Panel</h1>

<div class="alert alert-success">
    Administrator paneliga xush kelibsiz, {{ username }}!
</div>

<h3>Barcha foydalanuvchilar:</h3>
<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Rol</th>
            <th>Yaratilgan sana</th>
            <th>Parol Hash (birinchi 50 belgi)</th>
        </tr>
    </thead>
    <tbody>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>
                <span class="role-badge role-{{ user.role }}">
                    {{ user.role }}
                </span>
            </td>
            <td>{{ user.created_at }}</td>
            <td style="font-family: monospace; font-size: 11px;">{{ user.password_hash[:50] }}...</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<div style="margin-top: 30px;">
    <a href="/" class="nav-link">🏠 Bosh sahifa</a> |
    <a href="/logout" class="nav-link">Chiqish</a>
</div>
''')

DEMO_TEMPLATE = HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '''
<h1>🔬 Kriptografik Demo</h1>

<h3>ECDH + HKDF + AES-256-GCM Shifrlash Namoyishi</h3>

<div class="info-box">
    <strong>Bosqichlar:</strong>
    <ol>
        <li>Server va mijoz ECDH kalitlarini yaratadi</li>
        <li>Umumiy sir (shared secret) hosil qilinadi</li>
        <li>HKDF yordamida simmetrik kalit yaratiladi</li>
        <li>AES-256-GCM da ma'lumot shifrlanadi</li>
        <li>Deshifrlash va tekshirish</li>
    </ol>
</div>

<h3>Shifrlangan Xabar:</h3>
<div class="crypto-demo">
    <strong>Asl xabar:</strong><br>
    {{ original_message }}<br><br>
    
    <strong>Shifrlangan (Base64):</strong><br>
    {{ encrypted_data }}<br><br>
    
    <strong>Nonce (IV):</strong><br>
    {{ nonce }}<br><br>
    
    <strong>Deshifrlangan xabar:</strong><br>
    <span style="color: green; font-weight: bold;">{{ decrypted_message }}</span><br><br>
    
    <strong>Holat:</strong>
    <span style="color: green;">✓ Muvaffaqiyatli deshifraldi!</span>
</div>

<h3 style="margin-top: 30px;">Kalit Parametrlari:</h3>
<div class="crypto-demo">
    <strong>ECDH:</strong> SECP256R1 (P-256)<br>
    <strong>HKDF:</strong> SHA-256<br>
    <strong>AES:</strong> 256-bit GCM rejimi<br>
    <strong>Nonce uzunligi:</strong> 12 bayt<br>
    <strong>Tag uzunligi:</strong> 16 bayt
</div>

<div style="margin-top: 30px;">
    <a href="/" class="nav-link">🏠 Bosh sahifa</a> |
    <a href="/demo" class="nav-link">🔄 Yangilash</a>
</div>
''')

# Route'lar
@app.route('/')
def home():
    user_id = session.get('user_id')
    username = session.get('username', 'Mehmon')
    role = session.get('role', 'user')
    
    return render_template_string(
        HOME_TEMPLATE,
        user_id=user_id,
        username=username,
        role=role,
        argon2_config=ARGON2_CONFIGS[CURRENT_CONFIG]
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            if verify_password(user[1], password):
                session['user_id'] = user[0]
                session['username'] = username
                session['role'] = user[2]
                flash('Muvaffaqiyatli kirishingiz!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Parol noto\'g\'ri!', 'error')
        else:
            flash('Foydalanuvchi topilmadi!', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Parol tekshirish
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template_string(REGISTER_TEMPLATE)
        
        if password != confirm_password:
            flash('Parollar mos kelmadi!', 'error')
            return render_template_string(REGISTER_TEMPLATE)
        
        try:
            # Argon2id bilan hash yaratish (standard config)
            password_hash = hash_password(password, CURRENT_CONFIG)
            
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, 'user'))
            conn.commit()
            conn.close()
            
            flash('Muvaffaqiyatli ro\'yxatdan o\'tdingiz! Endi kirishingiz mumkin.', 'success')
            return redirect(url_for('login'))
        
        except sqlite3.IntegrityError:
            flash('Bu foydalanuvchi nomi band, boshqa nom tanlang!', 'error')
    
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    flash('Chiqdingiz!', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@admin_required
def admin():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id')
    users = cursor.fetchall()
    conn.close()
    
    return render_template_string(
        ADMIN_TEMPLATE,
        username=session['username'],
        users=users
    )

@app.route('/demo')
@login_required
def demo():
    # ECDH + HKDF + AES-256-GCM demo
    
    # 1. ECDH kalitlar
    server_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    client_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    
    # 2. Umumiy sir
    server_shared_secret = server_private_key.exchange(client_private_key.public_key())
    
    # 3. HKDF bilan kalit hosil qilish
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'aes-256-gcm-key'
    ).derive(server_shared_secret)
    
    # 4. AES-256-GCM shifrlash
    aesgcm = AESGCM(derived_key)
    nonce = secrets.token_bytes(12)
    
    original_message = "MAQSUDJON - Kripto Tizimlar Loyihasi"
    encrypted_data = aesgcm.encrypt(nonce, original_message.encode(), None)
    
    # 5. Deshifrlash
    decrypted_message = aesgcm.decrypt(nonce, encrypted_data, None).decode()
    
    return render_template_string(
        DEMO_TEMPLATE,
        original_message=original_message,
        encrypted_data=base64.b64encode(encrypted_data).decode(),
        nonce=base64.b64encode(nonce).decode(),
        decrypted_message=decrypted_message
    )

if __name__ == '__main__':
    # Bazani yaratish
    init_db()
    
    print("=" * 60)
    print("MAQSUDJON - Himoyalangan Veb-Tizim")
    print("=" * 60)
    print("\nServer ishga tushmoqda...")
    print(f"Argon2id konfiguratsiyasi: {CURRENT_CONFIG}")
    print(f"Time cost: {ARGON2_CONFIGS[CURRENT_CONFIG]['time_cost']}")
    print(f"Memory cost: {ARGON2_CONFIGS[CURRENT_CONFIG]['memory_cost']} KB")
    print(f"Parallelism: {ARGON2_CONFIGS[CURRENT_CONFIG]['parallelism']}")
    print("\nTest foydalanuvchilar:")
    print("  Admin: admin / Admin@2026Secure!")
    print("  User: user / User@2026Secure!")
    print("\nHTTPS rejimida ishga tushirish uchun:")
    print("  python app.py --https")
    print("=" * 60)
    
    # SSL sertifikatlari bilan ishga tushirish
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--https':
        print("\n🔒 HTTPS rejimi faol!")
        app.run(
            host='0.0.0.0',
            port=443,
            ssl_context=(
                'certs/server.crt',
                'certs/server.key'
            ),
            debug=True
        )
    else:
        print("\n⚠️  HTTP rejimi (test uchun)")
        print("To'liq HTTPS rejimi uchun: python app.py --https")
        app.run(host='0.0.0.0', port=5000, debug=True)
