from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Product, Order, OrderItem, CustomerProfile, PromoCode
from .services import send_telegram_message
from .forms import CustomerRegistrationForm, ProfileUpdateForm

def get_cart_details(request):
    cart = request.session.get('cart', {})
    promo_code_str = request.session.get('promo_code')
    
    promo = None
    if promo_code_str:
        promo = PromoCode.objects.filter(code__iexact=promo_code_str, active=True).first()
        if not promo:
            if 'promo_code' in request.session:
                del request.session['promo_code']
                
    cart_items = []
    subtotal = 0
    total_discount = 0
    
    applicable_product_ids = []
    if promo and promo.applicable_products.exists():
        applicable_product_ids = list(promo.applicable_products.values_list('id', flat=True))
        
    for pid, item in cart.items():
        price = float(item['price'])
        quantity = item['quantity']
        item_total = price * quantity
        subtotal += item_total
        
        discount_for_item = 0
        if promo:
            if not applicable_product_ids or int(pid) in applicable_product_ids:
                discount_for_item = item_total * (promo.discount_percentage / 100.0)
                total_discount += discount_for_item
                
        cart_items.append({
            'product_id': pid,
            'name': item['name'],
            'original_price': price,
            'discounted_price': price - (discount_for_item / quantity) if quantity > 0 else price,
            'quantity': quantity,
            'total': item_total - discount_for_item,
            'image_url': item.get('image_url')
        })
        
    total_price = subtotal - total_discount
    
    return {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_discount': total_discount,
        'total_price': total_price,
        'promo': promo,
        'cart': cart
    }

def home(request):
    cart = request.session.get('cart', {})
    cart_product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.exclude(id__in=cart_product_ids)
    return render(request, 'store/home.html', {'products': products})

def offer_zone(request):
    products = Product.objects.filter(is_offer=True)
    return render(request, 'store/offer_zone.html', {'products': products})

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

def apply_promo(request):
    if request.method == 'POST':
        code = request.POST.get('promo_code', '').strip()
        if not code:
            if 'promo_code' in request.session:
                del request.session['promo_code']
                messages.info(request, "Promo code removed.")
            return redirect('view_cart')
            
        promo = PromoCode.objects.filter(code__iexact=code, active=True).first()
        if promo:
            request.session['promo_code'] = promo.code
            messages.success(request, f"Promo code '{promo.code}' applied successfully!")
        else:
            messages.error(request, "Invalid or inactive promo code.")
    return redirect('view_cart')

def view_cart(request):
    details = get_cart_details(request)
    return render(request, 'store/cart.html', details)

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
    details = get_cart_details(request)
    cart = details['cart']
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    if request.method == 'POST':
        total_price = details['total_price']
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
        order_details_msg += f"💰 Total: ₹{total_price:.2f}\n"
        
        if details['promo']:
            order_details_msg += f"🎟️ Promo Applied: {details['promo'].code} (-₹{details['total_discount']:.2f})\n"
            
        order_details_msg += "\n📦 <b>Items:</b>\n"

        for item in details['cart_items']:
            product = get_object_or_404(Product, id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['discounted_price'],
                quantity=item['quantity']
            )
            order_details_msg += f"- {item['quantity']}x {item['name']} (₹{item['discounted_price']:.2f})\n"
        
        # Clear cart and promo code
        request.session['cart'] = {}
        if 'promo_code' in request.session:
            del request.session['promo_code']
        
        # Send Telegram notification
        send_telegram_message(order_details_msg)
        
        messages.success(request, "Order placed successfully!")
        return render(request, 'store/checkout_success.html', {'order': order})
        
    return render(request, 'store/checkout.html', details)

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

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(user=request.user)
        
    return render(request, 'store/profile.html', {
        'form': form,
        'orders': orders
    })
