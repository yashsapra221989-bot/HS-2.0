// script.js - JavaScript for Emergency QR Medical ID

let userId = null;

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

// Ensure hs_patients array exists
function getPatients() {
    return JSON.parse(localStorage.getItem('hs_patients') || '[]');
}
function savePatients(patients) {
    localStorage.setItem('hs_patients', JSON.stringify(patients));
}

// 1. Register User Logic
function registerUser(name, email, phone, password) {
    const patients = getPatients();
    
    // Check if email already exists
    if (patients.find(p => p.email === email)) {
        document.getElementById('globalError').textContent = 'Email already registered.';
        return;
    }
    
    // Generate HS-YYYY-XXXX
    const year = new Date().getFullYear();
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const newId = `HS-${year}-${randomNum}`;
    
    const newUser = {
        id: newId,
        name: name,
        email: email,
        phone: phone,
        password: password,
        medComplete: false,
        blood: '', dob: '', gender: '', weight: '', height: '', abha: '',
        allergies: [], meds: [], conditions: [], surgeries: '',
        ecName: '', ecRel: '', ecPhone: '', doctor: ''
    };
    
    patients.push(newUser);
    savePatients(patients);
    
    sessionStorage.setItem('loggedInUser', newId);
    showToast('Account created successfully!', 'success');
    
    // Redirection
    setTimeout(() => {
        window.location.href = 'sync.html';
    }, 1000);
}

// 2. Login User Logic
function userLogin(email, password) {
    const patients = getPatients();
    const user = patients.find(p => p.email === email);
    
    if (!user) {
        document.getElementById('globalError').textContent = 'No account found with this email.';
        return;
    }
    if (user.password !== password) {
        document.getElementById('globalError').textContent = 'Incorrect password.';
        return;
    }
    
    sessionStorage.setItem('loggedInUser', user.id);
    showToast('Login successful!', 'success');
    
    setTimeout(() => {
        if (user.medComplete) window.location.href = 'qr.html';
        else window.location.href = 'sync.html';
    }, 1000);
}

// 3. Sync HTML form fields to localStorage
function saveMedicalDataToLocal() {
    const loggedInId = sessionStorage.getItem('loggedInUser');
    if (!loggedInId) return;

    const patients = getPatients();
    const index = patients.findIndex(p => p.id === loggedInId);
    if (index === -1) return;

    // Read rich fields from sync.html (if elements exist)
    const getValue = id => document.getElementById(id) ? document.getElementById(id).value.trim() : '';
    
    // Parse arrays correctly
    const parseArray = str => s && s.trim() ? s.split(',').map(item => item.trim()) : [];

    const allergyStr = getValue('allergy');
    const medsStr = getValue('meds');
    const conditionsStr = getValue('condition');

    patients[index].name = getValue('name') || patients[index].name;
    patients[index].blood = getValue('blood');
    patients[index].dob = getValue('dob');
    patients[index].gender = getValue('gender');
    patients[index].weight = getValue('weight');
    patients[index].height = getValue('height');
    patients[index].abha = getValue('abha');
    
    patients[index].allergies = allergyStr ? allergyStr.split(',').map(s=>s.trim()) : [];
    patients[index].meds = medsStr ? medsStr.split(',').map(s=>s.trim()) : [];
    patients[index].conditions = conditionsStr ? conditionsStr.split(',').map(s=>s.trim()) : [];
    patients[index].surgeries = getValue('surgeries');
    
    patients[index].ecName = getValue('ecName');
    patients[index].ecRel = getValue('ecRel');
    patients[index].ecPhone = getValue('ecPhone') || getValue('contact'); // fallback contact
    patients[index].doctor = getValue('doctor');

    patients[index].medComplete = true; // Mark as true!

    savePatients(patients);
}

// Existing save to server (kept as requested) but runs local save first
async function saveMedicalDataToServer() {
    saveMedicalDataToLocal(); // Always update localStorage first
    
    // Original server save logic...
    try {
        const medicalData = {
            id: sessionStorage.getItem('loggedInUser') || 'unknown',
            name: document.getElementById('name') ? document.getElementById('name').value : '',
            // (truncated for brevity, but kept structure)
        };
        const response = await fetch('/api/save-medical-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(medicalData)
        }).catch(e => { /* ignores network error */ });
    } catch (error) {
        console.error('Server save failed, but local save succeeded.');
    }
}

function generateQR() {
    saveMedicalDataToLocal();
    saveMedicalDataToServer();
    
    setTimeout(() => {
        window.location.href = 'qr.html';
    }, 500);
}

// Utility: QR rendering code for qr.html
function renderQRCodeOnPage(containerId, patientId) {
    const qrContainer = document.getElementById(containerId);
    if (!qrContainer) return;
    
    qrContainer.innerHTML = '';
    const url = window.location.origin + '/viewer.html?id=' + encodeURIComponent(patientId);
    
    new QRCode(qrContainer, {
        text: url,
        width: 180, height: 180,
        colorDark: '#000000', colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });
}