// script.js - JavaScript for Emergency QR Medical ID

let stream = null;
let photoTaken = false;
let userId = null;  // User ID for database tracking

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// Initialize or retrieve user ID
function initializeUserId() {
    userId = localStorage.getItem('userId');
    if (!userId) {
        // Generate a new user ID if one doesn't exist
        userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('userId', userId);
        console.log('New User ID created:', userId);
    } else {
        console.log('Existing User ID:', userId);
    }
}

// Update progress bar
function updateProgressBar() {
    const name = document.getElementById('name').value.trim();
    const blood = document.getElementById('blood').value.trim();
    const allergy = document.getElementById('allergy').value.trim();
    const condition = document.getElementById('condition').value.trim();
    const contact = document.getElementById('contact').value.trim();
    
    let progress = 0;
    if (name) progress += 20;
    if (blood) progress += 15;
    if (allergy) progress += 15;
    if (condition) progress += 15;
    if (contact) progress += 15;
    if (photoTaken) progress += 20;
    
    document.getElementById('progressBar').style.width = progress + '%';
}

// Save medical data to server database
async function saveMedicalDataToServer() {
    try {
        const photo = document.getElementById('photo');
        const medicalData = {
            id: userId,
            name: document.getElementById('name').value.trim(),
            blood: document.getElementById('blood').value.trim(),
            allergy: document.getElementById('allergy').value.trim(),
            condition: document.getElementById('condition').value.trim(),
            contact: document.getElementById('contact').value.trim(),
            photo: photo.src
        };

        const response = await fetch('/api/save-medical-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(medicalData)
        });

        const result = await response.json();
        
        if (result.success) {
            console.log('Medical data saved to database:', result.user_id);
            localStorage.setItem('userId', result.user_id);
            userId = result.user_id;
            return true;
        } else {
            console.error('Failed to save data:', result.error);
            showToast('Warning: Could not save to database, but continuing...', 'warning');
            return false;
        }
    } catch (error) {
        console.error('Error saving to database:', error);
        showToast('Warning: Database save failed, but continuing...', 'warning');
        return false;
    }
}

// Real-time input validation
function setupInputValidation() {
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            updateProgressBar();
            validateField(this);
        });
    });
}

function validateField(input) {
    const value = input.value.trim();
    const statusId = input.id + 'Status';
    const statusEl = document.getElementById(statusId);
    
    if (!statusEl) return;
    
    if (value.length > 0) {
        input.classList.remove('invalid');
        input.classList.add('valid');
        statusEl.textContent = '✓ Complete';
        statusEl.classList.remove('invalid');
        statusEl.classList.add('valid');
    } else {
        input.classList.remove('valid');
        input.classList.add('invalid');
        statusEl.textContent = '';
        statusEl.classList.remove('valid');
        statusEl.classList.add('invalid');
    }
}

// Load saved data from localStorage on page load
window.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    initializeUserId();  // Initialize user ID
    setupInputValidation();
    loadSavedData();
    
    // Delay camera initialization to ensure DOM is fully ready
    setTimeout(() => {
        console.log('Starting camera initialization...');
        startCamera();
    }, 500);
});

function loadSavedData() {
    const savedData = localStorage.getItem('medicalData');
    if (savedData) {
        const data = JSON.parse(savedData);
        document.getElementById('name').value = data.name || '';
        document.getElementById('blood').value = data.blood || '';
        document.getElementById('allergy').value = data.allergy || '';
        document.getElementById('condition').value = data.condition || '';
        document.getElementById('contact').value = data.contact || '';
        
        // Load saved photo
        const savedPhoto = localStorage.getItem('medicalPhoto');
        if (savedPhoto) {
            document.getElementById('photo').src = savedPhoto;
            document.getElementById('photo').style.display = 'block';
            document.getElementById('video').style.display = 'none';
            document.getElementById('captureBtn').style.display = 'none';
            photoTaken = true;
            showPhotoBadge();
            updateProgressBar();
        }
    }
    validateAllFields();
}

function validateAllFields() {
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => validateField(input));
}

