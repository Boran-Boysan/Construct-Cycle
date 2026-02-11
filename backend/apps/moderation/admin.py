from django.contrib import admin
from .models import Report, UserWarning, UserBan

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_number', 'reporter', 'target_type', 'reason', 'status']

@admin.register(UserWarning)
class UserWarningAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'created_at']

@admin.register(UserBan)
class UserBanAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'expires_at']
