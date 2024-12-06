from datetime import datetime
from itertools import product

from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth import authenticate, login, logout

from django.db.models import Sum, F, Count

from django.shortcuts import render, get_object_or_404, redirect

from store_app.forms import SaleForm, ProductForm, LoginForm
from store_app.models import Product, Sale, InventoryLog, Payment, Analytics
from django.db.models.functions import TruncDate
from .forms import UserRegistrationForm
from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Product, Sale, InventoryLog
from .forms import SaleForm

# Create your views here.
@login_required
def dashboard(request):
    # Example analytics data for the dashboard
    total_products = Product.objects.count()
    out_of_stock = Product.objects.filter(quantity=0).count()
    low_stock = Product.objects.filter(quantity__lte=10).count()  # Customize threshold

    return render(request, 'dashboard.html', {
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'products': Product.objects.all()[:10]  # Show top 10 products (example)
    })

    # return render(request, 'dashboard.html')


@login_required
def product_list(request):
    products = Product.objects.all()

    return render(request, 'product_list.html', {'products': products})


@login_required
def log_sale(request):
    products = Product.objects.all()  # Fetch all products for display

    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            payment_method = form.cleaned_data['payment_method']

            # Ensure sale price cannot be less than the actual price of the product
            total_price = product.price * quantity
            if total_price < product.price:
                messages.error(request, f'Error: Sale price cannot be less than the product price.')
                return redirect('log_sale')

            # Ensure that quantity does not exceed available stock
            if product.quantity >= quantity:
                # Update product stock
                product.quantity -= quantity
                product.save()
                messages.success(request, f'Sale {product.name} has been added to the sale.')
                # Create a Sale record
                sale = Sale.objects.create(
                    product=product,
                    quantity=quantity,
                    total_price=total_price,
                    payment_method=payment_method
                )

                # Log the inventory change
                InventoryLog.objects.create(
                    product=product,
                    quantity_changed=-quantity,
                    status="Out of Stock" if product.quantity == 0 else "In Stock",
                    change_reason="Sale"
                )

                # Update sales statistics (optional)
                today = timezone.now().date()
                analytics, created = Analytics.objects.get_or_create(product=product)
                analytics.total_sales += quantity
                if created or sale.sale_date.date() == today:
                    analytics.save()

                # Success message
                messages.success(request,
                                 f'Sale of {quantity} units of {product.name} logged successfully. Total price: {total_price}.')
                return redirect('product_list')

            else:
                # Error message for insufficient stock
                messages.error(request, f'Not enough stock for {product.name}. Only {product.quantity} left.')

    else:
        form = SaleForm()

    return render(request, 'log_sale.html', {'products': products, 'form': form})





@login_required
def stock_management(request):
    search_query = request.GET.get('search', '')  # Capture the search query
    products = Product.objects.filter(
        Q(name__icontains=search_query) | Q(sku__icontains=search_query)
    ).all()  # Filter products by name or SKU

    # Set up pagination
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'stock_management.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

@login_required
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {'product': product})


@login_required
def analytics(request):
    most_sold = Product.objects.order_by('-quantity')[:5]
    least_sold = Product.objects.order_by('quantity')[:5]

    return render(request, 'analytics.html', {
        'most_sold': most_sold,
        'least_sold': least_sold
    })
    # return render(request, 'analytics.html')


@login_required
def view_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {'product': product})


@login_required

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()

            return redirect('product_list')  # Redirect to the product list after saving
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})


@login_required
@permission_required("Store_App.add_product")
def add_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity_to_add = int(request.POST['quantity'])  # Get the quantity from the form
        product.quantity += quantity_to_add
        product.save()
        messages.success(request, f'Product {product.name} has been updated.')
        return redirect('product_list')  # Redirect to product list after adding stock

    return render(request, 'add_stock.html', {'product': product})


@login_required
@permission_required("Store_App.delete_product")
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')  # Redirect to product list after deletion

    return render(request, 'confirm_delete.html', {'product': product})




@login_required
def low_stock(request):
    """API endpoint for low stock data."""

    # Define the threshold for low stock (e.g., less than 10 items in stock)
    low_stock_threshold = 10

    # Get products that are below the low stock threshold
    low_stock_products = (
        Product.objects.filter(quantity__lte=low_stock_threshold)
        .values('name', 'sku', 'quantity')
        .order_by('name')
    )

    # Prepare data for the chart
    labels = [product['name'] for product in low_stock_products]
    data = [product['quantity'] for product in low_stock_products]

    return JsonResponse({
        "title": "Low Stock Products",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data,  # Stock quantities of low stock products
            }]
        }
    })