async function startCamera() {
    try {
        console.log('startCamera() called');
        
        // Check if already using camera (if photo already captured)
        const savedPhoto = localStorage.getItem('medicalPhoto');
        if (savedPhoto) {
            console.log('Photo already exists, skipping camera');
            document.getElementById('retakeBtn').style.display = 'inline-block';
            return;
        }

        console.log('Checking for video element...');
        const video = document.getElementById('video');
        
        if (!video) {
            console.error('Video element not found in DOM');
            showToast('Video element not found!', 'error');
            return;
        }

        console.log('Video element found:', video);

        // Stop any existing streams
        if (stream) {
            console.log('Stopping existing stream');
            stream.getTracks().forEach(track => track.stop());
        }

        // Request camera access with proper constraints
        const constraints = {
            video: {
                width: { ideal: 300 },
                height: { ideal: 225 },
                facingMode: 'user'
            },
            audio: false
        };

        console.log('Requesting camera with constraints...');
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        console.log('Camera access granted, stream:', stream);

        // Set video stream
        console.log('Setting video stream...');
        video.srcObject = stream;
        video.setAttribute('playsinline', 'true');
        
        // Force play
        try {
            await video.play();
            console.log('Video playing');
        } catch (playErr) {
            console.log('Play error (may be normal):', playErr);
        }
        
        // Show capture button and notify user
        const captureBtn = document.getElementById('captureBtn');
        if (captureBtn) {
            captureBtn.style.display = 'inline-block';
            console.log('Capture button shown');
        }
        
        showToast('Camera ready! Click "Capture Photo" to continue.', 'success');
        console.log('Camera initialization complete');

        // Add capture event listener
        if (captureBtn) {
            captureBtn.removeEventListener('click', capturePhoto);
            captureBtn.addEventListener('click', capturePhoto);
            console.log('Capture button listener added');
        }

    } catch (err) {
        console.error('Camera error caught:', err);
        console.error('Error name:', err.name);
        console.error('Error message:', err.message);
        
        // Provide specific error messages
        if (err.name === 'NotAllowedError') {
            showToast('Camera permission denied. Please allow camera access in browser settings.', 'error');
        } else if (err.name === 'NotFoundError') {
            showToast('No camera device found. Please check your device.', 'error');
        } else if (err.name === 'NotReadableError') {
            showToast('Camera is already in use by another application.', 'error');
        } else if (err.name === 'OverconstrainedError') {
            console.log('Retrying with default constraints...');
            showToast('Retrying with default camera settings...', 'warning');
            retryWithDefaultConstraints();
        } else {
            showToast('Camera error: ' + err.message, 'error');
        }
    }
}

async function retryWithDefaultConstraints() {
    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // Try with minimal constraints
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: true,
            audio: false
        });

        const video = document.getElementById('video');
        video.srcObject = stream;
        document.getElementById('captureBtn').style.display = 'inline-block';
        showToast('Camera ready with default settings!', 'info');

        const captureBtn = document.getElementById('captureBtn');
        if (captureBtn) {
            captureBtn.addEventListener('click', capturePhoto);
        }
    } catch (retryErr) {
        console.error('Retry failed:', retryErr);
        showToast('Unable to access camera. Please check permissions.', 'error');
    }
}

