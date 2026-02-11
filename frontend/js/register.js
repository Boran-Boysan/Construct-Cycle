// register.js - EMAIL DOĞRULAMA AKIŞI İLE

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const submitBtn = document.getElementById('submit-btn');

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
        container.scrollIntoView({ behavior: 'smooth' });
    }

    // Clear alerts
    function clearAlerts() {
        const container = document.getElementById('alert-container');
        if (container) container.innerHTML = '';
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAlerts();

            // Get form data
            const firstName = document.getElementById('first_name').value.trim();
            const lastName = document.getElementById('last_name').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password_confirm').value;
            const terms = document.getElementById('terms').checked;

            // Basic Validation
            if (!firstName || !lastName || !email || !phone || !password || !passwordConfirm) {
                showAlert('Lütfen tüm zorunlu alanları doldurun.');
                return;
            }

            if (!terms) {
                showAlert('Devam etmek için şartları kabul etmelisiniz.');
                return;
            }

            if (password !== passwordConfirm) {
                showAlert('Şifreler eşleşmiyor.');
                return;
            }

            if (password.length < 8) {
                showAlert('Şifre en az 8 karakter olmalıdır.');
                return;
            }

            // Prepare data for API
            const userData = {
                first_name: firstName,
                last_name: lastName,
                email: email,
                phone: phone,
                password: password,
                password_confirm: passwordConfirm,
                user_type: 'buyer'
            };

            // Loading state
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kayıt yapılıyor...';

            try {
                const response = await fetch('http://localhost:8000/api/v1/auth/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData)
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // ✅ Backend email gönderdi, doğrulama sayfasına yönlendir
                    showAlert('Kayıt başarılı! Email adresinize doğrulama kodu gönderildi. 📧', 'success');

                    // Email'i local storage'a kaydet
                    localStorage.setItem('pendingEmail', email);
                    localStorage.setItem('pendingVerification', 'true');

                    // 2 saniye sonra email doğrulama sayfasına yönlendir
                    setTimeout(() => {
                        window.location.href = `verify-email.html?email=${encodeURIComponent(email)}`;
                    }, 2000);

                } else if (response.status === 400 && data.message &&
                           (data.message.includes('zaten kayıtlı') || data.message.includes('already exists'))) {
                    // ✅ Email zaten kayıtlı ama doğrulanmamış olabilir
                    showAlert('Bu email adresi zaten kayıtlı. Eğer email doğrulaması yapmadıysanız, doğrulama sayfasına yönlendiriliyorsunuz...', 'info');

                    localStorage.setItem('pendingEmail', email);
                    localStorage.setItem('pendingVerification', 'true');

                    setTimeout(() => {
                        window.location.href = `verify-email.html?email=${encodeURIComponent(email)}`;
                    }, 2000);

                } else {
                    let errorMessage = data.message || 'Kayıt sırasında bir hata oluştu.';

                    // Backend'den gelen field-specific hatalar
                    if (data.errors) {
                        const firstError = Object.values(data.errors)[0];
                        errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
                    }

                    showAlert(errorMessage, 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }

            } catch (error) {
                console.error('Register error:', error);
                showAlert('Sunucuya bağlanılamadı. Lütfen tekrar deneyin.', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    // Input masking for phone
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', (e) => {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
            if (!x) return;
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? ' ' + x[3] : '') + (x[4] ? ' ' + x[4] : '');
        });
    }
});