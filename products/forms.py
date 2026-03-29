from django import forms
from django.core.validators import MinValueValidator
from decimal import Decimal

from .widgets import CustomClearableFileInput
from .models import Product, Category


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} ★') for i in range(1, 6)],
        label='Rating',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comment = forms.CharField(
        label='Comment',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Share your thoughts about this product...'
        })
    )


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['stock_quantity', 'low_stock_threshold', 'views_count', 'sku', 'featured', 'new_arrival', 'best_seller', 'weight_kg']

    image = forms.ImageField(
        label='Image', required=False, widget=CustomClearableFileInput
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        # Add non-negative price validation
        self.fields['price'].validators = [MinValueValidator(Decimal('0.01'))]
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-2'
