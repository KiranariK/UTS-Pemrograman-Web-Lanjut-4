# Cyber Incident Management API

## Ringkasan
MVP REST API untuk tim IT/Security Operation Center (SOC) dalam mencatat, memantau, dan menindaklanjuti insiden seperti phishing, malware, brute-force, akses tidak sah, dan gangguan layanan.

## Pengguna dan fitur
- Security analyst/SOC: membuat laporan dan mencatat penanganan.
- Administrator IT: mengelola pengguna dan aset.
- Auditor/koordinator: meninjau audit log.
Fitur: CRUD insiden, data pengguna/aset, catatan tindak lanjut, audit log, pencarian, filter severity/status, pagination.

## Batasan
Menggunakan data simulasi; belum ada login/JWT, otorisasi berbasis role, notifikasi, atau integrasi SIEM/EDR. Tidak melakukan scanning maupun eksploitasi. Hanya gunakan pada sistem milik sendiri/yang diizinkan.

## Stack dan MVC
Python Flask, Flask-SQLAlchemy ORM, SQLite, Flask-Migrate. `models/` mengelola entitas, `controllers/` menangani endpoint dan logika aplikasi, `run.py` menjalankan aplikasi.

## Instalasi
```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
flask --app run.py seed
flask --app run.py run --debug
```
API: http://127.0.0.1:5000 ; health: GET `/api/v1/health`.

## Database / ERD
Ada lima tabel relevan: `users`, `assets`, `incidents`, `incident_updates`, `audit_logs`. FK: incidents.user_id -> users.id; incidents.asset_id -> assets.id; incident_updates.incident_id -> incidents.id; audit_logs.incident_id -> incidents.id. ERD berada di `docs/erd.mmd`.

## Endpoint
| Method | Endpoint | Fungsi |
|---|---|---|
| GET/POST | /api/v1/users | daftar/buat pengguna |
| GET/POST | /api/v1/assets | daftar/buat aset |
| GET/POST | /api/v1/incidents | cari/daftar/buat insiden |
| GET/PATCH/DELETE | /api/v1/incidents/{id} | detail/ubah/hapus |
| GET/POST | /api/v1/incidents/{id}/updates | riwayat/tambah tindak lanjut |
| GET | /api/v1/audit-logs | audit log |
| GET | /api/v1/health | health check |

Dokumentasi API: `docs/openapi.yaml`.

## Contoh request
Buat user: `{"name":"Dina","email":"dina@example.com","role":"analyst"}`
Buat aset: `{"asset_name":"Web Server","asset_type":"server","ip_address":"192.0.2.10","criticality":"high"}`
Buat insiden (isi ID dari response user dan aset):
```json
{"title":"Percobaan brute force","description":"Login gagal berulang","incident_type":"brute_force","severity":"high","source_ip":"198.51.100.25","user_id":1,"asset_id":1}
```
Cari: `GET /api/v1/incidents?search=login&severity=high&status=open&page=1&per_page=10`.
Response sukses menggunakan `{"success":true,"data":...}`. Error konsisten: `{"success":false,"error":{"code":"VALIDATION_ERROR","message":"..."}}`.

## Automated test
`pytest -q`. Test menguji pembuatan insiden berhasil, validasi field wajib, serta pencarian dan pagination.

## Migration / seed
Inisialisasi lokal menggunakan perintah `init-db` dan `seed`. Untuk migration versioned: `flask --app run.py db init`, `flask --app run.py db migrate -m "initial schema"`, `flask --app run.py db upgrade`.

## Keamanan
Validasi field dan enum, email unik, pemeriksaan relasi FK, pagination maksimum 100, konfigurasi secret melalui environment, error response tanpa stack trace. Sebelum produksi tambahkan JWT, RBAC, rate limiting, HTTPS, backup, audit retention, dan manajemen secret.

## Rencana UAS
1. JWT dan role admin/analyst/auditor.
2. Swagger UI dan deployment.
3. Notifikasi webhook/email untuk insiden critical.
4. Dashboard tren insiden dan SLA.
5. Integrasi data simulasi SIEM/EDR.
6. Optimasi query, backup, dan security testing terotorisasi.

## Publikasi GitHub
```bash
git init
git add .
git commit -m "chore: initial project structure"
git add app/models && git commit -m "feat: add relational models"
git add app/controllers tests docs README.md && git commit -m "feat: implement API and tests"
git tag v1.0
git remote add origin https://github.com/USERNAME/cyber-incident-management-api.git
git push -u origin main --tags
```
Ganti `USERNAME` dengan akun GitHub. URL demo baru tersedia setelah deploy ke hosting yang mendukung Flask.
