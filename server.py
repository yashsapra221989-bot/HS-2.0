"""
Flask server for Emergency Medical QR Code System
Serves the application and generates QR codes with absolute URLs
Includes SQLite database for persistent data storage
"""

import os
import socket
import sqlite3
import uuid
import hashlib
from datetime import datetime

from flask import Flask, request

app = Flask(__name__, static_folder='public', static_url_path='')

def hash_password(password: str) -> str:
    """Hash password with SHA-256. For production use bcrypt instead."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# ✅ FIX: Handle CORS preflight OPTIONS requests explicitly.
# Without this, browsers block cross-origin requests before they reach the route handler.
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 204
DATABASE = 'medical_data.db'

# NOTE FOR NETLIFY: SQLite will NOT persist data on Netlify. 
# You must switch to a cloud database (e.g., Supabase/PostgreSQL).
# Example change for Supabase:
# import os
# import psycopg2
# DATABASE_URL = os.environ.get('DATABASE_URL')
# conn = psycopg2.connect(DATABASE_URL)

# Initialize database
def init_db():
    """Initialize SQLite database with medical_records and users tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Medical records table
    c.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id TEXT PRIMARY KEY,
            name TEXT,
            blood_type TEXT,
            allergies TEXT,
            conditions TEXT,
            emergency_contact TEXT,
            photo BLOB,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            dob TEXT,
            gender TEXT,
            weight TEXT,
            height TEXT,
            abha TEXT,
            meds TEXT,
            surgeries TEXT,
            ecName TEXT,
            ecRel TEXT,
            doctor TEXT
        )
    ''')
    # SOS Alerts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            lat REAL,
            lon REAL,
            resolved INTEGER DEFAULT 0,
            manual_location TEXT
        )
    ''')
    try:
        c.execute('ALTER TABLE sos_alerts ADD COLUMN manual_location TEXT')
    except Exception:
        pass
    # Users table for account credentials
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[DATABASE] Initialized: {DATABASE}")

# Initialize database on startup
init_db()

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Connect to external host to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Note: On Netlify, static routes are handled by the 'public' directory.
# The exact same logic is replicated here for local testing.
@app.route('/')
def index():
    return app.send_static_file('landing.html')

@app.route('/<path:path>')
def static_proxy(path):
    # Only serve known static files, otherwise bypass to other routes or 404
    if path.endswith('.html') or path.endswith('.js') or path.endswith('.css'):
        try:
            return app.send_static_file(path)
        except Exception:
            pass
    return {'error': 'Not found'}, 404

