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
async function registerUser(name, email, phone, password) {
    if (!name || !email || !password) {
        return { success: false, error: 'Name, email and password are required.' };
    }

    // Generate HS-YYYY-XXXX
    const year = new Date().getFullYear();
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const newId = `HS-${year}-${randomNum}`;

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: newId,
                name: name,
                password: password,
                contact: phone
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            localStorage.setItem('loggedInUser', newId);
            localStorage.setItem('currentProfileId', newId); // Set default profile
            
            // Show alert with the newly generated ID
            alert(`Account created successfully!\n\nYour Patient ID is: ${newId}\nPlease use this ID or your registered email to log in next time.`);
            showToast('Account created! Welcome to HealthSync.', 'success');
            setTimeout(() => { window.location.href = 'sync.html'; }, 1000);
            return { success: true };
        } else {
            return { success: false, error: data.error || 'Server rejected registration.' };
        }
    } catch (err) {
        return { success: false, error: 'Could not connect to the server.' };
    }
}

// ─── 2. LOGIN USER ───────────────────────────────────────────────────────────
async function userLogin(userId, password) {
    if (!userId || !password) {
        return { success: false, error: 'Patient ID and password are required.' };
    }

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, password: password })
        });
        
        const data = await res.json();
        
        if (data.success) {
            localStorage.setItem('loggedInUser', userId);
            localStorage.setItem('currentProfileId', userId); // Default to self
            showToast('Login successful! Redirecting…', 'success');
            
            // Redirect to sync to let them edit their profile, or qr if complete
            setTimeout(() => { window.location.href = 'qr.html'; }, 1000);
            return { success: true };
        } else {
            return { success: false, error: data.error || 'Invalid credentials.' };
        }
    } catch (err) {
        return { success: false, error: 'Could not connect to the server.' };
    }
}

// ─── 3. SAVE MEDICAL DATA TO LOCALSTORAGE ───────────────────────────────────
function saveMedicalDataToLocal() {
    const profileId = localStorage.getItem('currentProfileId');
    if (!profileId) return false;

    const patients = getPatients();
    const index = patients.findIndex(p => p.id === profileId);
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
    const profileId = localStorage.getItem('currentProfileId');
    const accountId = localStorage.getItem('loggedInUser');
    if (!profileId || !accountId) return;

    const getValue = id => {
        const el = document.getElementById(id);
        return el ? el.value.trim() : '';
    };

    const payload = {
        id:       profileId,
        account_id: accountId,
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
        const res = await fetch('/api/save-medical-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        return data.success;
    } catch (e) {
        console.error('[HealthSync] Server save failed:', e);
        return false;
    }
}

// ─── 5. GENERATE QR (called from sync.html button) ──────────────────────────
async function generateQR() {
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

    const success = await saveMedicalDataToServer();
    
    if (success) {
        showToast('Profile saved! Generating QR…', 'success');
        setTimeout(() => {
            window.location.href = 'qr.html';
        }, 900);
    } else {
        showToast('Could not save to server. Try again.', 'error');
        if (btn) {
            btn.textContent = 'Generate Emergency QR Card →';
            btn.disabled = false;
        }
    }
}

// ─── 5.5 ADD FAMILY MEMBER ───────────────────────────────────────────────────
async function createFamilyMember(name, relation) {
    const accountId = localStorage.getItem('loggedInUser');
    if (!accountId) return null;

    const year = new Date().getFullYear();
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const newId = `DEP-${year}-${randomNum}`; // Dependant prefix

    const newUser = {
        id: newId,
        account_id: accountId,
        name: name,
        ecRel: relation,
        medComplete: false,
        blood: '', dob: '', gender: '', weight: '', height: '', abha: '',
        allergies: [], meds: [], conditions: [], surgeries: '',
        ecName: '', ecPhone: '', doctor: ''
    };

    const patients = getPatients();
    patients.push(newUser);
    savePatients(patients);

    // Try server sync
    try {
        await fetch('/api/add-family-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_id: accountId, name, relation })
        });
    } catch (e) {
        console.warn('Server sync failed, continuing locally.');
    }

    return newId;
}

// ─── 6. RENDER QR CODE ──────────────────────────────────────────────────────
async function renderQRCodeOnPage(containerId, patientId) {
    const qrContainer = document.getElementById(containerId);
    if (!qrContainer) return;

    qrContainer.innerHTML = '';
    let url = window.location.origin + '/viewer.html?id=' + encodeURIComponent(patientId);

    // Fetch the proper local network IP from the server ONLY if on localhost.
    // Otherwise, we keep window.location.origin (which works for ngrok!).
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        try {
            const res = await fetch('/api/generate-qr-url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: patientId })
            });
            if (res.ok) {
                const data = await res.json();
                if (data.success && data.qr_url) {
                    url = data.qr_url;
                }
            }
        } catch (e) {
            console.warn('Could not fetch network IP, using window.location.origin instead.');
        }
    }

    new QRCode(qrContainer, {
        text: url,
        width: 180, height: 180,
        colorDark: '#000000', colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });
}