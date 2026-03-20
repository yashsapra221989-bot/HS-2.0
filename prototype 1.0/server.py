"""
Flask server for Emergency Medical QR Code System
Serves the application and generates QR codes with absolute URLs
Includes SQLite database for persistent data storage
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, render_template_string, request, send_file
import json
import os
import socket
import qrcode
import sqlite3
import uuid
from io import BytesIO
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
DATABASE = 'medical_data.db'

# Initialize database
def init_db():
    """Initialize SQLite database with medical_records table"""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE medical_records (
                id TEXT PRIMARY KEY,
                name TEXT,
                blood_type TEXT,
                allergies TEXT,
                conditions TEXT,
                emergency_contact TEXT,
                photo BLOB,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
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

@app.route('/')
def index():
    """Serve the main form page"""
    with open('sync.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/qr.html')
def qr_page():
    """Serve the QR display page"""
    with open('qr.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/viewer.html')
def viewer_page():
    """Serve the viewer page"""
    with open('viewer.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/save-medical-data', methods=['POST'])
def save_medical_data():
    """Save medical data to database (photos not stored)"""
    try:
        data = request.json
        user_id = data.get('id') or str(uuid.uuid4())
        
        print(f"[SAVE] Saving data for user: {user_id} (photo excluded)")
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if record exists
        c.execute('SELECT id FROM medical_records WHERE id = ?', (user_id,))
        existing = c.fetchone()
        
        if existing:
            print(f"[SAVE] Updating existing record for {user_id}")
            # Update existing record - NO PHOTO STORAGE
            c.execute('''
                UPDATE medical_records 
                SET name = ?, blood_type = ?, allergies = ?, conditions = ?, 
                    emergency_contact = ?, photo = NULL, updated_at = ?
                WHERE id = ?
            ''', (
                data.get('name', ''),
                data.get('blood', ''),
                data.get('allergy', ''),
                data.get('condition', ''),
                data.get('contact', ''),
                datetime.now().isoformat(),
                user_id
            ))
        else:
            print(f"[SAVE] Creating new record for {user_id}")
            # Insert new record - NO PHOTO STORAGE
            c.execute('''
                INSERT INTO medical_records 
                (id, name, blood_type, allergies, conditions, emergency_contact, photo, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('name', ''),
                data.get('blood', ''),
                data.get('allergy', ''),
                data.get('condition', ''),
                data.get('contact', ''),
                None,  # Photo is NULL
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print(f"[SAVE] Successfully saved data for {user_id} (photo not stored)")
        
        return {
            'success': True,
            'user_id': user_id,
            'message': 'Medical data saved successfully (photo stored locally only)'
        }
    except Exception as e:
        import traceback
        print(f"[SAVE] Error: {e}")
        print(f"[SAVE] Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e)
        }, 500

@app.route('/api/get-medical-data/<user_id>', methods=['GET'])
def get_medical_data(user_id):
    """Retrieve medical data from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, name, blood_type, allergies, conditions, emergency_contact, photo, updated_at
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
            'updated_at': row[7]
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
    """Generate a QR code with absolute URL pointing to viewer.html"""
    try:
        data = request.json
        
        # Get local IP and port
        local_ip = get_local_ip()
        port = os.environ.get('PORT', 5000)
        
        # Create absolute URL with encoded data
        import base64
        medical_data = json.dumps(data)
        encoded_data = base64.b64encode(medical_data.encode()).decode()
        viewer_url = f"http://{local_ip}:{port}/viewer.html?data={encoded_data}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(viewer_url)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        img_io = BytesIO()
        qr_image.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Convert to base64 for embedding
        import base64 as b64
        img_base64 = b64.b64encode(img_io.getvalue()).decode()
        
        return {
            'success': True,
            'qr_image': f"data:image/png;base64,{img_base64}",
            'qr_url': viewer_url,
            'local_ip': local_ip,
            'port': port
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }, 500

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

@app.route('/script.js')
def serve_script():
    """Serve the JavaScript file"""
    with open('script.js', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

@app.route('/dashboard.html')
def dashboard_page():
    """Serve the dashboard page"""
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/all-records', methods=['GET'])
def all_records():
    """Get all medical records from database"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, name, blood_type, allergies, conditions, emergency_contact, photo, created_at, updated_at
            FROM medical_records
            ORDER BY updated_at DESC
        ''')
        
        records = c.fetchall()
        conn.close()
        
        # Convert records to list of lists, excluding photo data for the list view
        simplified_records = []
        for record in records:
            # Return all fields except photo for the list (photo is too large)
            simplified_records.append([
                record[0],  # id
                record[1],  # name
                record[2],  # blood_type
                record[3],  # allergies
                record[4],  # conditions
                record[5],  # emergency_contact
                'Yes' if record[6] else 'No',  # photo (boolean string)
                record[7],  # created_at
                record[8]   # updated_at
            ])
        
        return {
            'success': True,
            'count': len(simplified_records),
            'records': simplified_records
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
    
    app.run(host='0.0.0.0', port=port, debug=True)
