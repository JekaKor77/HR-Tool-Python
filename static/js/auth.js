function showAuthError(msg) {
    const el = document.getElementById('authError');
    const msgEl = document.getElementById('errorMessage');
    if (msgEl) msgEl.textContent = msg;
    if (el) el.classList.remove('d-none');
}

function hideAuthError() {
    const el = document.getElementById('authError');
    if (el) el.classList.add('d-none');
}

// generic POST helper for auth actions
async function postAuth(endpoint, payload) {
    hideAuthError();
    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-TOKEN': getCSRFToken() || ''
            },
            credentials: 'same-origin',
            body: JSON.stringify(payload)
        });

        const data = await res.json().catch(()=> ({}));

        if (res.ok) return data;
        const err = data.error || data.message || 'Authentication failed';
        throw new Error(err);
    } catch (err) {
        throw err;
    }
}

// handle login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    try {
        const payload = {
            email: document.getElementById('loginEmail').value,
            password: document.getElementById('loginPassword').value
        };
        const data = await postAuth('/auth/login', payload);

        if (data.access_token) {
            window.__access_token = data.access_token;
            sessionStorage.setItem('access_token', data.access_token);
        }

        const params = new URLSearchParams(window.location.search);
        const next = params.get('next');
        window.location.replace(next || '/');
    } catch (err) {
        showAuthError(err.message);
    } finally {
        btn.disabled = false;
    }
});


// handle register

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('registerBtn');
    btn.disabled = true;
    try {
        const payload = {
            first_name: document.getElementById('firstName').value,
            last_name: document.getElementById('lastName').value,
            email: document.getElementById('registerEmail').value,
            password: document.getElementById('registerPassword').value
        };
        const data = await postAuth('/auth/register', payload);

        if (data.access_token) {
            window.__access_token = data.access_token;
            sessionStorage.setItem('access_token', data.access_token);
        }

        const params = new URLSearchParams();
        params.set('registered', '1');
        window.location.replace('/auth?' + params.toString());
    } catch (err) {
        showAuthError(err.message);
    } finally {
        btn.disabled = false;
    }
});


// show a welcome / registered message if ?registered=1
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('registered') === '1') {
        showAlert('Registration successful — please log in.', 'success');
    }
});



