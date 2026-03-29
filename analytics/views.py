from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from decimal import Decimal
from checkout.models import Order, OrderLineItem


@staff_member_required
def analytics_dashboard(request):
    """Display key analytics metrics and top products."""
    # Total Revenue: sum of grand_total for all delivered or completed orders (excluding cancelled)
    # Typically revenue counts paid and delivered orders. We'll sum grand_total for orders with payment_status='paid' and status='delivered' or maybe all paid.
    # Let's include all orders with payment_status='paid' (including delivered, shipped, confirmed).
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')

    # Average Order Value: total revenue / number of paid orders
    paid_orders_count = Order.objects.filter(payment_status='paid').count()
    avg_order_value = total_revenue / paid_orders_count if paid_orders_count > 0 else Decimal('0.00')

    # Orders by Status: count orders by status (excluding cancelled maybe)
    orders_by_status = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    # Convert to list of dicts for template
    status_labels = []
    status_counts = []
    for item in orders_by_status:
        # capitalize status label
        label = dict(Order._meta.get_field('status').choices)[item['status']]
        status_labels.append(label)
        status_counts.append(item['count'])

    # Top 10 Products: by quantity sold in paid orders
    # Join OrderLineItem with Order where Order.payment_status='paid'
    top_products = OrderLineItem.objects.filter(
        order__payment_status='paid'
    ).values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('lineitem_total')
    ).order_by('-total_quantity')[:10]

    context = {
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'top_products': top_products,
    }
    return render(request, 'analytics/dashboard.html', context)