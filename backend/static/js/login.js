document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const loginForm = document.getElementById('login-form');
    const submitBtn = document.getElementById('submit-btn');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    // Toggle password visibility
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

    // Show alert message
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

    // Clear alerts
    function clearAlerts() {
        const container = document.getElementById('alert-container');
        if (container) container.innerHTML = '';
    }

    // Validate email
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Login form handler
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAlerts();

            const email = emailInput.value.trim();
            const password = passwordInput.value;

            // Form Validation
            if (!email || !password) {
                showAlert('Lütfen tüm alanları doldurun.');
                return;
            }

            if (!isValidEmail(email)) {
                showAlert('Geçerli bir e-posta adresi girin.');
                return;
            }

            // Loading state
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Giriş yapılıyor...';

            try {
                // Use Auth service from main.js
                // Auth.login will handle API call and session storage
                const response = await Auth.login(email, password);

                showAlert('Giriş başarılı! Yönlendiriliyorsunuz...', 'success');
                console.log('User logged in:', response.user);

                setTimeout(() => {
                    // Role based redirection
                    const user = response.user;
                    if (user && user.user_type === 'admin') {
                        // Redirect to admin panel if available, or profile
                        window.location.href = '/admin/';
                    } else {
                        // Buyer and Seller go to home
                        window.location.href = '/';
                    }
                }, 1000);

            } catch (error) {
                console.error('Login error:', error);

                let errorMessage = 'Giriş yapılırken bir hata oluştu.';

                if (error.status === 401) {
                    errorMessage = 'E-posta veya şifre hatalı.';
                } else if (error.status === 429) {
                    errorMessage = 'Çok fazla deneme yaptınız. Lütfen biraz bekleyin.';
                } else if (error.data && error.data.detail) {
                    errorMessage = error.data.detail;
                } else if (error.message) {
                    errorMessage = error.message;
                }

                showAlert(errorMessage, 'error');

                // Reset button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    // Social Login Placeholders
    const socialBtns = document.querySelectorAll('.social-btn');
    socialBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Check which provider
            const text = btn.querySelector('span').innerText.toLowerCase();
            showAlert(`${text} ile giriş henüz aktif değil. Lütfen e-posta ile giriş yapın.`, 'warning');
        });
    });
});
