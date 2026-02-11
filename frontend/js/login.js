/**
 * LOGIN PAGE JS
 * Dosya Yeri: js/login.js
 */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const submitBtn = document.getElementById('submit-btn');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    window.togglePassword = function (fieldId) {
        const field = document.getElementById(fieldId);
        const icon = field.parentNode.querySelector('.toggle-password i');
        if (field.type === 'password') {
            field.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            field.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    };

    function showAlert(message, type = 'error') {
        const container = document.getElementById('alert-container');
        if (!container) return;
        container.innerHTML = `
            <div class="alert alert-${type}">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
    }

    function clearAlerts() {
        const container = document.getElementById('alert-container');
        if (container) container.innerHTML = '';
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAlerts();

            const email = emailInput.value.trim();
            const password = passwordInput.value;

            if (!email || !password) {
                showAlert('Lütfen tüm alanları doldurun.');
                return;
            }

            if (!isValidEmail(email)) {
                showAlert('Geçerli bir e-posta adresi girin.');
                return;
            }

            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Giriş yapılıyor...';

            try {
                const response = await Auth.login(email, password);

                showAlert('Giriş başarılı! Yönlendiriliyorsunuz...', 'success');

                // Login sonrası ana sayfaya yönlendir
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);

            } catch (error) {
                console.error('Login error:', error);

                let errorMessage = 'Giriş yapılırken bir hata oluştu.';

                if (error.status === 401) {
                    errorMessage = 'E-posta veya şifre hatalı.';
                } else if (error.status === 403) {
                    if (error.data && error.data.message && error.data.message.includes('doğrulan')) {
                        errorMessage = 'Email adresinizi henüz doğrulamadınız.';
                    } else {
                        errorMessage = error.data?.detail || error.data?.message || 'Giriş yetkiniz yok.';
                    }
                } else if (error.status === 429) {
                    errorMessage = 'Çok fazla deneme yaptınız. Biraz bekleyin.';
                } else if (error.data && error.data.non_field_errors) {
                    const nfe = error.data.non_field_errors;
                    errorMessage = Array.isArray(nfe) ? nfe[0] : nfe;
                } else if (error.data && error.data.detail) {
                    errorMessage = error.data.detail;
                } else if (error.data && error.data.message) {
                    errorMessage = error.data.message;
                } else if (error.message) {
                    errorMessage = error.message;
                }

                showAlert(errorMessage, 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }
});