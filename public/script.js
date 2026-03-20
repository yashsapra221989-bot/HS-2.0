// script.js - HealthSync Core Logic

// ─── INJECT TOAST CSS into <head> ───────────────────────────────────────────
(function injectToastStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .toast {
            position: fixed;
            bottom: 32px;
            right: 32px;
            z-index: 9999;
            padding: 14px 22px;
            border-radius: 12px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.9rem;
            font-weight: 500;
            color: #e8edf5;
            background: #161b27;
            border: 1px solid #232d42;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            opacity: 1;
            transform: translateY(0);
            transition: opacity 0.4s ease, transform 0.4s ease;
            max-width: 320px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .toast.success { border-color: rgba(0,229,160,0.4); color: #00e5a0; }
        .toast.error   { border-color: rgba(255,71,87,0.4);  color: #ff4757; }
        .toast.info    { border-color: rgba(0,200,255,0.4);  color: #00c8ff; }
        .toast.hide    { opacity: 0; transform: translateY(12px); }
    `;
    document.head.appendChild(style);
})();

// ─── TOAST NOTIFICATION ─────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = (icons[type] || '') + ' ' + message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// ─── LOCALSTORAGE HELPERS ────────────────────────────────────────────────────
function getPatients() {
    return JSON.parse(localStorage.getItem('hs_patients') || '[]');
}
function savePatients(patients) {
    localStorage.setItem('hs_patients', JSON.stringify(patients));
}

// ─── 1. REGISTER USER ────────────────────────────────────────────────────────
function registerUser(name, email, phone, password) {
    const patients = getPatients();

    if (!name || !email || !password) {
        document.getElementById('globalError').textContent = 'Name, email and password are required.';
        return;
    }

    // Check duplicate email
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
        name,
        email,
        phone,
        password,
        medComplete: false,
        blood: '', dob: '', gender: '', weight: '', height: '', abha: '',
        allergies: [], meds: [], conditions: [], surgeries: '',
        ecName: '', ecRel: '', ecPhone: '', doctor: ''
    };

    patients.push(newUser);
    savePatients(patients);

    sessionStorage.setItem('loggedInUser', newId);
    showToast('Account created! Welcome to HealthSync.', 'success');

    setTimeout(() => { window.location.href = 'sync.html'; }, 1200);
}

// ─── 2. LOGIN USER ───────────────────────────────────────────────────────────
function userLogin(email, password) {
    if (!email || !password) {
        document.getElementById('globalError').textContent = 'Email and password are required.';
        return;
    }

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
    showToast('Login successful! Redirecting…', 'success');

    setTimeout(() => {
        window.location.href = user.medComplete ? 'qr.html' : 'sync.html';
    }, 1000);
}

// ─── 3. SAVE MEDICAL DATA TO LOCALSTORAGE ───────────────────────────────────
function saveMedicalDataToLocal() {
    const loggedInId = sessionStorage.getItem('loggedInUser');
    if (!loggedInId) return false;

    const patients = getPatients();
    const index = patients.findIndex(p => p.id === loggedInId);
    if (index === -1) return false;

    const getValue = id => {
        const el = document.getElementById(id);
        return el ? el.value.trim() : '';
    };
    const parseArr = str => str ? str.split(',').map(s => s.trim()).filter(Boolean) : [];

    patients[index].name       = getValue('name') || patients[index].name;
    patients[index].blood      = getValue('blood');
    patients[index].dob        = getValue('dob');
    patients[index].gender     = getValue('gender');
    patients[index].weight     = getValue('weight');
    patients[index].height     = getValue('height');
    patients[index].abha       = getValue('abha');
    patients[index].allergies  = parseArr(getValue('allergy'));
    patients[index].meds       = parseArr(getValue('meds'));
    patients[index].conditions = parseArr(getValue('condition'));
    patients[index].surgeries  = getValue('surgeries');
    patients[index].ecName     = getValue('ecName');
    patients[index].ecRel      = getValue('ecRel');
    patients[index].ecPhone    = getValue('ecPhone') || getValue('contact');
    patients[index].doctor     = getValue('doctor');
    patients[index].medComplete = true;

    savePatients(patients);
    return true;
}

// ─── 4. SAVE TO SERVER (NON-BLOCKING) ───────────────────────────────────────
async function saveMedicalDataToServer() {
    const loggedInId = sessionStorage.getItem('loggedInUser');
    if (!loggedInId) return;

    const getValue = id => {
        const el = document.getElementById(id);
        return el ? el.value.trim() : '';
    };

    const payload = {
        id:       loggedInId,
        name:     getValue('name'),
        blood:    getValue('blood'),
        dob:      getValue('dob'),
        gender:   getValue('gender'),
        weight:   getValue('weight'),
        height:   getValue('height'),
        abha:     getValue('abha'),
        allergy:  getValue('allergy'),
        meds:     getValue('meds'),
        condition: getValue('condition'),
        surgeries: getValue('surgeries'),
        ecName:   getValue('ecName'),
        ecRel:    getValue('ecRel'),
        contact:  getValue('ecPhone') || getValue('contact'),
        doctor:   getValue('doctor')
    };

    try {
        await fetch('/api/save-medical-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (e) {
        // Server save is non-critical; localStorage is source of truth
        console.warn('[HealthSync] Server save skipped — continuing offline.');
    }
}

// ─── 5. GENERATE QR (called from sync.html button) ──────────────────────────
function generateQR() {
    // Validate required fields
    const name    = document.getElementById('name')    ? document.getElementById('name').value.trim()    : '';
    const blood   = document.getElementById('blood')   ? document.getElementById('blood').value.trim()   : '';
    const ecPhone = document.getElementById('ecPhone') ? document.getElementById('ecPhone').value.trim() : '';

    const errors = [];
    if (!name)    errors.push('Full Name');
    if (!blood)   errors.push('Blood Group');
    if (!ecPhone) errors.push('Emergency Phone');

    if (errors.length > 0) {
        showToast(`Please fill: ${errors.join(', ')}`, 'error');
        return;
    }

    const btn = document.querySelector('.btn-submit');
    if (btn) {
        btn.textContent = 'Saving…';
        btn.disabled = true;
    }

    saveMedicalDataToLocal();
    saveMedicalDataToServer(); // fire-and-forget

    showToast('Profile saved! Generating QR…', 'success');

    setTimeout(() => {
        window.location.href = 'qr.html';
    }, 900);
}

// ─── 6. RENDER QR CODE ──────────────────────────────────────────────────────
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