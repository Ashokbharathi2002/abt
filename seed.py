import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import Category, Product

def seed():
    if Category.objects.exists():
        print("Database already seeded")
        return
    
    electronics = Category.objects.create(name='Electronics', slug='electronics')
    clothing = Category.objects.create(name='Clothing', slug='clothing')

    Product.objects.create(
        category=electronics,
        name='Smartphone Pro',
        description='The latest and greatest smartphone with an amazing camera and long battery life.',
        price=999.99,
        stock=50,
        image_url='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80'
    )

    Product.objects.create(
        category=electronics,
        name='Wireless Headphones',
        description='Noise-cancelling wireless headphones for an immersive audio experience.',
        price=199.50,
        stock=100,
        image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80'
    )

    Product.objects.create(
        category=clothing,
        name='Cotton T-Shirt',
        description='A comfortable, 100% cotton t-shirt perfect for everyday wear.',
        price=25.00,
        stock=200,
        image_url='https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80'
    )
    
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
