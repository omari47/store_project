from itertools import product

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from store_app.forms import SaleForm, ProductForm
from store_app.models import Product, Sale, InventoryLog


# Create your views here.
def dashboard(request):

    return render(request, 'dashboard.html')


def product_list(request):
    items = Product.objects.all()

    return render(request, 'product_list.html', {'products': items})




def log_sale(request):
    products = Product.objects.all()  # Fetch all products to display in the table

    # Process the sale when the form is submitted
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            # item = form.cleaned_data['item']
            product_id = form.cleaned_data['product'].id
            quantity = form.cleaned_data['quantity']
            item = get_object_or_404(Product, pk=product_id)

            if item.quantity >= quantity:  # Ensure enough stock
                # Update item stock quantity
                item.quantity -= quantity
                item.save()


                # Create a Sale record
                sale = Sale(product=Product, quantity=quantity, total_price=Product.price * quantity,
                            # Sale.objects.create(item=item, quantity=quantity, price=sale_price)
                            payment_method=form.cleaned_data['payment_method'])
                sale.save()

                # Log the inventory change
                log = InventoryLog(
                    product=Product,
                    quantity_changed=-quantity,
                    status="Out of Stock" if Product.quantity == 0 else "In Stock",
                    change_reason="sale"
                )
                log.save()

                # Show a success message
                messages.success(request, f'Sale of {quantity} {Product.name} completed successfully.')

                return redirect('product_list')  # Redirect to prevent resubmission on page refresh
            else:
                # Show an error message if not enough stock is available
                messages.error(request, 'Not enough stock available for this sale.')

    else:
        form = SaleForm()  # Initialize empty form

    return render(request, 'log_sale.html', {'products': products, 'form': form})
    # return render(request, 'log_sale.html')




def stock_management(request):
    return render(request, 'stock_management.html')


def product_details(request):
    return render(request, 'product_details.html')


def analytics(request):
    return render(request, 'analytics.html')


def view_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {'product': product})


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


def add_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        quantity_to_add = int(request.POST['quantity'])  # Get the quantity from the form
        product.quantity += quantity_to_add
        product.save()
        return redirect('product_list')  # Redirect to product list after adding stock

    return render(request, 'add_stock.html', {'product': product})


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')  # Redirect to product list after deletion

    return render(request, 'confirm_delete.html', {'product': product})
