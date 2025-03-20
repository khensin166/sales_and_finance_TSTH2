from django.db import models
from django.utils import timezone

# Create your models here.
# Model Produksi Susu Mentah
class RawMilk(models.Model):
    cow_id = models.IntegerField()
    production_time = models.DateTimeField()
    expiration_time = models.DateTimeField()
    volume_liters = models.DecimalField(max_digits=5, decimal_places=2)
    previous_volume = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='fresh')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cow {self.cow_id} - {self.volume_liters}L"


# Model Tipe Produk
class ProductType(models.Model):
    product_name = models.CharField(max_length=255)
    product_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name}"


# Model Stok Produk
class ProductStock(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    initial_quantity = models.IntegerField()
    quantity = models.IntegerField()
    production_at = models.DateField(default=timezone.now)
    expiry_at = models.DateField()
    status = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_type}"


# Model Histori Perubahan Stok
class StockHistory(models.Model):
    product_stock = models.ForeignKey(ProductStock, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20)  # 'Added' atau 'Removed'
    quantity_change = models.IntegerField()
    change_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.change_type} {self.quantity_change}"
