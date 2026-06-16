from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.contrib import messages
from django.core.mail import EmailMessage
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product, Category, Manufacturer, Cart, CartItem, Order, OrderItem, Profile
from .forms import CheckoutForm, SignUpForm, ProfileEditForm
from .utils import generate_excel_receipt
from .serializers import CategorySerializer, ManufacturerSerializer, ProductSerializer, CartSerializer, CartItemSerializer, ProfileSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ProfileSerializer


def home(request):
    popular_products = Product.objects.all().order_by('-id')[:6]
    categories = Category.objects.all()
    context = {
        'popular_products': popular_products,
        'categories': categories,
    }
    return render(request, 'store/index.html', context)


def about(request):
    return HttpResponse("""
        <h1>👤 Об авторе</h1>
        <p>Лабораторную работу выполнил: Асядовский Станислав</p>
        <p>Группа: 88ТП</p>
        <p><a href='/'>← На главную</a></p>
    """)


def shop_info(request):
    return HttpResponse("""
        <h1>🛍️ О магазине</h1>
        <p>Тема лабораторной работы: Магазин аксессуаров для домашних животных</p>
        <p>В нашем магазине вы найдёте:</p>
        <ul>
            <li>🐕 Ошейники и поводки для собак</li>
            <li>🐈 Когтеточки и игрушки для кошек</li>
            <li>🐹 Домики и поилки для грызунов</li>
            <li>🦜 Клетки и жердочки для птиц</li>
        </ul>
        <p><a href='/'>← На главную</a></p>
    """)


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    cat_id = request.GET.get('category', '')
    man_id = request.GET.get('manufacturer', '')
    search_query = request.GET.get('search', '')
    
    if cat_id:
        products = products.filter(category_id=int(cat_id))
    if man_id:
        products = products.filter(manufacturer_id=int(man_id))
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'selected_category': int(cat_id) if cat_id else '',
        'selected_manufacturer': int(man_id) if man_id else '',
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
    
    return redirect('cart_view')


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


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = Order.objects.create(
                    user=request.user,
                    address=form.cleaned_data['address'],
                    phone=form.cleaned_data['phone'],
                    email=form.cleaned_data['email'],
                    comment=form.cleaned_data.get('comment', ''),
                    total_price=cart.total_price()
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                excel_file = generate_excel_receipt(order)

                email = EmailMessage(
                    subject=f'Чек заказа №{order.pk} - Магазин аксессуаров для животных',
                    body=f'Здравствуйте, {request.user.username}!\n\n'
                         f'Ваш заказ №{order.pk} успешно оформлен.\n'
                         f'Сумма заказа: {order.total_price} руб.\n'
                         f'Адрес доставки: {order.address}\n\n'
                         f'Чек во вложении.\n\n'
                         f'Спасибо за покупку!',
                    from_email='shop@example.com',
                    to=[order.email],
                )
                email.attach(f'check_order_{order.pk}.xlsx', excel_file.read(),
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                email.send(fail_silently=False)

                cart_items.delete()
                messages.success(request, f'Заказ №{order.pk} оформлен! Чек отправлен на {order.email}')
                return redirect('order_success', order_id=order.pk)

            except Exception as e:
                messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
                return redirect('checkout')
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': cart.total_price(),
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    context = {'order': order}
    return render(request, 'store/order_success.html', context)


# Представления аутентификации

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('product_list')
    else:
        form = SignUpForm()
    return render(request, 'store/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'product_list')
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('product_list')


@login_required
def profile_view(request):
    profile = request.user.profile
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'store/profile.html', context)


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'store/profile_edit.html', {'form': form})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, 'Доступ запрещён')
        return redirect('profile')
    context = {'order': order}
    return render(request, 'store/order_detail.html', context)


# API ViewSets

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.profile.role == 'admin':
            return Cart.objects.all()
        return Cart.objects.filter(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.profile.role == 'admin':
            return CartItem.objects.all()
        return CartItem.objects.filter(cart__user=self.request.user)


# API /api/me/

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    profile = request.user.profile
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    profile = request.user.profile
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)