from rest_framework import serializers
from .models import RawMilk, ProductType, ProductStock, StockHistory

class RawMilkSerializer(serializers.ModelSerializer):

    class Meta:
        model = RawMilk
        fields = ['cow_id', 'production_time', 'expiration_time', 'volume_liters', 'status']


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'


class ProductStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStock
        fields = '__all__'


# class StockHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StockHistory
#         fields = '__all__'