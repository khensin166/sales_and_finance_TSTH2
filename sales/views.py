from django.db.models import Sum
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend # pylint: disable=import-error
from rest_framework import status
from rest_framework import serializers
from .models import Order, SalesTransaction
from .serializers import OrderSerializer, SalesTransactionSerializer
from .filters import SalesTransactionFilter
import logging

logger = logging.getLogger(__name__)

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        try:
            instance = serializer.save()
            logger.info(f"Order created successfully: {instance.order_no}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            logger.error(f"Validation error during order creation: {str(e)}")
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error during order creation: {str(e)}")
            return Response({
                "error": "An unexpected error occurred while creating the order."
            }, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializer)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_update(self, serializer):
        try:
            instance = self.get_object()
            if instance.status in ['Completed', 'Cancelled']:
                logger.warning(f"Attempt to update order {instance.order_no} with status {instance.status}")
                return Response({
                    "error": "Pesanan yang sudah selesai atau dibatalkan tidak bisa diperbarui."
                }, status=status.HTTP_400_BAD_REQUEST)
            instance = serializer.save()
            logger.info(f"Order updated successfully: {instance.order_no}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            logger.error(f"Validation error during order update: {str(e)}")
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error during order update: {str(e)}")
            return Response({
                "error": "An unexpected error occurred while updating the order."
            }, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        try:
            order_no = instance.order_no
            instance.delete()
            logger.info(f"Order deleted successfully: {order_no}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error during order deletion: {str(e)}")
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return self.perform_update(serializer)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

class SalesTransactionListView(generics.ListAPIView):
    queryset = SalesTransaction.objects.all().order_by('-transaction_date')
    serializer_class = SalesTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SalesTransactionFilter
    ordering_fields = ['transaction_date']
    ordering = ['-transaction_date']

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.info("Successfully retrieved sales transaction list")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving sales transaction list: {str(e)}")
            return Response({
                "error": "An unexpected error occurred while retrieving sales transactions."
            }, status=status.HTTP_400_BAD_REQUEST)

class SalesTransactionDetailView(generics.RetrieveAPIView):
    queryset = SalesTransaction.objects.all()
    serializer_class = SalesTransactionSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Successfully retrieved sales transaction {instance.id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving sales transaction {instance.id}: {str(e)}")
            return Response({
                "error": "An unexpected error occurred while retrieving the sales transaction."
            }, status=status.HTTP_400_BAD_REQUEST)