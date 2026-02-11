from rest_framework import serializers
from .models import Address, City, District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'plate_code']


class CityWithDistrictsSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'plate_code', 'districts']


class AddressSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'title', 'full_name', 'phone',
            'city', 'city_name', 'district', 'district_name',
            'neighborhood', 'address_line', 'postal_code',
            'is_default', 'is_active', 'full_address', 'created_at'
        ]

    def validate_phone(self, value):
        import re
        phone = re.sub(r'[^0-9]', '', value)
        if len(phone) < 10:
            raise serializers.ValidationError("Geçerli bir telefon numarası girin.")
        return value

    def validate(self, data):
        city = data.get('city')
        district = data.get('district')
        if city and district and district.city != city:
            raise serializers.ValidationError({'district': 'İlçe seçilen ile ait değil.'})
        return data


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'address_type', 'title', 'full_name', 'phone',
            'city', 'district', 'neighborhood', 'address_line',
            'postal_code', 'is_default'
        ]
