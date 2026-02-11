from django.contrib import admin
from .models import ReturnRequest, ReturnItem, Refund

class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'order', 'user', 'status', 'created_at']
    inlines = [ReturnItemInline]

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['return_request', 'amount', 'status']
