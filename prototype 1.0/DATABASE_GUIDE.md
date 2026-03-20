# Database Integration Guide

## Overview
Your Medical QR Code application now includes **SQLite database** integration for persistent data storage. Instead of only storing data in browser localStorage, user data is now automatically saved to a server-side database.

## Database Features

### ✅ What's New

1. **Automatic Data Persistence** - User medical information is saved to `medical_data.db`
2. **Server-Side Storage** - Data survives browser cache clearing
3. **User Tracking** - Each user gets a unique ID (`userId`)
4. **Photo Storage** - Captured photos are stored in the database
5. **Timestamp Tracking** - Records creation and update times

### Database Schema

The database includes a `medical_records` table with:

```
- id (TEXT, PRIMARY KEY)           : Unique user ID
- name (TEXT)                      : User's full name
- blood_type (TEXT)                : Blood type
- allergies (TEXT)                 : Allergies information
- conditions (TEXT)                : Medical conditions
- emergency_contact (TEXT)         : Emergency contact info
- photo (BLOB)                     : Captured photo (base64 encoded)
- created_at (TIMESTAMP)           : Record creation time
- updated_at (TIMESTAMP)           : Last update time
```

## API Endpoints

### 1. Save Medical Data
**Endpoint:** `POST /api/save-medical-data`

**Request Body:**
```json
{
  "id": "user_1710123456_abc123",
  "name": "John Doe",
  "blood": "O+",
  "allergy": "Penicillin",
  "condition": "Asthma",
  "contact": "555-1234",
  "photo": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user_1710123456_abc123",
  "message": "Medical data saved successfully"
}
```

### 2. Retrieve Medical Data
**Endpoint:** `GET /api/get-medical-data/<user_id>`

**Response:**
```json
{
  "success": true,
  "id": "user_1710123456_abc123",
  "name": "John Doe",
  "blood": "O+",
  "allergy": "Penicillin",
  "condition": "Asthma",
  "contact": "555-1234",
  "photo": "data:image/jpeg;base64,...",
  "updated_at": "2024-03-11T10:30:45.123456"
}
```

## How It Works

### Data Flow

1. **Form Entry** - User fills out medical information
2. **Photo Capture** - User takes/uploads photo
3. **Auto-Save** - When user clicks "Generate QR Code"
   - Data is saved to localStorage (browser cache)
   - **NEW:** Data is also sent to server and saved to database
4. **User ID** - A unique `userId` is generated and stored locally
5. **Database Storage** - Server stores all data with timestamp

### User ID Generation

- First time users: A unique ID is generated automatically
  - Format: `user_<timestamp>_<random>`
  - Example: `user_1710123456_abc123xyz`
- Subsequent visits: The same ID is reused (stored in localStorage)

## Usage in JavaScript

### Automatic Usage
The database integration is **automatic**. When users click "Generate QR Code":

```javascript
// This happens automatically:
1. Forms values are collected
2. Photo is included
3. saveMedicalDataToServer() is called
4. Data is sent to /api/save-medical-data
5. Response confirms storage
6. User is redirected to QR page
```

### Manual Database Operations

You can manually retrieve data from the server:

```javascript
// Fetch saved user data from database
async function loadUserDataFromServer(userId) {
    const response = await fetch(`/api/get-medical-data/${userId}`);
    const result = await response.json();
    
    if (result.success) {
        return result;  // Contains all saved medical data
    } else {
        console.error('Data not found:', result.error);
    }
}

// Use it:
const userData = await loadUserDataFromServer(userId);
console.log(userData.name, userData.blood);
```

## Database File

- **Location:** `medical_data.db` (in the same directory as `server.py`)
- **Type:** SQLite 3
- **Automatic Creation:** Database is created automatically on first run
- **Size:** Very small and portable

## Viewing Database Data

### Option 1: SQLite Browser
Download [DB Browser for SQLite](https://sqlitebrowser.org/) and open `medical_data.db`

### Option 2: Command Line
```bash
# List all records
sqlite3 medical_data.db "SELECT id, name, blood_type, created_at FROM medical_records;"

# View specific user
sqlite3 medical_data.db "SELECT * FROM medical_records WHERE id='user_1710123456_abc123';"
```

### Option 3: Python Script
```python
import sqlite3

conn = sqlite3.connect('medical_data.db')
c = conn.cursor()

# Get all records
c.execute("SELECT id, name, blood_type, updated_at FROM medical_records")
for row in c.fetchall():
    print(row)

conn.close()
```

## Data Backup & Recovery

### Backup Database
```bash
# Simple file copy
cp medical_data.db medical_data_backup.db

# Or compress it
zip medical_data_backup.zip medical_data.db
```

### Restore from Backup
```bash
cp medical_data_backup.db medical_data.db
```

## Security Considerations

⚠️ **Current Implementation Notes:**
- Data is stored in plain text (no encryption)
- Photo data is base64 encoded
- For production use, consider:
  - HTTPS encryption
  - Database user authentication
  - Input validation & sanitization
  - Regular backups
  - Privacy policy compliance

## Troubleshooting

### Database Not Found Error
- Check that `server.py` is running
- Verify `medical_data.db` exists in your project directory
- Restart the Flask server

### Data Not Saving
- Check browser console for errors (F12)
- Verify server is running on correct port
- Check network tab to see API requests
- Look for error messages in server terminal

### Large Database Size
- Photos take up space. To optimize:
  - Reduce photo quality
  - Add photo compression
  - Archive old records

## Advanced: Custom Queries

Add these functions to `server.py` for additional features:

### Get All Records
```python
@app.route('/api/all-records', methods=['GET'])
def get_all_records():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, name, blood_type, updated_at FROM medical_records")
    records = c.fetchall()
    conn.close()
    return {'success': True, 'records': records}
```

### Delete Record
```python
@app.route('/api/delete-medical-data/<user_id>', methods=['DELETE'])
def delete_medical_data(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM medical_records WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {'success': True, 'message': 'Record deleted'}
```

### Export to JSON
```python
import json

@app.route('/api/export-data', methods=['GET'])
def export_data():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM medical_records")
    columns = [col[0] for col in c.description]
    data = [dict(zip(columns, row)) for row in c.fetchall()]
    conn.close()
    return json.dumps(data, indent=2)
```

## Summary

Your application now has:
✅ Database for persistent storage
✅ Automatic data saving
✅ User tracking via unique IDs
✅ API endpoints for data retrieval
✅ Photo storage capability

Users can rely on their data being saved securely on the server, not just in browser cache!
