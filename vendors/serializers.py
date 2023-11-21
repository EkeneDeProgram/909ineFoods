from rest_framework import serializers
from .models import Location, Vendor, Category, MenuItem


# Location model serializer
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("id", "street", "city", "state")


# Vendor model serializer
class VendorSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, required=False)

    class Meta:
        model = Vendor
        fields = ("id", "name", "description", "locations", "contact_info", "email")

    def create(self, validated_data):
        locations_data = validated_data.pop("locations", [])
        vendor = Vendor.objects.create(**validated_data)

        for location_data in locations_data:
            Location.objects.create(vendor=vendor, **location_data)

        return vendor
    

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.contact_info = validated_data.get("contact_info", instance.contact_info)

        locations_data = validated_data.get("locations", [])
        instance.locations.all().delete()

        for location_data in locations_data:
            Location.objects.create(vendor=instance, **location_data)

        instance.save()
        return instance
    

# Category model serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "parent_category")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["parent_category"] = CategorySerializer(instance.parent_category).data
        return representation
    
    
# MenuItem model serializer
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("id", "vendor", "category", "name", "description", "price")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["vendor"] = VendorSerializer(instance.vendor).data
        representation["category"] = CategorySerializer(instance.category).data
        return representation
