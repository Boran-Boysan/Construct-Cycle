from django.db import models
from django.conf import settings
from decimal import Decimal


class Cart(models.Model):
    """Kullanıcı Sepeti"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="Kullanıcı"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
        verbose_name = "Sepet"
        verbose_name_plural = "Sepetler"

    def __str__(self):
        return f"{self.user.email} - Sepet"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total(self):
        return self.subtotal

    def clear(self):
        self.items.all().delete()

    def add_product(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': Decimal(str(quantity))}
        )
        if not created:
            cart_item.quantity += Decimal(str(quantity))
            cart_item.save()
        return cart_item

    def remove_product(self, product):
        return self.items.filter(product=product).delete()[0] > 0


class CartItem(models.Model):
    """Sepet Kalemi"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = "Sepet Kalemi"
        verbose_name_plural = "Sepet Kalemleri"
        unique_together = [['cart', 'product']]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def unit_price(self):
        return self.product.sale_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity
