from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Category(models.Model):
    """Модель категории товара"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    """Модель производителя"""
    name = models.CharField(max_length=100, verbose_name="Название")
    country = models.CharField(max_length=100, verbose_name="Страна")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товара"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='products/', verbose_name="Фото товара")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )
    stock_quantity = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Количество на складе"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="Категория"
    )
    manufacturer = models.ForeignKey(
        Manufacturer, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="Производитель"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Cart(models.Model):
    """Модель корзины"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart',
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def total_price(self):
        """Вычисляет общую стоимость всех товаров в корзине"""
        return sum(item.item_price() for item in self.items.all())


class CartItem(models.Model):
    """Модель элемента корзины"""
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Корзина"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"

    def item_price(self):
        """Вычисляет стоимость элемента корзины"""
        return self.product.price * self.quantity

    def clean(self):
        """Валидация: количество не должно превышать остаток на складе"""
        from django.core.exceptions import ValidationError
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(
                f'Недостаточно товара на складе. Доступно: {self.product.stock_quantity}'
            )