from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'description')
    search_fields = ('name', 'country')
    list_filter = ('country',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock_quantity', 'category', 'manufacturer')
    list_filter = ('category', 'manufacturer')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    readonly_fields = ('item_price',)

    def item_price(self, obj):
        if obj.pk:
            return obj.item_price()
        return '-'
    item_price.short_description = 'Стоимость'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price_display')
    inlines = [CartItemInline]
    readonly_fields = ('total_price_display',)

    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = 'Общая стоимость'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'item_price_display')
    list_filter = ('cart__user', 'product')

    def item_price_display(self, obj):
        return obj.item_price()
    item_price_display.short_description = 'Стоимость'

from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_total',)

    def item_total(self, obj):
        if obj.pk:
            return obj.item_total()
        return '-'
    item_total.short_description = 'Стоимость'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'email', 'total_price', 'created_at')
    inlines = [OrderItemInline]
    list_filter = ('created_at',)
    search_fields = ('user__username', 'email', 'phone')