from django.db import models
from stock.models import ProductStock
import uuid

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
    quantity = models.CharField(max_length=20)
    location = models.CharField(max_length=255, blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        """ Generate order_no dan hitung total_price sebelum menyimpan """
        if not self.order_no:
            self.order_no = f"ORD{uuid.uuid4().hex[:6].upper()}"  # ID unik

        # Hitung total harga otomatis
        self.total_price = self.product_price + self.shipping_cost

        # Update status jika shipping cost diisi
        if self.shipping_cost > 0 and self.status == 'Requested':
            self.status = 'Processed'

        # Validasi sebelum menyelesaikan pesanan
        if self.status == 'Completed' and not self.payment_method:
            raise ValueError("Metode pembayaran harus diisi sebelum menyelesaikan pesanan.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_no} - {self.customer_name}" # pylint: disable=no-member
        # return f"Order by {self.customer_name}"

class SalesTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transaction')
    product_stock = models.ForeignKey(ProductStock, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    objects = models.Manager()
    def __str__(self):
        return f"Transaction {self.pk} - Order {self.order.id}" # pylint: disable=no-member
        # return f"Transaction {self.id} - Order {self.order.id}"