function capturePhoto() {
    try {
        console.log('Capturing photo...');
        
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const photo = document.getElementById('photo');

        // Check if video element exists
        if (!video) {
            showToast('Video element not found!', 'error');
            return;
        }

        // Check canvas context
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            showToast('Canvas context unavailable.', 'error');
            return;
        }

        // Draw the video frame to canvas
        try {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            console.log('Image drawn to canvas');
        } catch (drawErr) {
            showToast('Could not capture from camera. Please try again.', 'error');
            console.error('drawImage error:', drawErr);
            return;
        }
        
        // Convert to base64 image with error handling
        let photoData;
        try {
            photoData = canvas.toDataURL('image/jpeg', 0.8);
            console.log('Photo data URL created, length:', photoData.length);
        } catch (err) {
            showToast('Failed to capture image. Please try again.', 'error');
            console.error('Canvas toDataURL error:', err);
            return;
        }

        // Validate photo data
        if (!photoData || photoData.length < 100) {
            showToast('Image capture failed. Please try again.', 'error');
            console.error('Photo data invalid, length:', photoData ? photoData.length : 0);
            return;
        }

        // Display the captured photo
        photo.src = photoData;
        photo.style.display = 'block';
        console.log('Photo displayed');
        
        // Save to localStorage
        try {
            localStorage.setItem('medicalPhoto', photoData);
            console.log('Photo saved to localStorage');
        } catch (err) {
            if (err.name === 'QuotaExceededError') {
                showToast('Storage full. Please clear browser data.', 'error');
                return;
            }
            throw err;
        }
        
        photoTaken = true;
        showPhotoBadge();
        updateProgressBar();
        
        // Stop camera stream
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            console.log('Camera stream stopped');
        }
        
        // Hide video and capture button, show retake button
        video.style.display = 'none';
        document.getElementById('captureBtn').style.display = 'none';
        document.getElementById('retakeBtn').style.display = 'inline-block';
        
        showToast('Photo captured successfully! ✓', 'success');
        console.log('Photo capture complete');
    } catch (err) {
        console.error('Photo capture error:', err);
        showToast('Error capturing photo: ' + err.message, 'error');
    }
}

function showPhotoBadge() {
    const statusDiv = document.getElementById('photoStatus');
    statusDiv.innerHTML = '<div class="photo-status-badge">✓ Photo Captured</div>';
}

function retakePhoto() {
    try {
        // Reset photo-related variables
        photoTaken = false;
        
        // Clear stored photo
        localStorage.removeItem('medicalPhoto');
        
        // Hide photo and retake button
        document.getElementById('photo').style.display = 'none';
        document.getElementById('photo').src = '';
        document.getElementById('retakeBtn').style.display = 'none';
        document.getElementById('photoStatus').innerHTML = '';
        
        // Show video and capture button
        document.getElementById('video').style.display = 'block';
        document.getElementById('captureBtn').style.display = 'inline-block';
        
        // Update progress bar
        updateProgressBar();
        
        showToast('Ready to retake photo. Click "Capture Photo" when ready.', 'info');
    } catch (err) {
        console.error('Retake photo error:', err);
        showToast('Error retaking photo.', 'error');
    }
}

function generateQR() {
    const generateBtn = document.getElementById('generateBtn');
    
    // Check if photo is captured
    const photo = document.getElementById('photo');
    if (photo.style.display === 'none' || !photo.src) {
        showToast('Please capture your face photo first!', 'warning');
        return;
    }
    
    // Get form values
    const name = document.getElementById('name').value.trim();
    const blood = document.getElementById('blood').value.trim();
    const allergy = document.getElementById('allergy').value.trim();
    const condition = document.getElementById('condition').value.trim();
    const contact = document.getElementById('contact').value.trim();

    // Validate that at least name is provided
    if (!name) {
        showToast('Please enter your name!', 'error');
        validateField(document.getElementById('name'));
        return;
    }

    // Disable button and show loading state
    generateBtn.disabled = true;
    const originalText = generateBtn.textContent;
    generateBtn.innerHTML = '<span class="spinner"></span>Generating...';

    // Create data object
    const medicalData = {
        name: name,
        blood: blood,
        allergy: allergy,
        condition: condition,
        contact: contact,
        timestamp: new Date().toISOString(),
        hasPhoto: true
    };

    // Save to localStorage for sync
    localStorage.setItem('medicalData', JSON.stringify(medicalData));

    // Save data to server database
    saveMedicalDataToServer();

    // Simulate processing time for better UX
    setTimeout(() => {
        try {
            showToast('Redirecting to QR Code page...', 'success');
            
            // Redirect to QR page after short delay
            setTimeout(() => {
                window.location.href = 'qr.html';
            }, 1000);
        } catch (error) {
            generateBtn.disabled = false;
            generateBtn.textContent = originalText;
            showToast('Error! Please try again.', 'error');
        }
    }, 800);
}

function downloadQR() {
    // Get the QR code canvas
    const canvas = document.querySelector('#qrcode canvas');
    if (canvas) {
        // Create download link
        const link = document.createElement('a');
        link.download = 'medical-qr-code.png';
        link.href = canvas.toDataURL();
        link.click();
        showToast('QR Code downloaded! ✓', 'success');
    }
}