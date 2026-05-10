from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Set this higher than price to show a discount.")
    is_offer = models.BooleanField(default=False)
    is_clearance = models.BooleanField(default=False, help_text="Check to display in the Stock Clearance zone.")
    stock = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(help_text="Percentage discount (e.g., 20 for 20%)")
    active = models.BooleanField(default=True)
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='promo_codes', help_text="Select specific products this code applies to. Leave empty to apply to the whole cart.")

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"

class AllowedPincode(models.Model):
    pincode = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True, help_text="Uncheck to temporarily disable deliveries to this pincode.")

    def __str__(self):
        return self.pincode
