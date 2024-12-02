"""
URL configuration for store_three project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from store_app import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    # View product details
    path('product/<int:product_id>/', views.view_details, name='view_details'),

    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),  # Edit product
    path('product/add_stock/<int:product_id>/', views.add_stock, name='add_stock'),  # Add stock
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),  # Delete product
    path('manage/', views.stock_management, name='stock_management'),
    path('sales/log/', views.log_sale, name='log_sale'),
    path('analytics', views.analytics, name='analytics'),
    path('product/details', views.product_details, name='product_details'),
    path('admin/', admin.site.urls),
]