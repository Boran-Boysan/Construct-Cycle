from django.contrib import admin
from .models import Address, City, District


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'plate_code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'plate_code']
    inlines = [DistrictInline]


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'is_active']
    list_filter = ['city', 'is_active']
    search_fields = ['name']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'city', 'district', 'is_default', 'is_active']
    list_filter = ['address_type', 'is_default', 'is_active', 'city']
    search_fields = ['title', 'full_name', 'user__email']
    raw_id_fields = ['user']
