

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.utils.html import format_html
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Kullanıcı oluşturma formu - Email zorunlu"""
    email = forms.EmailField(
        required=True,
        label='E-posta',
        help_text='Email adresi zorunludur'
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Kullanıcı düzenleme formu - Email zorunlu"""
    email = forms.EmailField(
        required=True,
        label='E-posta'
    )

    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Gelişmiş kullanıcı admin paneli"""

    # Formlar
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    # Liste görünümü
    list_display = (
        'email',
        'username',
        'phone',
        'user_status',
        'user_type_badge',
        'created_at_formatted'
    )

    list_filter = (
        'user_type',
        'is_staff',
        'is_superuser',
        'is_active',
        'is_email_verified',
        'created_at'
    )

    search_fields = ('email', 'username', 'phone', 'first_name', 'last_name')
    ordering = ('-created_at',)

    # Seçilebilir checkboxlar
    list_select_related = True
    list_per_page = 50

    # Toplu işlemler (Actions)
    actions = [
        'activate_users',
        'deactivate_users',
        'verify_emails',
        'make_seller',
        'make_buyer',
    ]

    # Kullanıcı eklerken gösterilecek alanlar
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone', 'password1', 'password2'),
        }),
        ('Kullanıcı Tipi', {
            'fields': ('user_type',),
        }),
        ('İzinler', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Kullanıcı düzenlerken gösterilecek alanlar
    fieldsets = (
        ('Giriş Bilgileri', {
            'fields': ('email', 'password')
        }),
        ('Kişisel Bilgiler', {
            'fields': ('username', 'first_name', 'last_name', 'phone')
        }),
        ('Kullanıcı Tipi', {
            'fields': ('user_type',),
        }),
        ('Durum', {
            'fields': ('is_active', 'is_email_verified'),
        }),
        ('İzinler', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Önemli Tarihler', {
            'fields': ('last_login', 'created_at'),
        }),
    )

    readonly_fields = ('last_login', 'created_at')

    # Custom display methods
    def user_status(self, obj):
        """Kullanıcı durumu badge"""
        if obj.is_active:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px;">✓ Aktif</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">✗ Pasif</span>'
        )

    user_status.short_description = 'Durum'

    def user_type_badge(self, obj):
        """Kullanıcı tipi badge"""
        colors = {
            'admin': '#dc2626',
            'seller': '#2563eb',
            'buyer': '#10b981',
        }
        color = colors.get(obj.user_type, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_user_type_display()
        )

    user_type_badge.short_description = 'Kullanıcı Tipi'

    def created_at_formatted(self, obj):
        """Oluşturulma tarihi formatlanmış"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Kayıt Tarihi'
    created_at_formatted.admin_order_field = 'created_at'

    # Toplu işlem metodları
    def activate_users(self, request, queryset):
        """Seçili kullanıcıları aktif yap"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} kullanıcı aktif edildi.')

    activate_users.short_description = "✓ Seçili kullanıcıları aktif yap"

    def deactivate_users(self, request, queryset):
        """Seçili kullanıcıları pasif yap"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} kullanıcı pasif edildi.')

    deactivate_users.short_description = "✗ Seçili kullanıcıları pasif yap"

    def verify_emails(self, request, queryset):
        """Seçili kullanıcıların emaillerini doğrula"""
        updated = queryset.update(is_email_verified=True)
        self.message_user(request, f'{updated} kullanıcının emaili doğrulandı.')

    verify_emails.short_description = "📧 Emailleri doğrula"

    def make_seller(self, request, queryset):
        """Seçili kullanıcıları satıcı yap"""
        updated = queryset.update(user_type='seller')
        self.message_user(request, f'{updated} kullanıcı satıcı yapıldı.')

    make_seller.short_description = "🏢 Satıcı yap"

    def make_buyer(self, request, queryset):
        """Seçili kullanıcıları alıcı yap"""
        updated = queryset.update(user_type='buyer')
        self.message_user(request, f'{updated} kullanıcı alıcı yapıldı.')

    make_buyer.short_description = "👤 Alıcı yap"