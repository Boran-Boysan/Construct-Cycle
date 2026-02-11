/**
 * BUYER DASHBOARD JS
 * Dosya Yeri: js/buyer-dashboard.js
 */

document.addEventListener('DOMContentLoaded', async () => {
    const user = Auth.getUser();

    if (!user) {
        window.location.href = '/login.html';
        return;
    }

    if (user.user_type !== 'buyer') {
        window.location.href = '/seller-dashboard.html';
        return;
    }

    document.getElementById('user-name').textContent = user.first_name || user.email;

    await loadDashboardStats();
    await loadRecentOrders();
});

async function loadDashboardStats() {
    try {
        const response = await API.get('/auth/buyer-dashboard-stats/');

        if (response.success) {
            const data = response.data;
            document.getElementById('total-orders').textContent = data.total_orders || 0;
            document.getElementById('pending-orders').textContent = data.pending_orders || 0;
            document.getElementById('favorites').textContent = data.favorites || 0;
            document.getElementById('messages').textContent = data.unread_messages || 0;
        }
    } catch (error) {
        console.error('Dashboard stats yüklenemedi:', error);
    }
}

async function loadRecentOrders() {
    try {
        const response = await API.get('/auth/recent-orders/?limit=5');

        if (response.success && response.data.length > 0) {
            const container = document.getElementById('recent-orders-list');
            container.innerHTML = '';

            response.data.forEach(order => {
                const orderCard = createOrderCard(order);
                container.appendChild(orderCard);
            });
        }
    } catch (error) {
        console.error('Son siparişler yüklenemedi:', error);
    }
}

function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card';
    card.innerHTML = `
        <div class="order-header">
            <span class="order-id">#${order.id}</span>
            <span class="order-status status-${order.status}">${getStatusText(order.status)}</span>
        </div>
        <div class="order-body">
            <p class="order-product">${order.product_name || 'Ürün'}</p>
            <p class="order-date">${UI.formatDate(order.created_at)}</p>
        </div>
        <div class="order-footer">
            <span class="order-price">${UI.formatPrice(order.total_price)}</span>
            <a href="/order-detail.html?id=${order.id}" class="btn-view">Detay</a>
        </div>
    `;
    return card;
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Beklemede',
        'processing': 'İşleniyor',
        'shipped': 'Kargoda',
        'delivered': 'Teslim Edildi',
        'cancelled': 'İptal Edildi'
    };
    return statusMap[status] || status;
}