@app.route('/api/save-medical-data', methods=['POST'])
def save_medical_data():
    """Save medical data to database (photos not stored)"""
    try:
        data = request.json
        user_id = data.get('id') or str(uuid.uuid4())
        password = data.get('password')  # Optional: from registration form

        print(f"[SAVE] Saving data for user: {user_id} (photo excluded)")

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # If password provided, upsert user account
        if password:
            c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            user_exists = c.fetchone()
            if user_exists:
                # ✅ FIX: store hashed password
                c.execute('UPDATE users SET password = ? WHERE user_id = ?', (hash_password(password), user_id))
            else:
                c.execute(
                    'INSERT INTO users (user_id, password, created_at) VALUES (?, ?, ?)',
                    (user_id, hash_password(password), datetime.now().isoformat())
                )

        # Check if medical record exists
        c.execute('SELECT id FROM medical_records WHERE id = ?', (user_id,))
        existing = c.fetchone()

        if existing:
            print(f"[SAVE] Updating existing record for {user_id}")
            c.execute('''
                UPDATE medical_records
                SET name = ?, blood_type = ?, allergies = ?, conditions = ?,
                    emergency_contact = ?, photo = NULL, updated_at = ?,
                    dob = ?, gender = ?, weight = ?, height = ?, abha = ?,
                    meds = ?, surgeries = ?, ecName = ?, ecRel = ?, doctor = ?
                WHERE id = ?
            ''', (
                data.get('name', ''),
                data.get('blood', ''),
                data.get('allergy', ''),
                data.get('condition', ''),
                data.get('contact', ''),
                datetime.now().isoformat(),
                data.get('dob', ''),
                data.get('gender', ''),
                data.get('weight', ''),
                data.get('height', ''),
                data.get('abha', ''),
                data.get('meds', ''),
                data.get('surgeries', ''),
                data.get('ecName', ''),
                data.get('ecRel', ''),
                data.get('doctor', ''),
                user_id
            ))
        else:
            print(f"[SAVE] Creating new record for {user_id}")
            c.execute('''
                INSERT INTO medical_records
                (id, name, blood_type, allergies, conditions, emergency_contact, photo, created_at, updated_at, dob, gender, weight, height, abha, meds, surgeries, ecName, ecRel, doctor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('name', ''),
                data.get('blood', ''),
                data.get('allergy', ''),
                data.get('condition', ''),
                data.get('contact', ''),
                None,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                data.get('dob', ''),
                data.get('gender', ''),
                data.get('weight', ''),
                data.get('height', ''),
                data.get('abha', ''),
                data.get('meds', ''),
                data.get('surgeries', ''),
                data.get('ecName', ''),
                data.get('ecRel', ''),
                data.get('doctor', '')
            ))

        conn.commit()
        conn.close()

        print(f"[SAVE] Successfully saved data for {user_id}")
        return {
            'success': True,
            'user_id': user_id,
            'message': 'Medical data saved successfully'
        }
    except Exception as e:
        import traceback
        print(f"[SAVE] Error: {e}")
        print(f"[SAVE] Traceback: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}, 500


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user account with credentials and medical data"""
    try:
        data = request.json
        user_id  = (data.get('user_id') or '').strip()
        password = (data.get('password') or '').strip()
        name     = (data.get('name') or '').strip()

        if not user_id or not password or not name:
            return {'success': False, 'error': 'user_id, password, and name are required'}, 400
        if len(user_id) < 3:
            return {'success': False, 'error': 'User ID must be at least 3 characters'}, 400
        if len(password) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}, 400

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # Check user ID not already taken
        c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if c.fetchone():
            conn.close()
            return {'success': False, 'error': 'User ID already taken'}, 409

        now = datetime.now().isoformat()

        # Create user account — store hashed password, never plaintext
        c.execute('INSERT INTO users (user_id, password, created_at) VALUES (?, ?, ?)',
                  (user_id, hash_password(password), now))

        # Create medical record
        c.execute('''
            INSERT INTO medical_records
            (id, name, blood_type, allergies, conditions, emergency_contact, photo, created_at, updated_at, dob, gender, weight, height, abha, meds, surgeries, ecName, ecRel, doctor)
            VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, '', '', '', '', '', '', '', '', '', '')
        ''', (
            user_id,
            name,
            data.get('blood', ''),
            data.get('allergy', ''),
            data.get('condition', ''),
            data.get('contact', ''),
            now, now
        ))

        conn.commit()
        conn.close()

        print(f"[REGISTER] New account created: {user_id}")
        return {'success': True, 'user_id': user_id, 'message': 'Account created successfully'}
    except Exception as e:
        import traceback
        print(f"[REGISTER] Error: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}, 500


@app.route('/api/login', methods=['POST'])
def login():
    """Verify user credentials against the database"""
    try:
        data     = request.json
        user_id  = (data.get('user_id') or '').strip()
        password = (data.get('password') or '')

        if not user_id or not password:
            return {'success': False, 'error': 'user_id and password required'}, 400

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()

        if not row:
            return {'success': False, 'error': 'User ID not found'}, 401
        # ✅ FIX: Compare hashed password, not plaintext
        if row[0] != hash_password(password):
            return {'success': False, 'error': 'Incorrect password'}, 401

        return {'success': True, 'user_id': user_id, 'message': 'Login successful'}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/api/get-medical-data/<user_id>', methods=['GET'])
def get_medical_data(user_id):
    """Retrieve medical data from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, name, blood_type, allergies, conditions, emergency_contact, photo, updated_at,
                   dob, gender, weight, height, abha, meds, surgeries, ecName, ecRel, doctor
            FROM medical_records WHERE id = ?
        ''', (user_id,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return {
                'success': False,
                'error': 'Record not found'
            }, 404
        
        # Convert photo back to string if it exists
        photo_str = None
        if row[6]:
            if isinstance(row[6], bytes):
                photo_str = row[6].decode('utf-8')
            else:
                photo_str = row[6]
        
        return {
            'success': True,
            'id': row[0],
            'name': row[1],
            'blood': row[2],
            'allergy': row[3],
            'condition': row[4],
            'contact': row[5],
            'photo': photo_str,
            'updated_at': row[7],
            'dob': row[8],
            'gender': row[9],
            'weight': row[10],
            'height': row[11],
            'abha': row[12],
            'meds': row[13],
            'surgeries': row[14],
            'ecName': row[15],
            'ecRel': row[16],
            'doctor': row[17]
        }
    except Exception as e:
        import traceback
        print(f"Error in get_medical_data: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }, 500

@app.route('/api/generate-qr-url', methods=['POST'])
def generate_qr_url():
    """Generate a short QR URL using only the user ID — keeps QR simple and scannable"""
    try:
        data = request.json
        user_id = data.get('id')

        if not user_id:
            return {'success': False, 'error': 'No user ID provided'}, 400

        local_ip = get_local_ip()
        port = os.environ.get('PORT', 5000)

        # SHORT URL — only the user ID, no embedded data
        viewer_url = f"http://{local_ip}:{port}/viewer.html?id={user_id}"

        return {
            'success': True,
            'qr_url': viewer_url,
            'local_ip': local_ip,
            'port': port
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/api/get-connection-info')
def get_connection_info():
    """Get connection info for display"""
    local_ip = get_local_ip()
    port = os.environ.get('PORT', 5000)
    return {
        'local_ip': local_ip,
        'port': port,
        'url': f"http://{local_ip}:{port}"
    }

# Note: script.js, sync.html, dashboard.html are also handled by static hosting.

@app.route('/api/all-records', methods=['GET'])
def all_records():
    """Get all medical records from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, name, blood_type, allergies, conditions, emergency_contact, photo, updated_at,
                   dob, gender, weight, height, abha, meds, surgeries, ecName, ecRel, doctor
            FROM medical_records
            ORDER BY updated_at DESC
        ''')
        
        records = c.fetchall()
        conn.close()
        
        # Convert records to list of dictionaries matching the frontend needs
        patient_list = []
        for row in records:
            # We skip photo for the list view to save bandwidth
            patient_list.append({
                'id': row[0],
                'name': row[1],
                'blood': row[2],
                'allergies': [s.strip() for s in row[3].split(',')] if row[3] else [],
                'conditions': [s.strip() for s in row[4].split(',')] if row[4] else [],
                'ecPhone': row[5],
                'updated_at': row[7],
                'dob': row[8],
                'gender': row[9],
                'weight': row[10],
                'height': row[11],
                'abha': row[12],
                'meds': [s.strip() for s in row[13].split(',')] if row[13] else [],
                'surgeries': row[14],
                'ecName': row[15],
                'ecRel': row[16],
                'doctor': row[17],
                'medComplete': True
            })
        
        return {
            'success': True,
            'count': len(patient_list),
            'records': patient_list
        }
    except Exception as e:
        import traceback
        print(f"Error in all_records: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }, 500

@app.route('/api/delete-medical-data/<user_id>', methods=['DELETE'])
def delete_medical_data(user_id):
    """Delete a medical record from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if record exists first
        c.execute('SELECT name FROM medical_records WHERE id = ?', (user_id,))
        record = c.fetchone()
        
        if not record:
            conn.close()
            return {
                'success': False,
                'error': 'Record not found'
            }, 404
        
        # Delete the record
        c.execute('DELETE FROM medical_records WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f'Record for {record[0]} deleted successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500

@app.route('/api/sos-alert', methods=['POST'])
def sos_alert():
    """Receive an SOS alert with optional GPS coordinates"""
    try:
        data = request.json
        timestamp = data.get('timestamp', datetime.now().isoformat())
        lat = data.get('lat')
        lon = data.get('lon')
        manual_loc = data.get('manual_location', '')

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO sos_alerts (timestamp, lat, lon, resolved, manual_location)
            VALUES (?, ?, ?, 0, ?)
        ''', (timestamp, lat, lon, manual_loc))
        conn.commit()
        conn.close()

        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/api/get-sos-alerts', methods=['GET'])
def get_sos_alerts():
    """Get active unresolved SOS alerts for the dashboard"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT id, timestamp, lat, lon, manual_location FROM sos_alerts WHERE resolved = 0 ORDER BY timestamp DESC')
        records = c.fetchall()
        conn.close()

        alerts = [
            {'id': r[0], 'timestamp': r[1], 'lat': r[2], 'lon': r[3], 'manual_location': r[4]}
            for r in records
        ]
        return {'success': True, 'alerts': alerts}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/api/resolve-sos-alert/<int:alert_id>', methods=['POST'])
def resolve_sos_alert(alert_id):
    """Mark an SOS alert as resolved"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('UPDATE sos_alerts SET resolved = 1 WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

# Note: The if __name__ == '__main__': block is only for local testing.
if __name__ == '__main__':
    local_ip = get_local_ip()
    port = int(os.environ.get('PORT', 5000))
    
    print(f"")
    print(f"{'='*60}")
    print(f"[HOSPITAL] Emergency Medical QR Code Server")
    print(f"{'='*60}")
    print(f"")
    print(f"Server is running!")
    print(f"")
    print(f"[PHONE] Access from your phone/computer:")
    print(f"   {local_ip}:{port}")
    print(f"")
    print(f"[URL] Full URL:")
    print(f"   http://{local_ip}:{port}")
    print(f"")
    print(f"[QR] To scan from phone on same network:")
    print(f"   1. Open browser on phone")
    print(f"   2. Go to: http://{local_ip}:{port}")
    print(f"   3. Fill the form and generate QR code")
    print(f"   4. Scan the QR code with any phone camera/QR scanner")
    print(f"")
    print(f"{'='*60}")
    print(f"")
    
    # ✅ FIX: Never run with debug=True in production — it exposes a remote code execution console.
    # Set DEBUG=1 env var only for local development.
    debug_mode = os.environ.get('DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)