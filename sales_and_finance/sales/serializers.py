from rest_framework import serializers
from .models import Order, SalesTransaction


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def validate(self, data):
        if data.get('status') == 'Completed' and not data.get('payment_method'):
            raise serializers.ValidationError({"payment_method": "Metode pembayaran harus diisi sebelum menyelesaikan pesanan."})
        return data

    def update(self, instance, validated_data):
        """ Update semua field yang dikirim dalam request """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Panggil metode save() untuk memastikan total_price dihitung ulang
        instance.save()
        return instance


class SalesTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTransaction
        fields = '__all__'
