from rest_framework import serializers
from .models import Category, Manufacturer, Product, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    manufacturer_name = serializers.ReadOnlyField(source='manufacturer.name')

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'price', 'stock_quantity',
                  'category', 'category_name', 'manufacturer', 'manufacturer_name']


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price',
                  'quantity', 'item_total']

    def get_item_total(self, obj):
        return obj.item_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'username', 'created_at', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()