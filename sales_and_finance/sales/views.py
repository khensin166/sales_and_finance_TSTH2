from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer

# List all orders & Create a new order
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

# Retrieve, Update, Delete an order
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Pastikan update status hanya jika shipping_cost bertambah
        if 'shipping_cost' in request.data and instance.status == 'Requested':
            instance.status = 'Processed'

        # Validasi sebelum menyelesaikan pesanan
        if request.data.get('status') == 'Completed' and not request.data.get('payment_method'):
            return Response({"error": "Metode pembayaran harus diisi sebelum menyelesaikan pesanan."}, status=status.HTTP_400_BAD_REQUEST)

        # Simpan instance setelah perubahan
        instance.save()

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
