from django.db import models
from stock.models import ProductStock, StockHistory
from django.core.exceptions import ValidationError
import uuid
from django.db import transaction


# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('Requested', 'Requested'),  # Status default ketika order dibuat
        ('Processed', 'Processed'),  # Setelah produk dicek dan biaya pengiriman ditambahkan
        ('Completed', 'Completed'),  # Setelah pembayaran dipilih
        ('Cancelled', 'Cancelled'),  # Jika dibatalkan
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('', 'Select Payment Method'),  # Default kosong, tidak boleh langsung completed
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Bank Transfer', 'Bank Transfer'),
    ]

    order_no = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):

        if not self.order_no:
            self.order_no = f"ORD{uuid.uuid4().hex[:6].upper()}"  # ID unik

        is_status_changed = self.pk is not None and Order.objects.get(pk=self.pk).status != self.status

        if is_status_changed and self.status == 'Completed':
            if not self.payment_method:
                raise ValidationError("Metode pembayaran harus dipilih sebelum menyelesaikan order.")

        super().save(*args, **kwargs)

        if is_status_changed and self.status == 'Completed':
            self.process_completion()

    def update_total_price(self):
        """ Hitung total harga berdasarkan OrderItem """
        total = sum(item.total_price for item in self.order_items.all()) # pylint: disable=no-member
        self.total_price = total + self.shipping_cost
        super().save(update_fields=['total_price'])

    def process_completion(self):
        """ Buat transaksi penjualan dan perbarui stok saat pesanan selesai """
        with transaction.atomic():
            for item in self.order_items.all():
                # Gunakan method sell_product dari ProductStock
                ProductStock.sell_product(item.product_stock.product_type, item.quantity)

                # Buat transaksi penjualan
                SalesTransaction.objects.create(
                    order=self,
                    product_stock=item.product_stock,
                    quantity=item.quantity,
                    total_price=item.total_price
                )

    def __str__(self):
        return f"Order {self.order_no} - {self.customer_name}"


class OrderItem(models.Model):
    """ Menyimpan setiap produk yang dipesan dalam order """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product_stock = models.ForeignKey(ProductStock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        """ Hitung total harga sebelum menyimpan """
        self.price_per_unit = self.product_stock.product_type.price   # pylint: disable=no-member
        self.total_price = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

        # Setelah menyimpan OrderItem, update total_price Order
        self.order.update_total_price() # pylint: disable=no-member


    def __str__(self):
        return f"{self.quantity} x {self.product_stock} in {self.order.order_no}" # pylint: disable=no-member

class SalesTransaction(models.Model):
    """ Menyimpan transaksi penjualan yang dihasilkan dari Order """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    product_stock = models.ForeignKey(ProductStock, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    objects = models.Manager()

    def __str__(self):
        return f"Transaction {self.pk} - Order {self.order.order_no}" # pylint: disable=no-member