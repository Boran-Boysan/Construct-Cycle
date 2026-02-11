/* ============================================
   INDEX PAGE JS - Ana Sayfa
   ============================================ */

let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
    loadCategories();
    loadProducts();
    initFilters();
    animateStats();
});

// ============================================
// LOAD CATEGORIES
// ============================================
async function loadCategories() {
    try {
        const categories = await Categories.getAll();
        const categoryList = document.getElementById('category-list');

        if (!categoryList) return;

        const categoryIcons = {
            'Metal ve Yapısal': 'fa-hammer',
            'Ahşap ve Doğrama': 'fa-tree',
            'Zemin ve Kaplama': 'fa-th-large',
            'Elektrik & Tesisat': 'fa-bolt',
            'Yalıtım': 'fa-snowflake',
            'Makine & Ekipman': 'fa-tools',
            'Beton ve Çimento': 'fa-cubes',
            'Boya ve Kaplama': 'fa-paint-roller'
        };

        categories.forEach(cat => {
            const icon = categoryIcons[cat.name] || 'fa-box';
            const item = document.createElement('a');
            item.href = `/products.html?category=${cat.id}`;
            item.className = 'category-item';
            item.innerHTML = `
                <i class="fas ${icon}"></i>
                <span>${cat.name}</span>
            `;
            categoryList.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

// ============================================
// LOAD PRODUCTS
// ============================================
async function loadProducts(append = false) {
    const grid = document.getElementById('product-grid');

    if (!grid) return;

    if (!append) {
        grid.innerHTML = `
            <div class="loading-placeholder">
                <div class="loading-spinner"></div>
                <p>Ürünler yükleniyor...</p>
            </div>
        `;
    }

    try {
        const params = {
            page: currentPage,
        };

        const city = document.getElementById('filter-city')?.value;
        const condition = document.getElementById('filter-condition')?.value;
        const ordering = document.getElementById('filter-sort')?.value;

        if (city) params.city = city;
        if (condition) params.condition = condition;
        if (ordering) params.ordering = ordering;

        const response = await Products.getAll(params);
        const products = response.results || response;

        if (!append) {
            grid.innerHTML = '';
        }

        if (products.length === 0 && !append) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="empty-state-icon">
                        <i class="fas fa-box-open"></i>
                    </div>
                    <h3>Henüz ilan yok</h3>
                    <p>Bu kriterlere uygun ilan bulunamadı.</p>
                </div>
            `;
            return;
        }

        products.forEach(product => {
            grid.appendChild(createProductCard(product));
        });

        const loadMore = document.getElementById('load-more');
        if (loadMore) {
            if (response.next) {
                loadMore.style.display = 'flex';
            } else {
                loadMore.style.display = 'none';
            }
        }

    } catch (error) {
        console.error('Failed to load products:', error);
        if (!append) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="empty-state-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3>Bir hata oluştu</h3>
                    <p>Ürünler yüklenirken bir sorun oluştu. Lütfen daha sonra tekrar deneyin.</p>
                    <button class="btn btn-primary" onclick="loadProducts()">Tekrar Dene</button>
                </div>
            `;
        }
    }
}

// ============================================
// CREATE PRODUCT CARD
// ============================================
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.onclick = () => window.location.href = `/product-detail.html?id=${product.id}`;

    const conditionLabels = {
        0: 'Sıfır',
        1: 'Az Kullanılmış',
        2: 'Kullanılmış'
    };

    const primaryImage = product.primary_image || product.images?.[0]?.image_url || '/static/images/placeholder.jpg';

    card.innerHTML = `
        <div class="product-card-image">
            <img src="${primaryImage}" alt="${product.name}" onerror="this.src='/static/images/placeholder.jpg'">
            <div class="product-card-badges">
                ${product.condition === 0 ? '<span class="product-badge new">Sıfır</span>' : ''}
                ${product.days_listed <= 3 ? '<span class="product-badge urgent">Yeni</span>' : ''}
            </div>
            <button class="product-favorite" onclick="event.stopPropagation(); toggleFavorite(${product.id}, this)">
                <i class="far fa-heart"></i>
            </button>
        </div>
        <div class="product-card-content">
            <div class="product-price">
                ${UI.formatPrice(product.sale_price)}
            </div>
            <h3 class="product-title">${product.name}</h3>
            <div class="product-meta">
                <span><i class="fas fa-map-marker-alt"></i> ${product.city}</span>
                <span><i class="fas fa-clock"></i> ${UI.relativeTime(product.created_at)}</span>
            </div>
        </div>
        <div class="product-card-footer">
            <div class="product-seller">
                <div class="seller-avatar" style="background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.7rem;">
                    ${product.company_name ? product.company_name[0].toUpperCase() : 'F'}
                </div>
                <span>${product.company_name || 'Firma'}</span>
            </div>
            <span class="product-stock ${product.stock_quantity < 10 ? 'low' : ''}">
                Stok: ${product.stock_quantity}
            </span>
        </div>
    `;

    return card;
}

// ============================================
// TOGGLE FAVORITE
// ============================================
function toggleFavorite(productId, btn) {
    if (!Auth.isLoggedIn()) {
        window.location.href = '/login.html';
        return;
    }

    btn.classList.toggle('active');
    const icon = btn.querySelector('i');
    icon.classList.toggle('far');
    icon.classList.toggle('fas');

    UI.toast(btn.classList.contains('active') ? 'Favorilere eklendi' : 'Favorilerden çıkarıldı', 'success');
}

// ============================================
// INIT FILTERS
// ============================================
function initFilters() {
    const filters = ['filter-city', 'filter-condition', 'filter-sort'];

    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) {
            filter.addEventListener('change', () => {
                currentPage = 1;
                loadProducts();
            });
        }
    });

    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => {
            currentPage++;
            loadProducts(true);
        });
    }
}

// ============================================
// ANIMATE STATS
// ============================================
function animateStats() {
    const stats = {
        'stat-products': 1250,
        'stat-companies': 340,
        'stat-savings': 15000
    };

    Object.entries(stats).forEach(([id, target]) => {
        const el = document.getElementById(id);
        if (!el) return;

        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = Math.floor(current).toLocaleString('tr-TR');
        }, 30);
    });
}