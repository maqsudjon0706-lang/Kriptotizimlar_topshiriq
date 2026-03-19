# MAQSUDJON - Kripto Tizimlar Loyihasi
# OpenSSL yordamida TLS sertifikat yaratish va himoyalangan veb-tizim

import os
import subprocess
import sys
import socket
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8 encoding ni ta'minlash
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Rangli chiqish uchun
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

# 1-VAZIFA: ROOT CA YARATISH
def create_root_ca():
    print_header("1-VAZIFA: ROOT CA (Sertifikatlash Markazi) Yaratish")
    
    # Private key yaratish (4096-bit RSA)
    print_info("4096-bitli RSA shaxsiy kalit yaratilmoqda...")
    subprocess.run([
        'openssl', 'genrsa',
        '-out', 'certs/maqsudjon_root_ca.key',
        '4096'
    ], check=True)
    print_success("Shaxsiy kalit yaratildi: certs/maqsudjon_root_ca.key")
    
    # Root CA sertifikati yaratish (self-signed)
    print_info("Root CA sertifikati yaratilmoqda...")
    
    # Konfiguratsiya fayli
    ca_config = """
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_ca

[dn]
C = UZ
ST = Tashkent
L = Tashkent
O = MAQSUDJON Crypto Systems
OU = Security Department
CN = MAQSUDJON Root CA

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:TRUE, pathlen:0
keyUsage = critical, digitalSignature, cRLSign, keyCertSign
"""
    
    with open('certs/ca_config.cnf', 'w') as f:
        f.write(ca_config)
    
    subprocess.run([
        'openssl', 'req', '-x509', '-new', '-nodes',
        '-key', 'certs/maqsudjon_root_ca.key',
        '-sha256', '-days', '3650',
        '-out', 'certs/maqsudjon_root_ca.crt',
        '-config', 'certs/ca_config.cnf'
    ], check=True)
    print_success("Root CA sertifikati yaratildi: certs/maqsudjon_root_ca.crt")
    
    # Sertifikat ma'lumotlarini ko'rish
    print_info("Sertifikat ma'lumotlari:")
    subprocess.run([
        'openssl', 'x509', '-in', 'certs/maqsudjon_root_ca.crt',
        '-text', '-noout'
    ], check=True)
    
    print_success("\n1-VAZIFA BAJARILDI: Root CA muvaffaqiyatli yaratildi!")
    return True

# 2-VAZIFA: SERVER SERTIFIKATI
def create_server_certificate():
    print_header("2-VAZIFA: Server Sertifikatini Yaratish")
    
    # Local IP manzilni olish
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print_info(f"Local IP manzil: {local_ip}")
    
    # Server private key
    print_info("Server shaxsiy kaliti yaratilmoqda...")
    subprocess.run([
        'openssl', 'genrsa',
        '-out', 'certs/server.key',
        '2048'
    ], check=True)
    print_success("Server kaliti yaratildi: certs/server.key")
    
    # CSR konfiguratsiyasi
    server_config = f"""
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C = UZ
ST = Tashkent
L = Tashkent
O = MAQSUDJON Web Services
OU = IT Department
CN = {hostname}

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = {hostname}
DNS.2 = localhost
IP.1 = {local_ip}
IP.2 = 127.0.0.1
"""
    
    with open('certs/server_config.cnf', 'w') as f:
        f.write(server_config)
    
    # CSR yaratish
    print_info("Certificate Signing Request (CSR) yaratilmoqda...")
    subprocess.run([
        'openssl', 'req', '-new',
        '-key', 'certs/server.key',
        '-out', 'certs/server.csr',
        '-config', 'certs/server_config.cnf'
    ], check=True)
    print_success("CSR yaratildi: certs/server.csr")
    
    # Server extension konfiguratsiyasi
    server_ext = """
[server_ext]
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = """ + hostname + """
DNS.2 = localhost
IP.1 = """ + local_ip + """
IP.2 = 127.0.0.1
"""
    
    with open('certs/server_ext.cnf', 'w') as f:
        f.write(server_ext)
    
    # Root CA bilan imzolash - to'g'rilangan format
    print_info("Root CA yordamida sertifikat imzolanmoqda...")
    subprocess.run([
        'openssl', 'x509', '-req',
        '-in', 'certs/server.csr',
        '-CA', 'certs/maqsudjon_root_ca.crt',
        '-CAkey', 'certs/maqsudjon_root_ca.key',
        '-CAcreateserial',
        '-out', 'certs/server.crt',
        '-days', '365',
        '-sha256',
        '-extfile', 'certs/server_ext.cnf',
        '-extensions', 'server_ext'
    ], check=True)
    print_success("Server sertifikati yaratildi: certs/server.crt")
    
    # Tekshirish
    print_info("Sertifikat tekshirilmoqda...")
    subprocess.run([
        'openssl', 'verify',
        '-CAfile', 'certs/maqsudjon_root_ca.crt',
        'certs/server.crt'
    ], check=True)
    
    print_success("\n2-VAZIFA BAJARILDI: Server sertifikati muvaffaqiyatli yaratildi!")
    return local_ip

