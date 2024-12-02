from django import forms
from .models import Product

class SaleForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label="Select a product, required=True")
    quantity = forms.IntegerField(min_value=1, label='Quantity, required=True')
    payment_method = forms.ChoiceField(choices=[('mpesa', 'MPESA'), ('cash', 'Cash'), ('card', 'Card')], label='Payment Method')
    sale_price = forms.DecimalField(max_digits=10, decimal_places=2, required=True)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'manufacture_date', 'expiry_date', 'price', 'sku']