@login_required
def payment_summary(request):
    """API for payment methods distribution (Pie Chart)."""
    payments = Payment.objects.values('payment_method').annotate(total=Count('id'))

    methods = [item['payment_method'].capitalize() for item in payments]
    counts = [item['total'] for item in payments]

    return JsonResponse({
        "title": "Payment Methods Distribution",
        "data": {
            "labels": methods,
            "datasets": [{
                "data": counts,
                "backgroundColor": ['#4e73df', '#1cc88a', '#36b9cc'],
                "hoverBackgroundColor": ['#2e59d9', '#17a673', '#2c9faf'],
                "hoverBorderColor": "rgba(234, 236, 244, 1)",
            }],
        }
    })

@login_required
# Sales Performance
def sales_performance(request):
    sales = Sale.objects.annotate(
        month=F("sale_date__month")
    ).values("month").annotate(
        total_sales=Sum("quantity")
    ).order_by("month")

    response_data = {
        "data": {
            "labels": [f"Month {entry['month']}" for entry in sales],
            "datasets": [
                {
                    "label": "Total Sales",
                    "data": [entry["total_sales"] for entry in sales],
                }
            ],
        }
    }
    return JsonResponse(response_data)


# Inventory Logs Chart
@login_required
def inventory_logs(request):
    """
    API endpoint to track inventory changes (added, removed, sold).
    """
    logs = InventoryLog.objects.order_by("-date").values(
        "date", "product__name", "change_type", "quantity"
    )
    return JsonResponse({"inventory_logs": list(logs)})


@login_required
def line_chart(request):
    """API endpoint for daily sales trends."""
    # Aggregate sales data by day
    daily_sales = (
        Sale.objects.annotate(sale_day=TruncDate('sale_date'))
        .values('sale_day')
        .annotate(total_revenue=Sum(F('quantity') * F('product__price')))
        .order_by('sale_day')
    )

    # Prepare data for the chart
    labels = [entry['sale_day'].strftime("%Y-%m-%d") for entry in daily_sales]
    data = [float(entry['total_revenue']) for entry in daily_sales]

    return JsonResponse({
        "title": "Daily Sales Trends",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data  # Revenue values for each day
            }]
        }
    })


@login_required
def bar_chart(request):
    """API endpoint for bar chart data."""
    # Fetch total sales by product
    sales_by_product = Sale.objects.values('product__name').annotate(total_sales=Sum('quantity')).order_by(
        '-total_sales')[:10]

    # Extract data for the chart
    labels = [item['product__name'] for item in sales_by_product]
    data = [item['total_sales'] for item in sales_by_product]

    return JsonResponse({
        "title": "Sales by Product",  # Title for the bar chart
        "data": {
            "labels": labels,  # Labels for the bar chart
            "datasets": [{
                "data": data  # Sales quantities
            }]
        }
    })


@login_required
def pie_chart(request):
    """API endpoint for pie chart data."""
    sales = Sale.objects.all()
    returned = sales.filter(payment_method="mpesa").count()
    cash = sales.filter(payment_method="cash").count()
    card = sales.filter(payment_method="card").count()

    return JsonResponse({
        "title": "Grouped by Payment Method",  # Title for the pie chart
        "data": {
            "labels": ["MPESA", "Cash", "Card"],  # Labels for the pie chart
            "datasets": [{
                "data": [returned, cash, card],  # Data for the pie chart
                "backgroundColor": ["#4e73df", "#1cc88a", "#36b9cc"],  # Colors for the chart sections
                "hoverBackgroundColor": ["#2e59d9", "#17a673", "#2c9faf"]
            }],
        }
    })


def test(request):
    return render(request, 'test.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')




def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Handle full name splitting
            full_name = form.cleaned_data.get('full_name')
            name_parts = full_name.split()
            user.first_name = name_parts[0]  # Always assign the first part
            user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            user.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})



from .forms import LoginForm  # Ensure LoginForm is imported


def login_view(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)  # Log the user in
                return redirect('dashboard')  # Update to the correct URL name
        messages.error(request, "Invalid username or password")
        return render(request, "login.html", {"form": form})
