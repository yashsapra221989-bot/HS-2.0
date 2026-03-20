# Emergency QR Medical ID - Web Application

This is a web-based application for managing medical information and generating scannable QR codes for emergency situations. The system allows emergency responders to scan a QR code and immediately access critical medical data in a structured format.

## Features

✓ **Web-Based Application** - Works on any browser (desktop/mobile)  
✓ **Real-time Form Validation** - Visual feedback as you fill information  
✓ **Photo Capture** - Capture photo from webcam (desktop only)  
✓ **QR Code Generation** - Creates scannable QR codes with encoded medical data  
✓ **Mobile Scanning** - Scan QR code on phone to view medical information  
✓ **PDF Download** - Download medical information as a PDF  
✓ **Data Persistence** - Auto-saves form data using localStorage  
✓ **Responsive Design** - Works on all devices  

## System Architecture

```
sync.html          → Main form to enter medical information
   ↓ (generate QR)
qr.html            → Display and download QR codes
   ↓ (encoded URL in QR)
viewer.html        → Display medical data when QR is scanned
   ↓ (download option)
PDF Document       → Downloadable medical record
```

## Requirements

- Python 3.7+
- Flask (for running local server)
- QR Code library
- Pillow (image processing)

## Installation & Setup

### Step 1: Install Python
Download from [python.org](https://www.python.org/downloads/)

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start the Flask Server
```bash
python server.py
```

You should see output like:
```
============================================================
🏥 Emergency Medical QR Code Server
============================================================

Server is running!

📱 Access from your phone/computer:
   192.168.1.100:5000

🔗 Full URL:
   http://192.168.1.100:5000

📲 To scan from phone on same network:
   1. Open browser on phone
   2. Go to: http://192.168.1.100:5000
   3. Fill the form and generate QR code
   4. Scan the QR code with any phone camera/QR scanner

============================================================
```

### Step 4: Access the Application

**On your desktop:**
- Open browser and go to: `http://localhost:5000`

**On your phone (same WiFi network):**
- Open browser and go to: `http://<your-computer-ip>:5000`
- Replace `<your-computer-ip>` with the IP shown when you start the server

## How to Use

### 1. Create Medical Profile
- Go to `http://localhost:5000` (or your phone's URL)
- Fill in your medical information:
  - Name
  - Blood Type
  - Allergies (Critical!)
  - Medical Conditions
  - Emergency Contact
- Form auto-saves as you type

### 2. Capture Photo (Desktop Only)
- Click "Capture Photo"
- Allow camera access
- Click to capture your photo

### 3. Generate QR Code
- Click "Generate QR Code"
- QR code will be displayed with your medical information

### 4. Scan QR Code
**From another phone:**
- Open Camera app (most modern phones scan QR automatically)
- Point at QR code
- Tap notification to open viewer
- View complete medical information
- Download as PDF if needed

**From QR Scanner app:**
- Any standard QR code scanner will work

### 5. Download as PDF
- After scanning QR code, click "Download PDF"
- Medical record saved as `Medical_Information.pdf`

## File Structure

```
sync.html           - Medical information form (main entry point)
qr.html             - QR code display and download page
viewer.html         - QR code scanning result page
script.js           - Form logic and validation
server.py           - Flask server for network access
requirements.txt    - Python dependencies
README.md           - This file
```

## Troubleshooting

### "Server not running" error
- Make sure Flask server is started: `python server.py`
- Check that port 5000 is not in use

### QR code not scanning on phone
- Ensure phone is on same WiFi network as computer
- Try using native camera app (usually works best)
- If URL shows `127.0.0.1`, use computer's local IP instead
- Make sure Flask server is running and displaying the IP correctly

### Can't access from phone
- Verify both devices are on same network
- Check firewall settings (may need to allow Python)
- Get the correct IP from server startup message
- Try: `http://<your-ip>:5000`

### Photo capture not working
- Only works on HTTPS or localhost
- Not available on phone browsers (use desktop for photo)
- Check camera permissions in browser settings

### PDF download not working
- Ensure JavaScript is enabled in browser
- Try a different browser (Chrome/Firefox recommended)
- Check if popup blockers are preventing download

## Network Setup Notes

**Finding Your Computer's IP Address:**

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your WiFi connection

**Mac/Linux:**
```bash
ifconfig
```
Look for the IP address under your WiFi interface

**Example:**
- Server shows: `192.168.1.100:5000`
- On phone browser, go to: `http://192.168.1.100:5000`

## Security Notes

- Data is stored locally in browser (localStorage)
- QR codes encode data in URL - treat as sensitive
- PDF downloads contain medical information - keep secure
- Only share QR codes with trusted persons/services
- Consider using HTTPS for production deployment

## Deployment

For production use with external access:
1. Use a cloud hosting service (Heroku, AWS, Google Cloud, etc.)
2. Set up a proper domain name
3. Install SSL certificates for HTTPS
4. Configure environment variables for security
5. Use a production WSGI server (Gunicorn, uWSGI)

## Support

Common issues and solutions are covered in Troubleshooting section above.

## License

This project is for emergency medical identification purposes.


