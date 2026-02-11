/**
 * ConstructCycle - Main JavaScript
 * API Services, Auth, and Utilities
 * Dosya Yeri: js/main.js
 */

// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api/v1',
    TOKEN_KEY: 'constructcycle_token',
    USER_KEY: 'constructcycle_user',
};

// ============================================
// API SERVICE
// ============================================
const API = {
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);

        const defaultHeaders = {
            'Content-Type': 'application/json',
        };

        if (token) {
            defaultHeaders['Authorization'] = `Token ${token}`;
        }

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw { status: response.status, data };
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    },

    put(endpoint, body) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body),
        });
    },

    patch(endpoint, body) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(body),
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    async upload(endpoint, formData) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);

        const headers = {};
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData,
        });

        return response.json();
    },
};

// ============================================
// AUTH SERVICE
// ============================================
const Auth = {
    async register(data) {
        const response = await API.post('/auth/register/', data);
        if (response.token) {
            this.setSession(response.token, response.user);
        }
        return response;
    },

    async login(email, password) {
        const response = await API.post('/auth/login/', { email, password });
        if (response.token) {
            this.setSession(response.token, response.user);
        }
        return response;
    },

    logout() {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_KEY);
        window.location.href = '/login.html';
    },

    setSession(token, user) {
        localStorage.setItem(CONFIG.TOKEN_KEY, token);
        localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
    },

    getUser() {
        const user = localStorage.getItem(CONFIG.USER_KEY);
        return user ? JSON.parse(user) : null;
    },

    getToken() {
        return localStorage.getItem(CONFIG.TOKEN_KEY);
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    async getProfile() {
        return API.get('/auth/profile/');
    },

    async updateProfile(data) {
        const response = await API.patch('/auth/profile/', data);
        if (response) {
            localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(response));
        }
        return response;
    },

    async changePassword(data) {
        return API.post('/auth/change-password/', data);
    },
};

