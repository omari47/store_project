from django import forms
from django.contrib.auth import get_user_model

from .models import Product
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SaleForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label="Select a product, required=True")
    quantity = forms.IntegerField(min_value=1, label='Quantity, required=True')
    payment_method = forms.ChoiceField(choices=[('mpesa', 'MPESA'), ('cash', 'Cash'), ('card', 'Card')], label='Payment Method')
    sale_price = forms.DecimalField(max_digits=10, decimal_places=2, required=True)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'manufacture_date', 'expiry_date', 'price', 'sku']



from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)