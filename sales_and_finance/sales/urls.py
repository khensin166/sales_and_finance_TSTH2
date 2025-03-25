from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),

    # GET /orders/ → List semua order.

    # POST /orders/ → Membuat order baru.

    # GET /orders/{id}/ → Melihat detail order tertentu.

    # PUT/PATCH /orders/{id}/ → Mengupdate order (contohnya menambah biaya pengiriman).

    # DELETE /orders/{id}/ → Menghapus order.
]
    # Menyajikan file media hanya dalam mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
