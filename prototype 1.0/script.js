// script.js - JavaScript for Emergency QR Medical ID

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
    if (name) progress += 25;
    if (blood) progress += 20;
    if (allergy) progress += 20;
    if (condition) progress += 20;
    if (contact) progress += 15;
    
    document.getElementById('progressBar').style.width = progress + '%';
}

// Save medical data to server database
async function saveMedicalDataToServer() {
    try {
        // Don't include photo in database save - use localStorage only
        const medicalData = {
            id: userId,
            name: document.getElementById('name').value.trim(),
            blood: document.getElementById('blood').value.trim(),
            allergy: document.getElementById('allergy').value.trim(),
            condition: document.getElementById('condition').value.trim(),
            contact: document.getElementById('contact').value.trim()
            // photo is intentionally NOT included
        };

        console.log('Saving data (photo excluded):', medicalData);

        const response = await fetch('/api/save-medical-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(medicalData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            console.log('✓ Medical data saved to database:', result.user_id);
            localStorage.setItem('userId', result.user_id);
            userId = result.user_id;
            showToast('Data saved to database!', 'success');
            return true;
        } else {
            console.error('Save failed:', result.error);
            showToast('Warning: Could not save to database, but continuing...', 'warning');
            return false;
        }
    } catch (error) {
        console.error('Error saving to database:', error);
        console.error('Stack:', error.stack);
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

// Load data when page loads
window.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    initializeUserId();  // Initialize user ID
    setupInputValidation();
    loadSavedData();
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
        updateProgressBar();
    }
    validateAllFields();
}

function validateAllFields() {
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => validateField(input));
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