from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Product, Order, OrderItem
from .services import send_telegram_message
from .forms import CustomerRegistrationForm

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image_url': product.image_url
        }
    
    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart.")
    return redirect('home')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    for pid, item in cart.items():
        price = float(item['price'])
        quantity = item['quantity']
        total = price * quantity
        total_price += total
        cart_items.append({
            'product_id': pid,
            'name': item['name'],
            'price': price,
            'quantity': quantity,
            'total': total,
            'image_url': item.get('image_url')
        })
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if action == 'increase':
            cart[product_id_str]['quantity'] += 1
        elif action == 'decrease':
            cart[product_id_str]['quantity'] -= 1
            if cart[product_id_str]['quantity'] <= 0:
                del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        messages.info(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    if request.method == 'POST':
        total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
        order = Order.objects.create(user=request.user, total_price=total_price)
        
        phone_number = "N/A"
        address = "N/A"
        if hasattr(request.user, 'profile'):
            phone_number = request.user.profile.phone_number
            address = request.user.profile.address

        order_details_msg = f"🛒 <b>New Order #{order.id}</b>\n"
        order_details_msg += f"👤 Customer: {request.user.first_name or request.user.username}\n"
        order_details_msg += f"📞 Phone: {phone_number}\n"
        order_details_msg += f"📍 Address: {address}\n"
        order_details_msg += f"💰 Total: ₹{total_price:.2f}\n\n"
        order_details_msg += "📦 <b>Items:</b>\n"

        for pid, item in cart.items():
            product = get_object_or_404(Product, id=pid)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price'],
                quantity=item['quantity']
            )
            order_details_msg += f"- {item['quantity']}x {item['name']} (₹{item['price']})\n"
        
        # Clear cart
        request.session['cart'] = {}
        
        # Send Telegram notification
        send_telegram_message(order_details_msg)
        
        messages.success(request, "Order placed successfully!")
        return render(request, 'store/checkout_success.html', {'order': order})
        
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    return render(request, 'store/checkout.html', {'cart': cart, 'total_price': total_price})

def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
