from rest_framework import serializers
from .models import Order, SalesTransaction, OrderItem, ProductStock


class OrderItemSerializer(serializers.ModelSerializer):
    product_stock = serializers.PrimaryKeyRelatedField(queryset=ProductStock.objects.all())  # Pastikan menggunakan model yang benar

    class Meta:
        model = OrderItem
        fields = ['id', 'product_stock', 'quantity', 'total_price']
        read_only_fields = ['total_price'] # Tambahkan product_stock agar tidak bisa diubah setelah dibuat

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_no', 'customer_name', 'email', 'phone_number', 
                  'location', 'shipping_cost', 'total_price', 'status', 
                  'payment_method', 'created_at', 'order_items']
        read_only_fields = ['order_no', 'total_price']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items', [])

        if not order_items_data:
            raise serializers.ValidationError({"order_items": "Minimal satu item harus dipesan."})

        order = Order.objects.create(**validated_data)

        order_items = []
        for item_data in order_items_data:
            # Ambil objek product_stock berdasarkan ID
            product_stock = item_data.pop('product_stock')  # Sekarang ini adalah ID
            product_stock_obj = ProductStock.objects.get(id=product_stock.id)  # Ambil objek

            if item_data['quantity'] > product_stock_obj.quantity:
                raise serializers.ValidationError({"order_items": f"Stok {product_stock_obj} tidak mencukupi."})

            order_item = OrderItem.objects.create(order=order, product_stock=product_stock_obj, **item_data)
            order_items.append(order_item)

        order.total_price = sum(item.total_price for item in order_items) + order.shipping_cost
        order.save()
        return order

    # def update(self, instance, validated_data):
    #     """ Update Order dan OrderItems jika ada perubahan """
    #     new_status = validated_data.get("status", instance.status)

    #     print("DEBUG: validated_data", validated_data)  # Tambahkan debug log

    #     if new_status == "Completed" and not instance.payment_method:
    #         raise serializers.ValidationError({"payment_method": "Metode pembayaran harus diisi sebelum menyelesaikan pesanan."})

    #     order_items_data = validated_data.pop("order_items", None)

    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     if order_items_data is not None:
    #         instance.order_items.all().delete()  # Hapus item lama
    #         order_items = []
    #         for item_data in order_items_data:
    #             product_stock = item_data["product_stock"]
    #             if item_data["quantity"] > product_stock.quantity:
    #                 raise serializers.ValidationError({"order_items": f"Stok {product_stock} tidak mencukupi."})
    #             order_item = OrderItem.objects.create(order=instance, **item_data)
    #             order_items.append(order_item)

    #         instance.total_price = sum(item.total_price for item in order_items) + instance.shipping_cost

    #     instance.save()
    #     return instance

    def update(self, instance, validated_data):
        new_status = validated_data.get("status", instance.status)
        payment_method = validated_data.get("payment_method", instance.payment_method)

        if new_status == "Completed" and not payment_method:
            raise serializers.ValidationError({"payment_method": "Metode pembayaran harus diisi sebelum menyelesaikan pesanan."})

        order_items_data = validated_data.pop("order_items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# bagaimana caranya jika saya ingin ketika order statusnya berubah menjadi processed maka data akan otomatis tertambah ke sales transaction dan product stock akan otomatis berkurang dan kebetulan sudah ada fungsi salesnya