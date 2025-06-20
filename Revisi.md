============================ 20-06-2025 =============================
Repair Product Type Function

-> Perubahan model product type jadi seperti ini 

product_name = models.CharField(max_length=255, unique=True)

-> Rubah juga di databasenya

ALTER TABLE product_type
ADD CONSTRAINT unique_product_name UNIQUE (product_name);