// ============================================
// PRODUCTS SERVICE
// ============================================
const Products = {
    async getAll(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/products/?${queryString}` : '/products/';
        return API.get(endpoint);
    },

    async getById(id) {
        return API.get(`/products/${id}/`);
    },

    async search(query) {
        return API.get(`/products/search/?q=${encodeURIComponent(query)}`);
    },

    async getMyProducts() {
        return API.get('/products/my-products/');
    },

    async create(data) {
        return API.post('/products/create/', data);
    },

    async update(id, data) {
        return API.patch(`/products/${id}/update/`, data);
    },

    async delete(id) {
        return API.delete(`/products/${id}/delete/`);
    },
};

// ============================================
// CATEGORIES SERVICE
// ============================================
const Categories = {
    async getAll() {
        const response = await API.get('/products/categories/');
        return response.results || response || [];
    },
};

// ============================================
// COMPANIES SERVICE
// ============================================
const Companies = {
    async register(data) {
        return API.post('/companies/register/', data);
    },

    async getMyCompany() {
        return API.get('/companies/my-company/');
    },

    async updateMyCompany(data) {
        return API.patch('/companies/my-company/', data);
    },

    async getById(id) {
        return API.get(`/companies/${id}/`);
    },
};

// ============================================
// ORDERS SERVICE
// ============================================
const Orders = {
    async create(data) {
        return API.post('/orders/create/', data);
    },

    async getMyOrders() {
        return API.get('/orders/my-orders/');
    },

    async getMySales() {
        return API.get('/orders/my-sales/');
    },

    async getById(id) {
        return API.get(`/orders/${id}/`);
    },

    async updateStatus(id, status, note = '') {
        return API.patch(`/orders/${id}/update-status/`, { status, seller_note: note });
    },

    async cancel(id) {
        return API.post(`/orders/${id}/cancel/`);
    },
};

// ============================================
// CONVERSATIONS SERVICE
// ============================================
const Conversations = {
    async getAll() {
        return API.get('/conversations/');
    },

    async start(productId, message) {
        return API.post('/conversations/start/', {
            product_id: productId,
            message_text: message,
        });
    },

    async getById(id) {
        return API.get(`/conversations/${id}/`);
    },

    async sendMessage(conversationId, message) {
        return API.post('/conversations/send-message/', {
            conversation: conversationId,
            message_text: message,
        });
    },

    async getUnreadCount() {
        return API.get('/conversations/unread-count/');
    },
};

// ============================================
// UI UTILITIES
// ============================================
const UI = {
    toast(message, type = 'info') {
        const container = document.getElementById('toast-container') || this.createToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${this.getToastIcon(type)}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    },

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle',
        };
        return icons[type] || icons.info;
    },

    showLoading() {
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="loading-spinner"></div>';
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    },

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },

    formatPrice(price) {
        return new Intl.NumberFormat('tr-TR', {
            style: 'currency',
            currency: 'TRY',
            minimumFractionDigits: 0,
        }).format(price);
    },

    formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('tr-TR', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
        }).format(date);
    },

    relativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Az önce';
        if (diffMins < 60) return `${diffMins} dakika önce`;
        if (diffHours < 24) return `${diffHours} saat önce`;
        if (diffDays < 7) return `${diffDays} gün önce`;
        return this.formatDate(dateString);
    },

    truncate(text, length = 100) {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    },
};

// ============================================
// FORM UTILITIES
// ============================================
const Form = {
    getData(form) {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        return data;
    },

    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    isValidPhone(phone) {
        const re = /^[0-9]{10,11}$/;
        return re.test(phone.replace(/\s/g, ''));
    },

    showError(field, message) {
        const input = typeof field === 'string' ? document.querySelector(field) : field;
        input.classList.add('error');

        let errorEl = input.parentNode.querySelector('.form-error');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            input.parentNode.appendChild(errorEl);
        }
        errorEl.textContent = message;
    },

    clearError(field) {
        const input = typeof field === 'string' ? document.querySelector(field) : field;
        input.classList.remove('error');

        const errorEl = input.parentNode.querySelector('.form-error');
        if (errorEl) {
            errorEl.remove();
        }
    },

    clearAllErrors(form) {
        form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
        form.querySelectorAll('.form-error').forEach(el => el.remove());
    },
};

// ============================================
// PATH HELPER
// Tüm sayfalar root-based URL kullanıyor: /login.html, /products.html vb.
// ============================================
function pagePath(filename) {
    return '/' + filename;
}

// ============================================
// HEADER COMPONENT
// ============================================
const Header = {
    init() {
        this.updateAuthButtons();
        this.initScrollEffect();
        this.initUserMenu();
        this.initMobileMenu();
        this.initSearch();
    },

    updateAuthButtons() {
        const authButtons = document.querySelector('.header-actions');
        if (!authButtons) return;

        const user = Auth.getUser();

        if (user) {
            const dashboardPage = user.user_type === 'seller' ? 'seller-dashboard.html' : 'buyer-dashboard.html';
            const dashboardLabel = user.user_type === 'seller' ? 'Satıcı Paneli' : 'Alıcı Paneli';

            authButtons.innerHTML = `
                <a href="${pagePath('messages.html')}" class="header-btn ghost icon-only" title="Mesajlar">
                    <i class="fas fa-comments"></i>
                    <span class="badge" id="unread-badge" style="display: none;">0</span>
                </a>
                <a href="${pagePath('favorites.html')}" class="header-btn ghost icon-only" title="Favoriler">
                    <i class="fas fa-heart"></i>
                </a>
                <a href="${pagePath('add-product.html')}" class="header-btn primary">
                    <i class="fas fa-plus"></i>
                    <span>İlan Ver</span>
                </a>
                <div class="user-menu" id="user-menu">
                    <div class="user-menu-trigger">
                        <div class="user-avatar">${user.first_name ? user.first_name[0].toUpperCase() : user.email[0].toUpperCase()}</div>
                        <span class="user-name-label">${user.first_name || user.email.split('@')[0]}</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div class="user-menu-dropdown">
                        <a href="${pagePath(dashboardPage)}" class="menu-highlight">
                            <i class="fas fa-tachometer-alt"></i>
                            ${dashboardLabel}
                        </a>
                        <div class="divider"></div>
                        <a href="${pagePath('profile.html')}">
                            <i class="fas fa-user"></i>
                            Profilim
                        </a>
                        <a href="${pagePath('my-products.html')}">
                            <i class="fas fa-box"></i>
                            İlanlarım
                        </a>
                        <a href="${pagePath('my-orders.html')}">
                            <i class="fas fa-shopping-bag"></i>
                            Siparişlerim
                        </a>
                        ${user.user_type === 'seller' ? `
                        <a href="${pagePath('my-company.html')}">
                            <i class="fas fa-building"></i>
                            Firmam
                        </a>
                        <a href="${pagePath('my-sales.html')}">
                            <i class="fas fa-chart-line"></i>
                            Satışlarım
                        </a>
                        ` : ''}
                        <div class="divider"></div>
                        <a href="${pagePath('settings.html')}">
                            <i class="fas fa-cog"></i>
                            Ayarlar
                        </a>
                        <button class="logout" onclick="Auth.logout()">
                            <i class="fas fa-sign-out-alt"></i>
                            Çıkış Yap
                        </button>
                    </div>
                </div>
            `;

            this.loadUnreadCount();
        } else {
            authButtons.innerHTML = `
                <a href="${pagePath('login.html')}" class="header-btn outline">
                    <i class="fas fa-sign-in-alt"></i>
                    <span>Giriş Yap</span>
                </a>
                <a href="${pagePath('register.html')}" class="header-btn primary">
                    <i class="fas fa-user-plus"></i>
                    <span>Kayıt Ol</span>
                </a>
            `;
        }
    },

    async loadUnreadCount() {
        try {
            const data = await Conversations.getUnreadCount();
            const badge = document.getElementById('unread-badge');
            if (badge && data.total_unread > 0) {
                badge.textContent = data.total_unread;
                badge.style.display = 'inline';
            }
        } catch (error) {
            console.error('Failed to load unread count:', error);
        }
    },

    initScrollEffect() {
        const header = document.querySelector('.header');
        if (!header) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    },

    initUserMenu() {
        document.addEventListener('click', (e) => {
            const userMenu = document.getElementById('user-menu');
            if (!userMenu) return;

            if (e.target.closest('.user-menu-trigger')) {
                userMenu.classList.toggle('active');
            } else if (!e.target.closest('.user-menu-dropdown')) {
                userMenu.classList.remove('active');
            }
        });
    },

    initMobileMenu() {
        const mobileBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');

        if (mobileBtn && mobileMenu) {
            mobileBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('active');
            });
        }
    },

    initSearch() {
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const query = searchForm.querySelector('input').value.trim();
                if (query) {
                    window.location.href = `/products.html?search=${encodeURIComponent(query)}`;
                }
            });
        }
    },
};

// ============================================
// INITIALIZE ON DOM READY
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    Header.init();
});

// ============================================
// EXPORT FOR MODULES
// ============================================
window.ConstructCycle = {
    API,
    Auth,
    Products,
    Categories,
    Companies,
    Orders,
    Conversations,
    UI,
    Form,
    Header,
    CONFIG,
};