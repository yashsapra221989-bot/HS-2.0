"""
Flask server for Emergency Medical QR Code System
Serves the application and generates QR codes with absolute URLs
Includes SQLite database for persistent data storage
"""

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
        print(f"✅ Database initialized: {DATABASE}")

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
    """Save medical data to database"""
    try:
        data = request.json
        user_id = data.get('id') or str(uuid.uuid4())
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Convert photo to bytes if it exists
        photo_data = data.get('photo')
        
        # Check if record exists
        c.execute('SELECT id FROM medical_records WHERE id = ?', (user_id,))
        existing = c.fetchone()
        
        if existing:
            # Update existing record
            c.execute('''
                UPDATE medical_records 
                SET name = ?, blood_type = ?, allergies = ?, conditions = ?, 
                    emergency_contact = ?, photo = ?, updated_at = ?
                WHERE id = ?
            ''', (
                data.get('name', ''),
                data.get('blood', ''),
                data.get('allergy', ''),
                data.get('condition', ''),
                data.get('contact', ''),
                photo_data.encode() if photo_data else None,
                datetime.now().isoformat(),
                user_id
            ))
        else:
            # Insert new record
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
                photo_data.encode() if photo_data else None,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'user_id': user_id,
            'message': 'Medical data saved successfully'
        }
    except Exception as e:
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
        
        # Convert back to expected format
        photo_str = row[6].decode() if row[6] else None
        
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

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = int(os.environ.get('PORT', 5000))
    
    print(f"")
    print(f"{'='*60}")
    print(f"🏥 Emergency Medical QR Code Server")
    print(f"{'='*60}")
    print(f"")
    print(f"Server is running!")
    print(f"")
    print(f"📱 Access from your phone/computer:")
    print(f"   {local_ip}:{port}")
    print(f"")
    print(f"🔗 Full URL:")
    print(f"   http://{local_ip}:{port}")
    print(f"")
    print(f"📲 To scan from phone on same network:")
    print(f"   1. Open browser on phone")
    print(f"   2. Go to: http://{local_ip}:{port}")
    print(f"   3. Fill the form and generate QR code")
    print(f"   4. Scan the QR code with any phone camera/QR scanner")
    print(f"")
    print(f"{'='*60}")
    print(f"")
    
    app.run(host='0.0.0.0', port=port, debug=True)
