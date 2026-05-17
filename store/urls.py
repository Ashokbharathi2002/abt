from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json'), name='manifest_json'),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='service_worker_js'),
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/buy/<int:product_id>/', views.buy_now, name='buy_now'),
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('offers/', views.offer_zone, name='offer_zone'),
    path('clearance/', views.clearance_zone, name='clearance_zone'),
    path('cart/apply_promo/', views.apply_promo, name='apply_promo'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/return/<int:order_id>/', views.return_order, name='return_order'),
    path('profile/test_notification/', views.test_notification, name='test_notification'),
]
