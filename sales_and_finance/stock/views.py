from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .serializers import RawMilkSerializer, ProductTypeSerializer, ProductStockSerializer
from .models import RawMilk, ProductType, ProductStock


# Untuk list & create RawMilk (tanpa `pk`)
class RawMilkListCreateView(generics.ListCreateAPIView):
    queryset = RawMilk.objects.all()
    serializer_class = RawMilkSerializer

# Untuk retrieve, update, dan delete RawMilk (dengan `pk`)
class RawMilkRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RawMilk.objects.all()
    serializer_class = RawMilkSerializer

# Untuk list & create ProductType (tanpa `pk`)
class ProductTypeCreateView(generics.ListCreateAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

# Untuk retrieve, update, dan delete ProductType (dengan `pk`)
class ProductTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

class ProductStockCreateView(generics.ListCreateAPIView):
    queryset = ProductStock.objects.all()
    serializer_class = ProductStockSerializer

# class StockHistoryViewSet(viewsets.ModelViewSet):
#     queryset = StockHistory.objects.all()
#     serializer_class = StockHistorySerializer