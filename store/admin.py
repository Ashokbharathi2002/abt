from django.contrib import admin
from .models import Category, Product, Order, OrderItem, CustomerProfile, PromoCode

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'original_price', 'is_offer', 'stock', 'created_at']
    list_filter = ['is_offer', 'category', 'created_at']
    list_editable = ['price', 'original_price', 'is_offer', 'stock']
    search_fields = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'pincode']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'active']
    list_filter = ['active']
    search_fields = ['code']
