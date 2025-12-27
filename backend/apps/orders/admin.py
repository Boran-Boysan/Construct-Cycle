
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Sipariş kalemleri inline"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_condition', 'quantity', 'unit_price', 'total_price', 'created_at')
    can_delete = False

    fields = ('product', 'product_name', 'quantity', 'unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Sipariş admin paneli"""

    list_display = (
        'order_number',
        'buyer_email',
        'seller_company_name',
        'status_badge',
        'payment_method_badge',
        'total_amount_display',
        'created_at_formatted'
    )

    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'buyer__email', 'seller_company__company_name')
    ordering = ('-created_at',)

    list_per_page = 50

    inlines = [OrderItemInline]

    # Toplu işlemler
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': ('order_number', 'buyer', 'seller_company')
        }),
        ('Durum', {
            'fields': ('status', 'payment_method')
        }),
        ('Fiyat', {
            'fields': ('total_amount',)
        }),
        ('Notlar', {
            'fields': ('buyer_note', 'seller_note')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ('order_number', 'created_at', 'updated_at')

    def buyer_email(self, obj):
        """Alıcı email"""
        return obj.buyer.email

    buyer_email.short_description = 'Alıcı'

    def seller_company_name(self, obj):
        """Satıcı firma adı"""
        return obj.seller_company.company_name

    seller_company_name.short_description = 'Satıcı Firma'

    def status_badge(self, obj):
        """Durum badge"""
        colors = {
            'pending': '#f59e0b',      # Turuncu
            'confirmed': '#3b82f6',    # Mavi
            'shipped': '#8b5cf6',      # Mor
            'delivered': '#10b981',    # Yeşil
            'cancelled': '#ef4444',    # Kırmızı
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'Durum'

    def payment_method_badge(self, obj):
        """Ödeme yöntemi badge"""
        icons = {
            'cash': '💵',
            'transfer': '🏦',
            'credit_card': '💳',
        }
        icon = icons.get(obj.payment_method, '💰')
        return format_html(
            '<span>{} {}</span>',
            icon,
            obj.get_payment_method_display()
        )

    payment_method_badge.short_description = 'Ödeme'

    def total_amount_display(self, obj):
        """Toplam tutar formatlanmış"""
        return format_html(
            '<span style="font-weight: bold; color: #10b981;">{:.2f} TL</span>',
            obj.total_amount
        )

    total_amount_display.short_description = 'Toplam Tutar'

    def created_at_formatted(self, obj):
        """Sipariş tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Sipariş Tarihi'
    created_at_formatted.admin_order_field = 'created_at'

    # Toplu işlemler
    def mark_as_confirmed(self, request, queryset):
        """Seçili siparişleri onayla"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} sipariş onaylandı.')

    mark_as_confirmed.short_description = "✓ Siparişleri onayla"

    def mark_as_shipped(self, request, queryset):
        """Seçili siparişleri kargoya verildi olarak işaretle"""
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} sipariş kargoya verildi olarak işaretlendi.')

    mark_as_shipped.short_description = "📦 Kargoya verildi"

    def mark_as_delivered(self, request, queryset):
        """Seçili siparişleri teslim edildi olarak işaretle"""
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} sipariş teslim edildi olarak işaretlendi.')

    mark_as_delivered.short_description = "✅ Teslim edildi"

    def mark_as_cancelled(self, request, queryset):
        """Seçili siparişleri iptal et"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} sipariş iptal edildi.')

    mark_as_cancelled.short_description = "❌ İptal et"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Sipariş kalemi admin paneli"""

    list_display = (
        'order_number',
        'product_name',
        'quantity',
        'unit_price_display',
        'total_price_display',
        'created_at_formatted'
    )

    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product_name', 'product__name')
    ordering = ('-created_at',)

    list_per_page = 50

    fieldsets = (
        ('Sipariş', {
            'fields': ('order',)
        }),
        ('Ürün', {
            'fields': ('product', 'product_name', 'product_condition')
        }),
        ('Miktar ve Fiyat', {
            'fields': ('quantity', 'unit_price', 'total_price')
        }),
        ('Tarih', {
            'fields': ('created_at',)
        }),
    )

    readonly_fields = ('product_name', 'product_condition', 'total_price', 'created_at')

    def order_number(self, obj):
        """Sipariş numarası"""
        return obj.order.order_number

    order_number.short_description = 'Sipariş No'

    def unit_price_display(self, obj):
        """Birim fiyat formatlanmış"""
        return f'{obj.unit_price:.2f} TL'

    unit_price_display.short_description = 'Birim Fiyat'

    def total_price_display(self, obj):
        """Toplam fiyat formatlanmış"""
        return format_html(
            '<span style="font-weight: bold; color: #10b981;">{:.2f} TL</span>',
            obj.total_price
        )

    total_price_display.short_description = 'Toplam'

    def created_at_formatted(self, obj):
        """Eklenme tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Eklenme Tarihi'
    created_at_formatted.admin_order_field = 'created_at'