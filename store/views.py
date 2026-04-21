from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Product, Category, Manufacturer, Cart, CartItem


def home(request):
    return HttpResponse("""
        <h1>Магазин аксессуаров для домашних животных</h1>
        <p><a href='/catalog/'>Каталог товаров</a></p>
        <p><a href='/about/'>Об авторе</a></p>
        <p><a href='/shop/'>О магазине</a></p>
    """)


def about(request):
    return HttpResponse("""
        <h1>Об авторе</h1>
        <p>Лабораторную работу выполнил: Асядовский Станислав</p>
        <p>Группа: 88ТП</p>
        <p><a href='/'>← На главную</a></p>
    """)


def shop_info(request):
    return HttpResponse("""
        <h1>О магазине</h1>
        <p>Тема лабораторной работы: Магазин аксессуаров для домашних животных</p>
        <p>В моём магазине вы найдёте:</p>
        <ul>
            <li>Ошейники и поводки для собак</li>
            <li>Когтеточки и игрушки для кошек</li>
            <li>Домики и поилки для грызунов</li>
            <li>Одежду и средства для ухода</li>
        </ul>
        <p><a href='/'>← На главную</a></p>
    """)


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    search_query = request.GET.get('search', '')
    
    if category_id:
        products = products.filter(category_id=category_id)
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'selected_category': int(category_id) if category_id else None,
        'selected_manufacturer': int(manufacturer_id) if manufacturer_id else None,
        'search_query': search_query,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not item_created:
        if cart_item.quantity < product.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Товар "{product.name}" добавлен в корзину')
        else:
            messages.error(request, f'Недостаточно товара на складе. Доступно: {product.stock_quantity}')
    else:
        messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    
    return redirect('product_list')


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0 and new_quantity <= cart_item.product.stock_quantity:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, 'Количество обновлено')
        else:
            messages.error(request, f'Недоступное количество. Доступно: {cart_item.product.stock_quantity}')
    
    return redirect('cart_view')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Товар "{product_name}" удалён из корзины')
    return redirect('cart_view')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = cart.total_price()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'store/cart.html', context)