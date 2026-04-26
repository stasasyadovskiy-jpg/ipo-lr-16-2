from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CategoryViewSet, ManufacturerViewSet, ProductViewSet, CartViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('shop/', views.shop_info, name='shop_info'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('api/', include(router.urls)),
]