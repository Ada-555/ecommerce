# Generated manually for performance indexes
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0003_product_download_file_product_is_digital_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['stock_quantity'], name='stock_qty_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['featured'], name='featured_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category'], name='category_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['rating'], name='rating_idx'),
        ),
        migrations.AddIndex(
            model_name='productvariant',
            index=models.Index(fields=['sku'], name='variant_sku_idx'),
        ),
    ]
