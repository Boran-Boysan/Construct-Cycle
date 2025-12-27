from django.contrib import admin
from django.utils.html import format_html
from .models import Company, CompanyUser


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Firma admin paneli"""

    list_display = (
        'company_name',
        'owner_email',
        'tax_number',
        'city',
        'phone',
        'verified_badge',
        'created_at_formatted'
    )

    list_filter = ('is_verified', 'city', 'created_at')
    search_fields = ('company_name', 'tax_number', 'owner_user__email', 'phone', 'email')
    ordering = ('-created_at',)

    list_per_page = 50

    # Toplu işlemler
    actions = ['verify_companies', 'unverify_companies']

    fieldsets = (
        ('Firma Bilgileri', {
            'fields': ('company_name', 'tax_number', 'owner_user')
        }),
        ('İletişim', {
            'fields': ('city', 'district', 'phone', 'email')
        }),
        ('Durum', {
            'fields': ('is_verified',)
        }),
        ('Tarihler', {
            'fields': ('created_at',)
        }),
    )

    readonly_fields = ('created_at',)

    def owner_email(self, obj):
        """Firma sahibinin emaili"""
        return obj.owner_user.email

    owner_email.short_description = 'Firma Sahibi'

    def verified_badge(self, obj):
        """Doğrulama durumu badge"""
        if obj.is_verified:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px;">✓ Doğrulanmış</span>'
            )
        return format_html(
            '<span style="background: #f59e0b; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">⏳ Bekliyor</span>'
        )

    verified_badge.short_description = 'Doğrulama'

    def created_at_formatted(self, obj):
        """Oluşturulma tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Kayıt Tarihi'
    created_at_formatted.admin_order_field = 'created_at'

    # Toplu işlemler
    def verify_companies(self, request, queryset):
        """Seçili firmaları doğrula"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} firma doğrulandı.')

    verify_companies.short_description = "✓ Seçili firmaları doğrula"

    def unverify_companies(self, request, queryset):
        """Seçili firmaların doğrulamasını kaldır"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} firmanın doğrulaması kaldırıldı.')

    unverify_companies.short_description = "✗ Doğrulamayı kaldır"


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    """Firma çalışanı admin paneli"""

    list_display = (
        'user_email',
        'company_name',
        'role_badge',
        'joined_at_formatted'
    )

    list_filter = ('role', 'joined_at')
    search_fields = (
        'user__email',
        'user__username',
        'company__company_name'
    )
    ordering = ('-joined_at',)

    list_per_page = 50

    # Toplu işlemler
    actions = ['make_admin', 'make_warehouse_manager', 'make_sales_staff']

    fieldsets = (
        ('Firma ve Kullanıcı', {
            'fields': ('company', 'user')
        }),
        ('Rol', {
            'fields': ('role',)
        }),
        ('Tarih', {
            'fields': ('joined_at',)
        }),
    )

    readonly_fields = ('joined_at',)

    def user_email(self, obj):
        """Kullanıcı emaili"""
        return obj.user.email

    user_email.short_description = 'Kullanıcı'

    def company_name(self, obj):
        """Firma adı"""
        return obj.company.company_name

    company_name.short_description = 'Firma'

    def role_badge(self, obj):
        """Rol badge"""
        colors = {
            'admin': '#dc2626',
            'warehouse_manager': '#2563eb',
            'sales_staff': '#10b981',
            'viewer': '#6b7280',
        }
        color = colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_role_display()
        )

    role_badge.short_description = 'Rol'

    def joined_at_formatted(self, obj):
        """Katılma tarihi formatlanmış"""
        return obj.joined_at.strftime('%d.%m.%Y %H:%M')

    joined_at_formatted.short_description = 'Katılma Tarihi'
    joined_at_formatted.admin_order_field = 'joined_at'

    # Toplu işlemler
    def make_admin(self, request, queryset):
        """Seçili kullanıcıları yönetici yap"""
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} kullanıcı yönetici yapıldı.')

    make_admin.short_description = "👑 Yönetici yap"

    def make_warehouse_manager(self, request, queryset):
        """Seçili kullanıcıları depo sorumlusu yap"""
        updated = queryset.update(role='warehouse_manager')
        self.message_user(request, f'{updated} kullanıcı depo sorumlusu yapıldı.')

    make_warehouse_manager.short_description = "📦 Depo sorumlusu yap"

    def make_sales_staff(self, request, queryset):
        """Seçili kullanıcıları satış yetkilisi yap"""
        updated = queryset.update(role='sales_staff')
        self.message_user(request, f'{updated} kullanıcı satış yetkilisi yapıldı.')

    make_sales_staff.short_description = "💼 Satış yetkilisi yap"