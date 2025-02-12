from django.db.models import Sum, Count, DateField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from order.models import Order
from django.utils.timezone import make_aware
from datetime import datetime



def get_sales_data(period=None, start_date=None, end_date=None):
    """
    Helper function to filter and aggregate sales data based on the specified period or date range.
    """
    # Filter completed and paid orders
    orders = Order.objects.filter(status="completed", is_paid=True)

    if start_date and end_date:
        # Custom date range filtering
        orders = orders.filter(ordered_date__range=[start_date, end_date])
        print(orders.exists())

        # Aggregate totals for the date range
        return {
            "total_sales": orders.aggregate(Sum("total_price"))["total_price__sum"] or 0,
            "total_orders": orders.count(),
        }

    elif period:
        # Determine date truncation based on the period
        if period == "day":
            orders = orders.annotate(period=TruncDay("ordered_date"))
        elif period == "week":
            orders = orders.annotate(period=TruncWeek("ordered_date"))
        elif period == "month":
            orders = orders.annotate(period=TruncMonth("ordered_date"))
        else:
            raise ValueError("Invalid period. Allowed values are 'day', 'week', or 'month'.")

        # Group by the truncated period and aggregate totals
        return list(
            orders.values("period")
            .annotate(total_sales=Sum("total_price"), total_orders=Count("id"))
            .order_by("period")
        )

    else:
        raise ValueError("You must specify either a period or a valid date range.")
