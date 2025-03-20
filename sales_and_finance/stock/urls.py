from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    
    # ================================ RAW MILK ========================
    path("rawmilk", views.RawMilkListCreateView.as_view(), name="rawmilk-view-create"), # GET (all) & POST
    path("rawmilk/<int:pk>/", views.RawMilkRetrieveUpdateDestroyView.as_view(), name="rawmilk-detail"), # GET (one), PUT, PATCH, DELETE
    # GET	/rawmilk/	Ambil semua data RawMilk
    # POST	/rawmilk/	Tambah data baru
    # GET	/rawmilk/1/	Ambil data dengan id=1
    # PUT	/rawmilk/1/	Update seluruh data id=1
    # PATCH	/rawmilk/1/	Update sebagian data id=1
    # DELETE	/rawmilk/1/	Hapus data id=1
    # ==================================================================


    # ================================ Product Type ========================
    path("producttype", views.ProductTypeCreateView.as_view(), name="product-type-view-create"), # GET (all) & POST
    path("producttype/<int:pk>/", views.ProductTypeRetrieveUpdateDestroyView.as_view(), name="product-type-detail"), # GET (one), PUT, PATCH, DELETE


    # ================================ Product Stok ========================
    path("productstock", views.ProductStockCreateView.as_view(), name="product-stock-view-create"), # GET (all) & POST
]
    # Menyajikan file media hanya dalam mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
