from datetime import timezone
from django.utils import timezone


from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Explicitly setting related_name to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
    )

    def __str__(self):
        return self.username
# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=0)
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_in_stock = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default="In Stock")

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.status = "Out of Stock"
        elif self.expiry_date < timezone.now().date():
            self.status = "Expired"
        else:
            self.status = "In Stock"
        super().save(*args, **kwargs)




    def __str__(self):
        return f'{self.name} {self.sku}'

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        unique_together = (('name', 'sku'),)
        ordering = ('name',)
        db_table = 'products'

# Sales Model
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    PAYMENT_CHOICES = [
        ('mpesa', 'MPESA'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f' Sale of {self.product.name}- {self.quantity} units  {self.sale_date}'

# Inventory Log Model
class InventoryLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='logs')
    quantity_changed = models.IntegerField()
    status = models.CharField(max_length=20) # In stock Out of stock ,
    updated_at = models.DateTimeField(auto_now=True)
    change_date = models.DateTimeField(auto_now_add=True)
    REASON_CHOICES = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
    ]
    change_reason = models.CharField(max_length=20, choices=REASON_CHOICES)

     # write a function for auto out of stock here as a property
    def __str__(self):
        return f"{self.product.name} - {self.quantity_changed} units"

    class Meta:
        verbose_name = 'Inventory Log'
        verbose_name_plural = 'Inventory Logs'
        ordering = ('product',)
        db_table = 'inventory_logs'

# Notification Model
class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification {self.message[:50]}'
# Payment Model
class Payment(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, choices=Sale.PAYMENT_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=30, blank=True, null=True)

    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        db_table = 'payments'

    def __str__(self):
        return f"Payment for Sale {self.sale.id} - {self.code} - {self.amount}"

# Analytics Data Model
class Analytics(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='analytics')
    total_sales = models.PositiveIntegerField(default=0)
    most_sold_date = models.DateTimeField(blank=True, null=True)
    least_sold_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Analytics for {self.product.name}"