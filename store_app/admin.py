from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Category, Product, Sale, InventoryLog, Notification, Payment, Analytics
admin.site.site_header = 'Store MIS'
admin.site.site_title = ' Manage Store MIS'
# Customizing the User model in the admin panel
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'role']
    search_fields = ['username', 'email', 'phone_number']
    list_per_page = 30

# Registering the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name',]

# Registering the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'quantity', 'is_in_stock', 'price', 'expiry_date', 'manufacture_date']
    list_filter = ['category', 'is_in_stock', 'expiry_date']
    search_fields = ['name', 'sku']
    ordering = ['name',]
    list_per_page = 30

# Registering the Sale model
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'total_price', 'sale_date', 'payment_method', 'transaction_id']
    list_filter = ['sale_date', 'payment_method']
    search_fields = ['product__name', 'transaction_id']

# Registering the Inventory Log model
@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_changed', 'status', 'change_reason', 'updated_at']
    list_filter = ['change_reason', 'status', 'updated_at']
    search_fields = ['product__name',]

# Registering the Notification model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['message',]

# Registering the Payment model
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['sale', 'amount', 'payment_date', 'payment_method', 'transaction_id', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['transaction_id', 'sale__product__name']
    list_per_page = 25

# Registering the Analytics model
@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_sales', 'most_sold_date', 'least_sold_date']
    search_fields = ['product__name',]