# 3-VAZIFA: CLIENT SERTIFIKATI
def create_client_certificate():
    print_header("3-VAZIFA: Foydalanuvchi (Mijoz) Sertifikatini Yaratish")
    
    # Client private key
    print_info("Foydalanuvchi shaxsiy kaliti yaratilmoqda...")
    subprocess.run([
        'openssl', 'genrsa',
        '-out', 'certs/client.key',
        '2048'
    ], check=True)
    print_success("Client kaliti yaratildi: certs/client.key")
    
    # Client CSR konfiguratsiyasi
    client_config = """
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn

[dn]
C = UZ
ST = Tashkent
L = Tashkent
O = MAQSUDJON Users
OU = Client Authentication
CN = MAQSUDJON Client
emailAddress = maqsudjon@example.com
"""
    
    with open('certs/client_config.cnf', 'w') as f:
        f.write(client_config)
    
    # CSR yaratish
    print_info("Client CSR yaratilmoqda...")
    subprocess.run([
        'openssl', 'req', '-new',
        '-key', 'certs/client.key',
        '-out', 'certs/client.csr',
        '-config', 'certs/client_config.cnf'
    ], check=True)
    print_success("CSR yaratildi: certs/client.csr")
    
    # Client extension
    client_ext = """
[client_ext]
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature
extendedKeyUsage = clientAuth
"""
    
    with open('certs/client_ext.cnf', 'w') as f:
        f.write(client_ext)
    
    # Root CA bilan imzolash
    print_info("Root CA yordamida imzolanmoqda...")
    subprocess.run([
        'openssl', 'x509', '-req',
        '-in', 'certs/client.csr',
        '-CA', 'certs/maqsudjon_root_ca.crt',
        '-CAkey', 'certs/maqsudjon_root_ca.key',
        '-CAcreateserial',
        '-out', 'certs/client.crt',
        '-days', '365',
        '-sha256',
        '-extfile', 'certs/client_ext.cnf',
        '-extensions', 'client_ext'
    ], check=True)
    print_success("Client sertifikati yaratildi: certs/client.crt")
    
    # PKCS#12 formatiga o'tkazish (brauzer uchun)
    print_info("PKCS#12 formatiga o'tkazilmoqda (brauzer uchun)...")
    subprocess.run([
        'openssl', 'pkcs12', '-export',
        '-out', 'certs/client.p12',
        '-inkey', 'certs/client.key',
        '-in', 'certs/client.crt',
        '-certfile', 'certs/maqsudjon_root_ca.crt',
        '-passout', 'pass:maqsudjon123'
    ], check=True)
    print_success("PKCS#12 fayl yaratildi: certs/client.p12 (parol: maqsudjon123)")
    
    print_success("\n3-VAZIFA BAJARILDI: Client sertifikati muvaffaqiyatli yaratildi!")
    return True

# 4-VAZIFA: ROOT CA NI WINDOWS GA QO'SHISH
def import_root_ca_to_windows():
    print_header("4-VAZIFA: Root CA ni Windows Trusted Root ga Qo'shish")
    
    print_info("Root CA sertifikati Windows Trusted Root Certification Authorities ga qo'shilmoqda...")
    print_info("Buning uchun Administrator huquqlari talab qilinadi!")
    
    try:
        # certutil yordamida import qilish
        subprocess.run([
            'certutil', '-addstore', 'root', 'certs\\maqsudjon_root_ca.crt'
        ], check=True, shell=True)
        print_success("Root CA muvaffaqiyatli import qilindi!")
    except subprocess.CalledProcessError as e:
        print_error(f"Import qilishda xatolik: {e}")
        print_info("Qo'lda import qilish uchun:")
        print("  1. certs\\maqsudjon_root_ca.crt faylini oching")
        print("  2. 'Install Certificate' tugmasini bosing")
        print("  3. 'Local Machine' tanlang")
        print("  4. 'Place all certificates in the following store' tanlang")
        print("  5. 'Trusted Root Certification Authorities' ni tanlang")
        print("  6. Next va Finish tugmalarini bosing")
    
    print_info("Tekshirish uchun:")
    print("  certutil -store root")
    
    print_success("\n4-VAZIFA BAJARILDI!")
    return True

if __name__ == "__main__":
    try:
        # Certs papkasini yaratish
        os.makedirs('certs', exist_ok=True)
        print_success("certs/ papkasi yaratildi")
        
        # Barcha vazifalarni bajarish
        create_root_ca()
        local_ip = create_server_certificate()
        create_client_certificate()
        import_root_ca_to_windows()
        
        print_header("BARCHA SERTIFIKATLAR YARATILDI!")
        print_info(f"Server IP manzili: {local_ip}")
        print_info("Keyingi qadam: Flask veb-serverini ishga tushirish")
        
    except Exception as e:
        print_error(f"Xatolik: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
