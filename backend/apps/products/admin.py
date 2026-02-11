from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Kategori admin paneli"""

    list_display = ('name', 'parent', 'slug', 'display_order', 'created_at_formatted')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')

    list_per_page = 50

    def created_at_formatted(self, obj):
        """Oluşturulma tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Oluşturma Tarihi'
    created_at_formatted.admin_order_field = 'created_at'


class ProductImageInline(admin.TabularInline):
    """Ürün fotoğrafları inline"""
    model = ProductImage
    extra = 1
    fields = ('image_url', 'is_primary', 'display_order')
    readonly_fields = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Ürün admin paneli"""

    list_display = (
        'name',
        'company_name',
        'category',
        'price_display',
        'condition_badge',
        'stock_badge',
        'city',
        'status_badge',
        'created_at_formatted'
    )

    list_filter = ('condition', 'is_active', 'is_sold', 'city', 'category', 'created_at')
    search_fields = ('name', 'description', 'company__company_name', 'tags')
    ordering = ('-created_at',)

    list_per_page = 50

    inlines = [ProductImageInline]

    # Toplu işlemler
    actions = ['activate_products', 'deactivate_products', 'mark_as_sold']

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('company', 'name', 'description', 'category')
        }),
        ('Fiyat ve Stok', {
            'fields': ('sale_price', 'ai_suggested_price', 'stock_quantity', 'condition')
        }),
        ('Konum', {
            'fields': ('city', 'district')
        }),
        ('Etiketler', {
            'fields': ('tags',),
            'description': 'PostgreSQL array field - Virgülle ayrılmış etiketler girebilirsiniz'
        }),
        ('Durum', {
            'fields': ('is_active', 'is_sold')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def company_name(self, obj):
        """Firma adı"""
        return obj.company.company_name

    company_name.short_description = 'Firma'

    def price_display(self, obj):
        """Fiyat gösterimi"""
        if obj.ai_suggested_price and obj.ai_suggested_price > obj.sale_price:
            savings = obj.savings
            html = '<div style="display: flex; flex-direction: column; gap: 2px;">'
            html += f'<span style="color: #10b981; font-weight: bold; font-size: 14px;">{obj.sale_price} TL</span>'
            html += f'<del style="color: #999; font-size: 11px;">{obj.ai_suggested_price} TL</del>'
            html += f'<span style="color: #10b981; font-size: 10px;">Tasarruf: {savings} TL</span>'
            html += '</div>'
            return mark_safe(html)
        return mark_safe(f'<span style="font-size: 14px;">{obj.sale_price} TL</span>')

    price_display.short_description = 'Fiyat'

    def condition_badge(self, obj):
        """Durum badge"""
        colors = {
            0: '#10b981',  # Sıfır - Yeşil
            1: '#3b82f6',  # Az kullanılmış - Mavi
            2: '#f59e0b',  # Kullanılmış - Turuncu
        }
        color = colors.get(obj.condition, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_condition_display()
        )

    condition_badge.short_description = 'Durum'

    def stock_badge(self, obj):
        """Stok badge"""
        if obj.stock_quantity == 0:
            return mark_safe('<span style="color: #ef4444; font-weight: bold;">Tükendi</span>')
        elif obj.stock_quantity < 10:
            return mark_safe(f'<span style="color: #f59e0b;">{obj.stock_quantity}</span>')
        return mark_safe(f'<span style="color: #10b981;">{obj.stock_quantity}</span>')

    stock_badge.short_description = 'Stok'

    def status_badge(self, obj):
        """Aktif/Pasif/Satıldı badge"""
        if obj.is_sold:
            return format_html(
                '<span style="background: #ef4444; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">Satıldı</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">Aktif</span>'
            )
        else:
            return format_html(
                '<span style="background: #6b7280; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">Pasif</span>'
            )

    status_badge.short_description = 'Durum'

    def created_at_formatted(self, obj):
        """Oluşturulma tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'İlan Tarihi'
    created_at_formatted.admin_order_field = 'created_at'

    # Toplu işlemler
    def activate_products(self, request, queryset):
        """Seçili ürünleri aktif yap"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} ürün aktif edildi.')

    activate_products.short_description = "✓ Ürünleri aktif yap"

    def deactivate_products(self, request, queryset):
        """Seçili ürünleri pasif yap"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} ürün pasif edildi.')

    deactivate_products.short_description = "✗ Ürünleri pasif yap"

    def mark_as_sold(self, request, queryset):
        """Seçili ürünleri satıldı olarak işaretle"""
        updated = queryset.update(is_sold=True, is_active=False)
        self.message_user(request, f'{updated} ürün satıldı olarak işaretlendi.')

    mark_as_sold.short_description = "💰 Satıldı olarak işaretle"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Ürün fotoğrafı admin paneli"""

    list_display = ('product_name', 'image_preview', 'is_primary', 'display_order', 'created_at_formatted')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name',)
    ordering = ('product', 'display_order')

    list_per_page = 50

    def product_name(self, obj):
        """Ürün adı"""
        return obj.product.name

    product_name.short_description = 'Ürün'

    def image_preview(self, obj):
        """Fotoğraf önizleme"""
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url.url}" width="100" height="100" style="object-fit: cover;" />')
        return '-'

    image_preview.short_description = 'Önizleme'

    def created_at_formatted(self, obj):
        """Yüklenme tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Yüklenme Tarihi'
    created_at_formatted.admin_order_field = 'created_at'