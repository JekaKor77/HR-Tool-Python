// Main JavaScript for HR CV Analysis System

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main .container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showLoading(element) {
    element.classList.add('loading');
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.style.display = 'block';
    }
}

function hideLoading(element) {
    element.classList.remove('loading');
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

// Form validation
function validateFileUpload(fileInput) {
    const file = fileInput.files[0];
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (!file) {
        return { valid: false, message: 'Please select a file to upload.' };
    }
    
    if (file.size > maxSize) {
        return { valid: false, message: 'File size must be less than 16MB.' };
    }
    
    if (!allowedTypes.includes(file.type)) {
        return { valid: false, message: 'Please upload a PDF, DOC, DOCX, or TXT file.' };
    }
    
    return { valid: true };
}

// Auto-save form data to localStorage
function autoSaveForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Load saved data
    const savedData = localStorage.getItem(`form_${formId}`);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = data[key];
                }
            });
        } catch (e) {
            console.warn('Could not load saved form data:', e);
        }
    }
    
    // Save data on input change
    form.addEventListener('input', function() {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    });
}

// Clear saved form data
function clearSavedForm(formId) {
    localStorage.removeItem(`form_${formId}`);
}

const ACCESS_TOKEN_LIFETIME = 45 * 60 * 1000;
const REFRESH_BEFORE_EXPIRY = 60 * 1000;

function getCSRFToken() {
    const name = "csrf_token=";
    const parts = document.cookie.split(";");
    for (let p of parts) {
        const c = p.trim();
        if (c.startsWith(name)) return c.substring(name.length);
    }
    return null;
}

let _refreshInProgress = null;


async function tryRefreshToken() {
    if (_refreshInProgress) {
        try { return await _refreshInProgress; } catch (e) { return null; }
    }

    const csrf = getCSRFToken();

    _refreshInProgress = (async () => {
        try {
            const res = await fetch('/auth/refresh', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    ...(csrf ? { 'X-CSRF-TOKEN': csrf } : {})
                },
                credentials: 'same-origin'
            });

            if (!res.ok) return null;
            const data = await res.json().catch(() => ({}));
            if (data.access_token) {
                window.__access_token = data.access_token;
                sessionStorage.setItem('access_token', data.access_token);
                scheduleRefresh();
                return data.access_token;
            }
            return null;
        } finally {
            _refreshInProgress = null;
        }
    })();

    return _refreshInProgress;
}

function scheduleRefresh() {
    clearTimeout(window._refreshTimer);
    window._refreshTimer = setTimeout(() => {
        tryRefreshToken();
    }, ACCESS_TOKEN_LIFETIME - REFRESH_BEFORE_EXPIRY);
}

async function authFetch(url, options = {}) {
    options.credentials = options.credentials || 'same-origin';
    options.headers = options.headers || {};

    if (window.__access_token) {
        options.headers['Authorization'] = 'Bearer ' + window.__access_token;
    }
    options.headers['X-Requested-With'] = options.headers['X-Requested-With'] || 'XMLHttpRequest';

    let resp = await fetch(url, options);

    if (resp.status === 401) {
        const newTok = await tryRefreshToken();
        if (newTok) {
            options.headers['Authorization'] = 'Bearer ' + newTok;
            resp = await fetch(url, options);
        } else {
            const redirectTo = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.replace(`/auth?next=${redirectTo}`);
            return;
        }
    }

    return resp;
}

function hasRefreshCookie() {
    return document.cookie.split(";").some(c => c.trim().startsWith("refresh_token="));
}

async function handleOAuthCallbackIfNeeded() {
    if (!window.location.pathname.startsWith('/auth/authorize/')) return;

    try {
        const res = await fetch(window.location.href, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        });

        const data = await res.json().catch(() => null);
        if (!data) return;

        if (data.access_token) {
            window.__access_token = data.access_token;
            sessionStorage.setItem('access_token', data.access_token);

            const params = new URLSearchParams(window.location.search);
            const next = params.get('next');

            window.location.replace(next || '/');
        }
    } catch (e) {
        console.error('OAuth callback handling error', e);
    }
}

function renderLogoutButton() {
    const accessToken = sessionStorage.getItem('access_token') || window.__access_token;
    if (!accessToken) return;

    const nav = document.querySelector('.navbar-nav.ms-auto');
    if (!nav || document.getElementById('logoutForm')) return;

    const form = document.createElement('form');
    form.id = 'logoutForm';
    form.className = 'd-inline ms-2';
    form.method = 'POST';
    form.action = '/auth/logout';
    form.innerHTML = `
        <button type="submit" class="btn btn-outline-light btn-sm">
            <i class="fas fa-sign-out-alt me-1"></i>Logout
        </button>
    `;
    nav.appendChild(form);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        let csrf = getCSRFToken();
        if (!csrf) {
            // делаем fetch, чтобы установить куку
            await fetch('/auth/csrf', {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin'
            });
            // читаем токен снова
            csrf = getCSRFToken();
        }

        if (!csrf) {
            console.error("CSRF token still not found!");
            return;
        }

        try {
            await fetch(form.action, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'X-CSRF-TOKEN': csrf
                }
            });
            sessionStorage.removeItem('access_token');
            window.location.href = '/';
        } catch (err) {
            console.error('Logout failed', err);
        }
    });
}

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
    await handleOAuthCallbackIfNeeded();
    const pathname = window.location.pathname + (window.location.search || '');
    window.__access_token = sessionStorage.getItem('access_token') || null;

    if (pathname.startsWith('/auth')) {
        if (!getCSRFToken()) {
            await fetch('/auth/csrf', {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin'
            });
        }
    } else {
        let token = window.__access_token;
        if (!token) {
            if (hasRefreshCookie()) {
                token = await tryRefreshToken();
            }
            if (!token && !hasRefreshCookie()) {
                const redirectTo = encodeURIComponent(pathname);
                window.location.replace(`/auth?next=${redirectTo}`);
                return;
            }
        }

        // Add fade-in animation to main content
        const mainContent = document.querySelector('main .container');
        if (mainContent) {
            mainContent.classList.add('fade-in-up');
        }

        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Auto-save quiz form
        autoSaveForm('quizForm');

        // Clear saved data when starting new candidate
        const newCandidateLink = document.querySelector('a[href*="new_candidate"]');
        if (newCandidateLink) {
            newCandidateLink.addEventListener('click', function() {
                clearSavedForm('quizForm');
            });
        }
        scheduleRefresh();
        renderLogoutButton();
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showAlert('An unexpected error occurred. Please try again.', 'danger');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showAlert('An unexpected error occurred. Please try again.', 'danger');
});
