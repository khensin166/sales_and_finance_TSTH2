# sales/tasks.py
from django.utils import timezone
from django.db import transaction
from sales.models import Order
from notifications.models import Notification
from stock.models import User
from datetime import timedelta
import logging

logger = logging.getLogger('sales')

def check_pending_orders():
    try:
        logger.info("Starting pending orders check at %s WIB", 
                    timezone.now().astimezone(timezone.get_current_timezone()))
        now = timezone.now()
        two_hours_ago = now - timedelta(hours=2)
        four_hours_ago = now - timedelta(hours=4)

        # Ambil order dengan status 'Requested'
        pending_orders = Order.objects.filter(
            status='Requested',
            created_at__lt=now
        )
        logger.info("Found %d pending orders to check", pending_orders.count())

        if not pending_orders.exists():
            logger.info("No pending orders to process")
            return

        # Ambil semua admin
        admins = User.objects.filter(role_id=1)
        if not admins.exists():
            logger.error("No admin users found for notifications")
            return

        with transaction.atomic():
            for order in pending_orders:
                time_since_creation = now - order.created_at
                created_at_wib = order.created_at.astimezone(timezone.get_current_timezone())
                logger.debug("Checking order %s: created_at=%s, time_since_creation=%s",
                             order.order_no, created_at_wib, time_since_creation)

                # Pengecekan untuk 2 jam
                if order.created_at <= two_hours_ago and time_since_creation < timedelta(hours=4):
                    if not Notification.objects.filter(
                        order=order,
                        type='ORDER_PENDING_2H'
                    ).exists():
                        for admin in admins:
                            Notification.objects.create(
                                order_id=order.id,
                                user_id=admin.id,
                                message=f"Order {order.order_no} telah menunggu selama 2 jam sejak "
                                        f"{created_at_wib.strftime('%Y-%m-%d %H:%M:%S %Z')}. "
                                        f"Harap segera!",
                                type='admin',
                                is_read=False,
                                created_at_wib=timezone.now().astimezone(
                                    timezone.get_current_timezone()
                                )
                            )
                            logger.info("Sent 2-hour pending order warning for order %s to user %s",
                                        order.order_no, admin.id)
                    else:
                        logger.debug("Skipped ORDER_PENDING_2H notification for order %s: already notified",
                                     order.order_no)

                # Pengecekan untuk 4 jam
                elif order.created_at <= four_hours_ago:
                    if not Notification.objects.filter(
                        order=order,
                        type='ORDER_PENDING_4H'
                    ).exists():
                        for admin in admins:
                            Notification.objects.create(
                                order_id=order.id,
                                user_id=admin.id,
                                message=f"Order {order.order_no} telah menunggu selama lebih dari 4 jam sejak "
                                        f"{created_at_wib.strftime('%Y-%m-%d %H:%M:%S %Z')}. "
                                        f"Harap segera ditindaklanjuti!",
                                type='ORDER_PENDING_4H',
                                is_read=False,
                                created_at_wib=timezone.now().astimezone(
                                    timezone.get_current_timezone()
                                )
                            )
                            logger.info("Sent 4-hour pending order warning for order %s to user %s",
                                        order.order_no, admin.id)
                    else:
                        logger.debug("Skipped ORDER_PENDING_4H notification for order %s: already notified",
                                     order.order_no)

    except Exception as e:
        logger.error("Error in check_pending_orders: %s", str(e), exc_info=True)