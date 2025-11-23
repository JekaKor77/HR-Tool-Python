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

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {

    let token = sessionStorage.getItem("access_token");
    if (!token) {
        token = await tryRefreshToken();
    }

    if (!token) {
        window.location.replace("/auth");
        return;
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

    setInterval(() => {
        tryRefreshToken();
    }, 10 * 60 * 1000);

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

function getCSRFToken() {
    const name = "csrf_token=";
    const parts = document.cookie.split(";");
    for (let p of parts) {
        const c = p.trim();
        if (c.startsWith(name)) return c.substring(name.length);
    }
    return null;
}

async function tryRefreshToken() {
    const csrf = getCSRFToken();

    const res = await fetch("/refresh", {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            ...(csrf ? { "X-CSRF-TOKEN": csrf } : {})
        }
    });

    if (!res.ok) return null;

    const data = await res.json();
    if (data.access_token) {
        window.__access_token = data.access_token;
        return data.access_token;
    }

    return null;
}

async function authFetch(url, options = {}) {
    if (!options.headers) options.headers = {};

    if (window.__access_token) {
        options.headers["Authorization"] = "Bearer " + window.__access_token;
    }

    let response = await fetch(url, options);

    if (response.status === 401) {
        const newToken = await tryRefreshToken();

        if (newToken) {
            options.headers["Authorization"] = "Bearer " + newToken;
            response = await fetch(url, options);
        } else {
            window.location.href = "/auth";
            return;
        }
    }

    return response;
}