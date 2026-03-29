import io
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from checkout.models import Order


def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Get store branding
    store_branding = getattr(settings, 'STORE_BRANDING', {}).get(
        order.store,
        {'name': 'Orderimo', 'primary_color': colors.HexColor('#00b4d8')}
    )
    primary_color = store_branding.get('primary_color', colors.HexColor('#00b4d8'))
    store_name = store_branding.get('name', 'Orderimo')

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(primary_color)
    c.drawString(50, height - 60, store_name)
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(50, height - 85, f"Invoice #{order.order_number}")
    c.drawString(50, height - 105, f"Date: {order.date.strftime('%d %B %Y')}")

    # Customer
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 135, "Bill To:")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 155, order.full_name)
    c.drawString(50, height - 172, order.email)
    address_y = height - 190
    c.drawString(50, address_y, order.street_address1)
    if order.street_address2:
        address_y -= 15
        c.drawString(50, address_y, order.street_address2)
    address_y -= 15
    c.drawString(50, address_y, order.town_or_city)
    if order.county:
        address_y -= 15
        c.drawString(50, address_y, order.county)
    address_y -= 15
    country_text = f"{order.country.name}, {order.postcode}" if order.postcode else f"{order.country.name}"
    c.drawString(50, address_y, country_text)

    # Items
    item_y = address_y - 40
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.white)
    c.rect(50, item_y - 5, width - 100, 25, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.drawString(55, item_y, "Item")
    c.drawString(width - 300, item_y, "Qty")
    c.drawString(width - 200, item_y, "Price")
    c.drawString(width - 100, item_y, "Total")
    c.setFillColor(colors.black)

    item_y -= 30
    total = 0
    for item in order.lineitems.all():
        name = item.product.name
        if item.product_size:
            name += f" (Size: {item.product_size.upper()})"
        c.drawString(55, item_y, name)
        c.drawString(width - 300, item_y, str(item.quantity))
        c.drawString(width - 200, item_y, f"€{item.product.price:.2f}")
        line_total = item.lineitem_total
        c.drawString(width - 100, item_y, f"€{line_total:.2f}")
        total += line_total
        item_y -= 20

    totals_y = item_y - 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 300, totals_y, "Subtotal:")
    c.drawString(width - 100, totals_y, f"€{total:.2f}")
    totals_y -= 20
    c.drawString(width - 300, totals_y, "Delivery:")
    c.drawString(width - 100, totals_y, f"€{order.delivery_cost:.2f}")
    totals_y -= 20
    if order.coupon_discount and order.coupon_discount > 0:
        c.drawString(width - 300, totals_y, "Discount:")
        c.drawString(width - 100, totals_y, f"-€{order.coupon_discount:.2f}")
        totals_y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(width - 300, totals_y, "Grand Total:")
    c.drawString(width - 100, totals_y, f"€{order.grand_total:.2f}")

    # Footer
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    copyright = getattr(settings, 'FOOTER_COPYRIGHT', f"© {order.date.year} {store_name}. All rights reserved.")
    c.drawString(50, 50, copyright)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def download_invoice(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to download invoices.")
    if not request.user.is_staff:
        if order.user_profile is None or order.user_profile.user != request.user:
            return HttpResponseForbidden("You do not have permission to access this invoice.")
    pdf = generate_invoice_pdf(order)
    return FileResponse(pdf, as_attachment=True, filename=f"Invoice-{order.order_number}.pdf")
