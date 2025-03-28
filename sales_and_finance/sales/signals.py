from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def handle_order_completion(sender, instance, **kwargs):
    if instance.status == "Completed":
        instance.process_completion()