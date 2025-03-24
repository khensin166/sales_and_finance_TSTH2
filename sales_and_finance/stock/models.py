from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
# Model Produksi Susu Mentah
class RawMilk(models.Model):
    objects = models.Manager()
    
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

    objects = models.Manager()
    def __str__(self):
        return f"{self.product_name}"


# Model Stok Produk
class ProductStock(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    initial_quantity = models.IntegerField()
    quantity = models.IntegerField()
    production_at = models.DateTimeField(default=timezone.now)
    expiry_at = models.DateTimeField()
    status = models.CharField(max_length=60)
    total_milk_used = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    def __str__(self):
        return f"{self.product_type}"

    def deduct_raw_milk(self):
        """ Mengurangi stok susu mentah berdasarkan total_milk_used tanpa perhitungan tambahan """
        if self.total_milk_used <= 0:
            return  # Jika tidak ada susu yang digunakan, keluar dari fungsi

        # Ambil stok susu dari yang paling lama (FIFO)
        raw_milk_entries = RawMilk.objects.filter(status="fresh").order_by("production_time")

        total_available = sum(entry.volume_liters for entry in raw_milk_entries)
        if self.total_milk_used > total_available:
            raise ValidationError("Stok susu mentah tidak mencukupi untuk produksi!")

        remaining_milk_needed = self.total_milk_used

        with transaction.atomic():
            for entry in raw_milk_entries:
                if remaining_milk_needed <= 0:
                    break

                if entry.volume_liters <= remaining_milk_needed:
                    remaining_milk_needed -= entry.volume_liters
                    entry.volume_liters = 0
                    entry.status = "used"
                else:
                    entry.volume_liters -= remaining_milk_needed
                    remaining_milk_needed = 0

                entry.save()

    def save(self, *args, **kwargs):
        """ Periksa apakah produk sudah expired saat disimpan """
        if self.expiry_at < timezone.now():
            self.status = "expired"
            # self.quantity = 0  # Set stok menjadi 0 jika expired
            StockHistory.objects.create(
                product_stock=self,
                change_type="expired",
                quantity_change=self.quantity
            )

        super().save(*args, **kwargs)

    @classmethod
    def check_expired_products(cls):
        """ Otomatis set produk expired jika sudah melewati tanggal kadaluarsa """
        expired_products = cls.objects.filter(expiry_at__lt=timezone.now(), status="available")
        
        with transaction.atomic():
            for product in expired_products:
                product.status = "expired"
                StockHistory.objects.create(
                    product_stock=product,
                    change_type="expired",
                    quantity_change=product.quantity
                )
                # product.quantity = 0  # Set stok menjadi 0
                product.save()

    @classmethod
    def sell_product(cls, product_type, quantity):
        """ Jual produk berdasarkan FIFO jika tersedia """
        available_stocks = cls.objects.filter(product_type=product_type, status="available", quantity__gt=0).order_by("production_at")

        remaining = quantity
        with transaction.atomic():
            for stock in available_stocks:
                if remaining <= 0:
                    break

                sold_quantity = min(stock.quantity, remaining)
                remaining -= sold_quantity
                stock.quantity -= sold_quantity

                if stock.quantity == 0:
                    stock.status = "sold_out"

                StockHistory.objects.create(
                    product_stock=stock,
                    change_type="sold",
                    quantity_change=sold_quantity
                )

                stock.save()

        if remaining > 0:
            raise ValidationError("Stok tidak mencukupi!")

# Model Histori Perubahan Stok
class StockHistory(models.Model):
    product_stock = models.ForeignKey(ProductStock, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20, choices=[("sold", "Sold"), ("expired", "Expired")])  # 'Added' atau 'Removed'
    quantity_change = models.IntegerField()
    change_date = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    def __str__(self):
        return f"{self.change_type} {self.quantity_change}"
